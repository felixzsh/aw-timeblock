"""Shared module for aw-nextblock ecosystem.

This module contains common functionality shared between aw-nextblock and 
aw-watcher-nextblock, including state management and data entities.
"""

from .entities import TimeBlock, SessionState, SessionStatus
from .state import (
    session_exists,
    load_session_state,
    save_session_state,
    delete_session_state,
)

__all__ = [
    "TimeBlock",
    "SessionState",
    "SessionStatus",
    "session_exists",
    "load_session_state",
    "save_session_state",
    "delete_session_state",
]
