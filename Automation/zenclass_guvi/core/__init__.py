"""
core package initialization for ZenClass & Guvi Automation Suite.
Exposes BrowserManager, StateManager, HitlHandler, and SummaryReporter.
"""

from core.browser import (
    BrowserManager,
    get_browser_manager,
    get_browser_context,
    get_page,
    close_context,
)
from core.state_manager import (
    StateManager,
    TaskRecord,
    TaskStatus,
    TaskPlatform,
    TaskResult,
    AttemptRecord,
)
from core.hitl_handler import (
    HitlHandler,
    HITLHandler,
    GuardrailType,
    GuardrailEvent,
    GuardrailRule,
    GUARDRAIL_RULES,
)
from core.reporter import (
    SummaryReporter,
    Reporter,
)

__all__ = [
    "BrowserManager",
    "get_browser_manager",
    "get_browser_context",
    "get_page",
    "close_context",
    "StateManager",
    "TaskRecord",
    "TaskStatus",
    "TaskPlatform",
    "TaskResult",
    "AttemptRecord",
    "HitlHandler",
    "HITLHandler",
    "GuardrailType",
    "GuardrailEvent",
    "GuardrailRule",
    "GUARDRAIL_RULES",
    "SummaryReporter",
    "Reporter",
]
