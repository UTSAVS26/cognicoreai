"""Policy hooks for V2 runtime safety and capability control."""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set


@dataclass
class PolicyDecision:
    """Result of a policy check over an action request."""

    allowed: bool
    reason: str = "allowed"
    severity: str = "S3"


class BasePolicy(abc.ABC):
    """Abstract policy interface for runtime action validation."""

    @abc.abstractmethod
    def evaluate(
        self, action: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> PolicyDecision:
        raise NotImplementedError


class AllowAllPolicy(BasePolicy):
    """Default policy that allows all actions."""

    def evaluate(
        self, action: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> PolicyDecision:
        return PolicyDecision(allowed=True)


class DenyByCapabilityPolicy(BasePolicy):
    """Policy that blocks specific capability/tool names."""

    def __init__(self, blocked_capabilities: Set[str]):
        self._blocked_capabilities = blocked_capabilities

    def evaluate(
        self, action: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> PolicyDecision:
        capability = action.get("capability") or action.get("tool_name")
        if capability in self._blocked_capabilities:
            return PolicyDecision(
                allowed=False,
                reason=f"Capability '{capability}' is blocked by policy.",
                severity="S2",
            )
        return PolicyDecision(allowed=True)
