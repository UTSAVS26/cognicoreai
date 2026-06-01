"""Protocol and lifecycle primitives for V2 runtime execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

LifecycleState = Literal[
    "created",
    "assigned",
    "running",
    "waiting",
    "retrying",
    "completed",
    "failed",
    "cancelled",
]

MessageType = Literal[
    "task.created",
    "task.assigned",
    "task.started",
    "task.progress",
    "task.completed",
    "task.failed",
    "task.cancelled",
    "tool.call.requested",
    "tool.call.completed",
    "tool.call.failed",
    "policy.blocked",
]


@dataclass
class ErrorEnvelope:
    """Standardized failure payload used by V2 runtime events."""

    error_type: Literal["validation", "dependency", "timeout", "policy", "internal"]
    severity: Literal["S1", "S2", "S3"]
    retriable: bool
    remediation_hint: str


@dataclass
class EventEnvelope:
    """Event wrapper carrying causality metadata across runtime operations."""

    message_type: MessageType
    source: str
    destination: str
    correlation_id: str
    protocol_version: str = "2.0.0-alpha"
    causation_id: Optional[str] = None
    message_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class RuntimeEvent:
    """A full runtime event consisting of envelope + payload + optional error."""

    envelope: EventEnvelope
    payload: Dict[str, Any]
    error: Optional[ErrorEnvelope] = None


_ALLOWED_TRANSITIONS: Dict[LifecycleState, List[LifecycleState]] = {
    "created": ["assigned", "cancelled"],
    "assigned": ["running", "cancelled"],
    "running": ["waiting", "retrying", "completed", "failed", "cancelled"],
    "waiting": ["running", "retrying", "failed", "cancelled"],
    "retrying": ["running", "failed", "cancelled"],
    "completed": [],
    "failed": [],
    "cancelled": [],
}


def validate_transition(current: LifecycleState, nxt: LifecycleState) -> bool:
    """Validate whether a lifecycle transition is allowed by the V2 state model."""
    return nxt in _ALLOWED_TRANSITIONS[current]


def new_correlation_id() -> str:
    """Create a correlation id for a runtime execution thread."""
    return str(uuid4())
