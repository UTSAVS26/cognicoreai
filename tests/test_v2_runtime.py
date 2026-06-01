"""V2 runtime tests to validate additive multi-agent behavior and policy hooks."""

import unittest
from unittest.mock import MagicMock

from cognicoreai import (
    Agent,
    BaseLLM,
    DenyByCapabilityPolicy,
    LLMResponse,
    ToolCall,
    V2Config,
    VolatileMemory,
)
from cognicoreai.tools import CalculatorTool


class TestV2Runtime(unittest.TestCase):
    def setUp(self):
        self.mock_llm = MagicMock(spec=BaseLLM)

    def test_planner_mode_runs_multi_role_loop(self):
        responses = [
            LLMResponse(
                content="Plan: compute then verify.",
                tool_calls=None,
                raw_response_message={
                    "role": "assistant",
                    "content": "Plan: compute then verify.",
                },
            ),
            LLMResponse(
                content="Execution says answer is 9.",
                tool_calls=None,
                raw_response_message={
                    "role": "assistant",
                    "content": "Execution says answer is 9.",
                },
            ),
            LLMResponse(
                content="Final answer: 9.",
                tool_calls=None,
                raw_response_message={
                    "role": "assistant",
                    "content": "Final answer: 9.",
                },
            ),
        ]
        self.mock_llm.get_completion.side_effect = responses

        agent = Agent(
            llm=self.mock_llm,
            memory=VolatileMemory(),
            tools=[CalculatorTool()],
            mode="planner",
            v2_config=V2Config(mode="planner"),
        )

        result = agent.chat("What is 3 * 3?")
        self.assertEqual(result, "Final answer: 9.")
        self.assertEqual(self.mock_llm.get_completion.call_count, 3)
        self.assertGreater(len(agent.events), 0)

    def test_policy_blocks_tool_call(self):
        first = LLMResponse(
            content=None,
            tool_calls=[
                ToolCall(
                    id="call_block",
                    function_name="calculator",
                    arguments='{"tool_input": "2 + 2"}',
                )
            ],
            raw_response_message={
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_block",
                        "function": {
                            "name": "calculator",
                            "arguments": '{"tool_input": "2 + 2"}',
                        },
                    }
                ],
            },
        )
        second = LLMResponse(
            content="I could not use calculator due to policy.",
            tool_calls=None,
            raw_response_message={
                "role": "assistant",
                "content": "I could not use calculator due to policy.",
            },
        )
        self.mock_llm.get_completion.side_effect = [first, second]

        agent = Agent(
            llm=self.mock_llm,
            memory=VolatileMemory(),
            tools=[CalculatorTool()],
            mode="supervisor",
            v2_config=V2Config(mode="supervisor"),
            policy=DenyByCapabilityPolicy(blocked_capabilities={"calculator"}),
        )

        result = agent.chat("What is 2 + 2?")
        self.assertIn("policy", result.lower())

        message_types = [event.envelope.message_type for event in agent.events]
        self.assertIn("policy.blocked", message_types)


if __name__ == "__main__":
    unittest.main()
