"""
Memory module for CogniCore agents.

This module provides the foundational components for managing an agent's memory.
The core design principle is to use an abstract base class (`BaseMemory`) to
define a consistent interface for all memory backends. This allows for
flexibility, enabling developers to use simple in-memory storage for testing
or to implement complex, persistent memory solutions (e.g., using databases
or file systems) for production use cases.

The standard message format used throughout the library is also defined here
as the `Message` type.
"""

import abc
from typing import Any, Dict, List, Literal, TypedDict


# Define a consistent, typed structure for all messages stored in memory.
# Using a TypedDict provides clarity and enables static analysis tools to
# catch potential bugs related to message format.
class Message(TypedDict, total=False):
    """
    Represents a single message in the conversation history.

    Attributes:

        role (Literal["system", "user", "assistant", "tool"]): The role of the entity
            that produced the message. "system" messages set the agent's
            behavior, "user" messages are from the end-user, and "assistant"
            messages are from the AI.

        content (str): The text content of the message.
    """

    role: Literal["system", "user", "assistant", "tool"]
    content: str
    name: str
    tool_call_id: str
    tool_calls: List[Dict[str, Any]]
    event: Dict[str, Any]


class BaseMemory(abc.ABC):
    """
    Abstract Base Class for all memory modules in CogniCore.

    This class defines the essential interface that any memory implementation
    must adhere to. By programming against this abstraction, the `Agent` class
    can seamlessly switch between different memory backends without changing
    its internal logic.
    """

    @abc.abstractmethod
    def add_message(self, message: Message) -> None:
        """
        Adds a single message to the memory store.

        This method is responsible for appending a new message to the
        conversation history.

        Args:
            message (Message): The message object to add to the history.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_history(self) -> List[Message]:
        """
        Retrieves the complete conversation history.

        Returns:
            List[Message]: A list of all message objects stored in memory,
                           in the order they were added.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def clear(self) -> None:
        """
        Clears the entire conversation history from memory.
        """
        raise NotImplementedError


class VolatileMemory(BaseMemory):
    """
    A simple, in-memory implementation of the BaseMemory.

    This memory backend stores the conversation history in a Python list.
    It is "volatile" because the history is lost as soon as the object is
    destroyed or the application exits.

    This class is ideal for development, testing, and simple applications
    where conversation persistence is not required.
    """

    def __init__(self) -> None:
        """Initializes the VolatileMemory with an empty history list."""
        self._history: List[Message] = []

    def add_message(self, message: Message) -> None:
        """
        Adds a single message to the in-memory history list.

        Args:
            message (Message): The message object to add.
        """
        self._history.append(message)

    def get_history(self) -> List[Message]:
        """
        Retrieves the complete conversation history.

        Returns:
            List[Message]: A copy of the internal history list to prevent
                           external modification of the memory state.
        """
        return self._history.copy()

    def clear(self) -> None:
        """
        Clears the history list, effectively resetting the agent's memory.
        """
        self._history.clear()

    def __repr__(self) -> str:
        """Provides a developer-friendly representation of the memory object."""
        return f"<VolatileMemory history_length={len(self._history)}>"
