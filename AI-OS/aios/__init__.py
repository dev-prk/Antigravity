"""
AI-OS - Autonomous Intelligence Operating System
Layer A: Governance, Policy Engine, and Antigravity-native runtime.
"""

__version__ = "1.0.0"

from aios.policy import (
    Decision,
    Action,
    PolicyDecision,
    CommandResult,
    PolicyViolationError,
    PolicyEngine,
)

__all__ = [
    "Decision",
    "Action",
    "PolicyDecision",
    "CommandResult",
    "PolicyViolationError",
    "PolicyEngine",
]
