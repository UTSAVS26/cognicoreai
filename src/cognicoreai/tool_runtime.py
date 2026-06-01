"""Tool execution runtime for V2, including policy checks and typed outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

from .policy import BasePolicy
from .tools import Tool

ToolStatus = Literal["completed", "failed", "blocked"]


@dataclass
class ToolExecutionResult:
    """Normalized outcome of a tool execution attempt."""

    status: ToolStatus
    content: str
    tool_name: str
    error_type: Optional[str] = None


class ToolRuntime:
    """Policy-aware and retry-capable tool execution adapter."""

    def __init__(self, tools: List[Tool], policy: BasePolicy):
        self._tools: Dict[str, Tool] = {tool.name: tool for tool in tools}
        self._policy = policy

    def execute(
        self, tool_name: str, tool_input: str, retry_budget: int = 0
    ) -> ToolExecutionResult:
        decision = self._policy.evaluate(
            {"type": "tool_call", "tool_name": tool_name, "capability": tool_name}
        )
        if not decision.allowed:
            return ToolExecutionResult(
                status="blocked",
                content=decision.reason,
                tool_name=tool_name,
                error_type="policy",
            )

        if tool_name not in self._tools:
            return ToolExecutionResult(
                status="failed",
                content=f"Error: Tool '{tool_name}' not found.",
                tool_name=tool_name,
                error_type="validation",
            )

        tool = self._tools[tool_name]
        attempts = 0
        while True:
            try:
                return ToolExecutionResult(
                    status="completed",
                    content=tool.run(tool_input),
                    tool_name=tool_name,
                )
            except Exception as exc:  # pragma: no cover - defensive path
                attempts += 1
                if attempts > retry_budget:
                    return ToolExecutionResult(
                        status="failed",
                        content=f"Tool execution failed: {exc}",
                        tool_name=tool_name,
                        error_type="internal",
                    )
