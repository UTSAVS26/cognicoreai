"""
The core agent module of the CogniCore framework.

This module has been refactored to be LLM-agnostic. The `Agent` class now
operates on the `BaseLLM` abstraction, allowing any compatible LLM backend
to be plugged in without changing the agent's reasoning logic.
"""

import json
from typing import List, Optional

# Import the new LLM abstraction and the established components
from cognicoreai.llms import BaseLLM
from cognicoreai.memory import BaseMemory
from cognicoreai.orchestrator import V2Config, V2MultiAgentRuntime
from cognicoreai.policy import AllowAllPolicy, BasePolicy
from cognicoreai.tools import Tool


class ToolHandler:
    """
    A helper class to manage the tools available to an agent.
    (This class remains unchanged as its logic is independent of the LLM)
    """

    def __init__(self, tools: List[Tool]):
        self._tools = {tool.name: tool for tool in tools}

    def get_tool_definitions(self) -> List[dict]:
        if not self._tools:
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
            for tool in self._tools.values()
        ]

    def execute_tool(self, tool_name: str, tool_input: str) -> str:
        if tool_name not in self._tools:
            return f"Error: Tool '{tool_name}' not found."

        tool = self._tools[tool_name]
        return tool.run(tool_input)


class Agent:
    """
    The central conversational agent, now decoupled from any specific LLM.
    """

    def __init__(
        self,
        llm: BaseLLM,
        memory: BaseMemory,
        tools: List[Tool],
        system_prompt: str = "You are a helpful assistant.",
        mode: str = "v1",
        v2_config: Optional[V2Config] = None,
        policy: Optional[BasePolicy] = None,
    ):
        """
        Initializes the Agent with LLM-agnostic components.

        Args:
            llm (BaseLLM): An instance of a class that implements the BaseLLM
                           interface (e.g., OpenAI_LLM).
            memory (BaseMemory): An instance of a memory backend.
            tools (List[Tool]): A list of tools the agent is equipped with.
            system_prompt (str): The initial instruction that defines the agent's
                                 persona and behavior.
        """
        self.llm = llm
        self.memory = memory
        self.system_prompt = system_prompt
        self.mode = mode
        self.tool_handler = ToolHandler(tools)
        self._v2_runtime: Optional[V2MultiAgentRuntime] = None

        # Clear memory and set the initial system prompt
        self.memory.clear()
        self.memory.add_message({"role": "system", "content": self.system_prompt})

        if self.mode != "v1":
            config = v2_config or V2Config(mode=self.mode)  # type: ignore[arg-type]
            self._v2_runtime = V2MultiAgentRuntime(
                llm=llm,
                memory=memory,
                tools=tools,
                system_prompt=system_prompt,
                config=config,
                policy=policy or AllowAllPolicy(),
            )

    @property
    def events(self):
        """Returns V2 runtime events when running in V2 mode."""
        if not self._v2_runtime:
            return []
        return self._v2_runtime.events

    def chat(self, user_input: str) -> str:
        """
        The main method for interacting with the agent. The logic now uses the
        standardized LLMResponse object.
        """
        if self._v2_runtime:
            return self._v2_runtime.chat(user_input)

        self.memory.add_message({"role": "user", "content": user_input})

        messages = self.memory.get_history()
        tool_definitions = self.tool_handler.get_tool_definitions()

        # 1. Get the initial response from the LLM via the abstraction
        response = self.llm.get_completion(messages, tool_definitions)

        # 2. Add the raw model response to memory
        # (This is important for maintaining conversational context)
        self.memory.add_message(response.raw_response_message)

        # 3. Check if the LLM decided to call a tool
        if response.tool_calls:
            # 4. Execute all requested tool calls
            for tool_call in response.tool_calls:
                tool_output = self.tool_handler.execute_tool(
                    tool_name=tool_call.function_name,
                    tool_input=json.loads(tool_call.arguments).get("tool_input"),
                )

                # 5. Add the tool's output back to memory
                self.memory.add_message(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function_name,
                        "content": tool_output,
                    }
                )

            # 6. Call the LLM *again* with the tool results in memory
            final_response = self.llm.get_completion(
                self.memory.get_history(), tool_definitions
            )
            # 7. Add the final response to memory and return its content
            self.memory.add_message(final_response.raw_response_message)
            return final_response.content

        # If no tool calls, the first response is the final one.
        return response.content
