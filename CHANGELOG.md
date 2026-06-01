# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0a1] - 2026-06-01

This is the first V2 alpha release track with additive multi-agent foundations,
while preserving V1 behavior as the default mode.

### Added
- V2 protocol primitives for lifecycle/event envelopes in `protocol.py`.
- V2 policy hooks in `policy.py` with default allow and capability-block policy.
- V2 tool runtime adapter in `tool_runtime.py` with policy-aware execution outcomes.
- V2 multi-agent runtime in `orchestrator.py` with `supervisor`, `planner`, and `blackboard` modes.
- Opt-in V2 mode support in `Agent` with V1 compatibility kept as default behavior.
- V2 integration tests in `tests/test_v2_runtime.py`.

### Changed
- Package version moved to `2.0.0a1` for alpha release track.
- Memory message typing expanded to include tool metadata used by runtime execution.
- Public exports updated with additive V2 runtime/policy/protocol/tool-runtime symbols.

### Compatibility
- V1 usage remains default by constructing `Agent(..., mode="v1")` implicitly.
- V2 can be enabled explicitly via `Agent(..., mode="supervisor" | "planner" | "blackboard")`.

## [1.0.0] - 2025-07-18

This is the initial public release of CogniCoreAI.

### Added
- Core `Agent` class for orchestrating conversations.
- `BaseLLM` abstraction layer with an `OpenAI_LLM` implementation.
- `BaseMemory` abstraction with a `VolatileMemory` implementation.
- `Tool` abstraction and a built-in `CalculatorTool`.
- `Simulator` framework for running behavioral tests on agents.
- `Scenario` and `Assertion` classes (`ToolUsedAssertion`, `ResponseContainsAssertion`) for defining test cases.
- Comprehensive test suite for all modules.
- Full documentation site built with Sphinx and the Furo theme.
- Ruff and Pytest configured for code quality and testing.
- Project structure configured with `pyproject.toml` for modern packaging.

## [1.0.1] - 2025-07-18
### Fixed
- Corrected README rendering and badge URLs on PyPI.