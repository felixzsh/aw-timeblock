from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum


class SessionStatus(Enum):
    """Session status enumeration."""
    INACTIVE = "inactive"
    ACTIVE = "active"


@dataclass
class TimeBlock:
    name: str
    planned_duration: int  # REFERENCE ONLY
    start_dt: Optional[datetime] = None
    end_dt: Optional[datetime] = None


@dataclass
class SessionPlan:
    name: str
    blocks: List[TimeBlock]


@dataclass
class SessionState:
    name: str
    blocks: List[TimeBlock]
    current_block_idx: int
    status: SessionStatus = SessionStatus.INACTIVE
    start_dt: Optional[datetime] = None
    end_dt: Optional[datetime] = None

    @property
    def current_block(self) -> Optional[TimeBlock]:
        if self.current_block_idx < len(self.blocks):
            return self.blocks[self.current_block_idx]
        return None

    @property
    def is_active(self) -> bool:
        """Check if the session is currently active."""
        return self.status == SessionStatus.ACTIVE

    @property
    def elapsed_time(self) -> float:
        if self.start_dt:
            return (datetime.now() - self.start_dt).total_seconds()
        return 0.0