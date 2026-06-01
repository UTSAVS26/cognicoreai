V2 Alpha Guide
==============

CogniCoreAI V2 starts as an alpha track focused on additive runtime architecture.
The primary objective is to introduce multi-agent foundations without breaking
existing V1 usage.

Version
-------

Current alpha version: ``2.0.0a1``

Compatibility Model
-------------------

- V1 behavior remains default.
- V2 behavior is opt-in by passing a runtime mode to ``Agent``.

V2 Runtime Modes
----------------

V2 introduces three orchestration modes:

- ``supervisor``: single coordinator role with optional tool calls.
- ``planner``: planner -> executor -> critic sequence.
- ``blackboard``: collaborative iterative roles (researcher, analyst, synthesizer).

Quick Example
-------------

.. code-block:: python

   from cognicoreai import Agent, OpenAI_LLM, VolatileMemory, CalculatorTool

   agent = Agent(
       llm=OpenAI_LLM(),
       memory=VolatileMemory(),
       tools=[CalculatorTool()],
       mode="planner",  # opt-in V2 mode
   )

   print(agent.chat("What is 12 * 7?"))

V2 Components Added
-------------------

- ``protocol.py``: runtime event and lifecycle envelopes.
- ``policy.py``: policy interfaces and decisions.
- ``tool_runtime.py``: policy-aware tool execution outcomes.
- ``orchestrator.py``: V2 multi-agent runtime implementation.

Testing Expectations
--------------------

- Keep V1 tests green as compatibility baseline.
- Run V2 tests for mode behavior and policy/tool interactions.

Recommended commands:

.. code-block:: bash

   # from repository root
   set PYTHONPATH=src
   pytest -q

Documentation Build
-------------------

Windows:

.. code-block:: bat

   cd docs
   make.bat html

Unix/Linux:

.. code-block:: bash

   make -C docs html
