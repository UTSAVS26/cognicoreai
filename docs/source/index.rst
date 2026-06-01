.. CogniCoreAI documentation master file, created by
   sphinx-quickstart on Fri Jul 18 14:11:42 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

####################################################################
CogniCoreAI: Build, Test, and Deploy Robust Conversational AI
####################################################################

**CogniCoreAI** is a modular Python framework for building sophisticated conversational AI agents. It is designed from the ground up to be extensible, testable, and easy to use.

Whether you're building a simple chatbot or a complex, tool-using agent, CogniCoreAI provides the foundational blocks you need, with a unique focus on **behavioral simulation** to ensure your agents are reliable and perform as expected.

.. figure:: /_static/cognicoreai_logo.png
   :alt: CogniCoreAI Logo
   :align: center
   :width: 200px


Key Features
============

*   **Modular & Extensible**: Swap out components like LLMs, memory, and tools with ease thanks to a clean, abstraction-based design.
*   **Powerful Tool Integration**: Equip your agents with tools to interact with APIs, databases, or any other external service.
*   **Built-in Simulation Framework**: Go beyond unit tests. Write behavioral scenarios to validate your agent's reasoning and decision-making process.
*   **LLM Agnostic**: Ships with an OpenAI client but is designed to work with any Large Language Model.
*   **Modern & Tested**: Built with modern Python practices and a comprehensive test suite.


Quick Start
===========

Get up and running in minutes. First, install the library:

.. code-block:: bash

   uv pip install cognicoreai

Now, create and chat with your first agent. Make sure your ``OPENAI_API_KEY`` environment variable is set.

.. code-block:: python
   :linenos:

   from cognicoreai import Agent, OpenAI_LLM, VolatileMemory, CalculatorTool

   # 1. Assemble the agent's components
   llm = OpenAI_LLM()
   memory = VolatileMemory()
   tools = [CalculatorTool()]

   # 2. Create the agent
   agent = Agent(llm, memory, tools)

   # 3. Start chatting!
   response = agent.chat("What is 125 divided by 5?")
   print(response)


Table of Contents
=================

Explore the documentation to learn more about how to use and extend CogniCoreAI.

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   getting_started
   v2_alpha
   user_guide/index
   how_to/index
   api_reference