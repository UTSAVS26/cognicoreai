"""V2 orchestration runtime with multi-agent execution modes."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional

from .llms import BaseLLM
from .memory import BaseMemory
from .policy import AllowAllPolicy, BasePolicy
from .protocol import EventEnvelope, RuntimeEvent, new_correlation_id
from .tool_runtime import ToolRuntime
from .tools import Tool

V2Mode = Literal["supervisor", "planner", "blackboard"]


@dataclass
class V2Config:
    """Config knobs for the V2 multi-agent runtime."""

    mode: V2Mode = "supervisor"
    max_rounds: int = 1
    emit_events: bool = True
    tool_retry_budget: int = 0


class V2MultiAgentRuntime:
    """An additive V2 runtime that keeps V1 compatibility via opt-in usage."""

    def __init__(
        self,
        llm: BaseLLM,
        memory: BaseMemory,
        tools: List[Tool],
        system_prompt: str,
        config: V2Config,
        policy: Optional[BasePolicy] = None,
    ):
        self.llm = llm
        self.memory = memory
        self.tools = tools
        self.system_prompt = system_prompt
        self.config = config
        self.policy = policy or AllowAllPolicy()
        self.tool_runtime = ToolRuntime(tools, self.policy)
        self._events: List[RuntimeEvent] = []

    @property
    def events(self) -> List[RuntimeEvent]:
        return self._events.copy()

    def _emit(self, message_type: str, correlation_id: str, payload: Dict[str, Any], causation_id: Optional[str] = None) -> str:
        env = EventEnvelope(
            message_type=message_type,  # type: ignore[arg-type]
            source="v2.runtime",
            destination="v2.runtime",
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
        if self.config.emit_events:
            self._events.append(RuntimeEvent(envelope=env, payload=payload))
        return env.message_id

    def _tool_definitions(self) -> List[dict]:
        if not self.tools:
            return []
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tool_input": {
                                "type": "string",
                                "description": "The input to be passed to the tool.",
                            }
                        },
                        "required": ["tool_input"],
                    },
                },
            }
            for tool in self.tools
        ]

    def _execute_role(self, role_name: str, role_prompt: str, correlation_id: str, input_text: Optional[str] = None) -> str:
        assign_id = self._emit("task.assigned", correlation_id, {"role": role_name})
        start_id = self._emit("task.started", correlation_id, {"role": role_name}, causation_id=assign_id)

        if input_text:
            self.memory.add_message({"role": "user", "content": input_text})

        self.memory.add_message(
            {
                "role": "system",
                "content": f"Role: {role_name}. {role_prompt}",
            }
        )

        response = self.llm.get_completion(self.memory.get_history(), self._tool_definitions())
        self.memory.add_message(response.raw_response_message)

        if response.tool_calls:
            for tc in response.tool_calls:
                tool_input = json.loads(tc.arguments).get("tool_input", "")
                tool_event_id = self._emit(
                    "tool.call.requested",
                    correlation_id,
                    {"role": role_name, "tool": tc.function_name},
                    causation_id=start_id,
                )
                tool_result = self.tool_runtime.execute(
                    tool_name=tc.function_name,
                    tool_input=tool_input,
                    retry_budget=self.config.tool_retry_budget,
                )
                if tool_result.status == "completed":
                    self._emit(
                        "tool.call.completed",
                        correlation_id,
                        {"role": role_name, "tool": tc.function_name},
                        causation_id=tool_event_id,
                    )
                elif tool_result.status == "blocked":
                    self._emit(
                        "policy.blocked",
                        correlation_id,
                        {"role": role_name, "tool": tc.function_name, "reason": tool_result.content},
                        causation_id=tool_event_id,
                    )
                else:
                    self._emit(
                        "tool.call.failed",
                        correlation_id,
                        {"role": role_name, "tool": tc.function_name, "error": tool_result.error_type},
                        causation_id=tool_event_id,
                    )

                self.memory.add_message(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": tc.function_name,
                        "content": tool_result.content,
                    }
                )

            final_response = self.llm.get_completion(
                self.memory.get_history(), self._tool_definitions()
            )
            self.memory.add_message(final_response.raw_response_message)
            out = final_response.content or ""
        else:
            out = response.content or ""

        self._emit("task.completed", correlation_id, {"role": role_name, "output": out}, causation_id=start_id)
        return out

    def chat(self, user_input: str) -> str:
        correlation_id = new_correlation_id()
        self._emit("task.created", correlation_id, {"mode": self.config.mode})

        if self.config.mode == "supervisor":
            return self._execute_role(
                "supervisor",
                "Decompose the problem and produce a final answer. Use tools if needed.",
                correlation_id,
                input_text=user_input,
            )

        if self.config.mode == "planner":
            self._execute_role(
                "planner",
                "Create a concise action plan for the user request.",
                correlation_id,
                input_text=user_input,
            )
            self._execute_role(
                "executor",
                "Execute the current plan and compute the solution with available tools.",
                correlation_id,
            )
            return self._execute_role(
                "critic",
                "Review the executor output and provide the best final response.",
                correlation_id,
            )

        blackboard_output = ""
        self.memory.add_message({"role": "user", "content": user_input})
        for _ in range(max(1, self.config.max_rounds)):
            self._execute_role(
                "researcher",
                "Contribute facts and intermediate findings to the blackboard.",
                correlation_id,
            )
            self._execute_role(
                "analyst",
                "Synthesize findings and refine the blackboard state.",
                correlation_id,
            )
            blackboard_output = self._execute_role(
                "synthesizer",
                "Produce the best consolidated answer from the blackboard.",
                correlation_id,
            )

        return blackboard_output
