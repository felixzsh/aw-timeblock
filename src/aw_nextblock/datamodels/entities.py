

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class TimeBlock:
    name: str
    planned_duration: int #REFERENCE ONLY
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

@dataclass
class SessionPlan:
    name: str
    blocks: List[TimeBlock]

@dataclass
class SessionState:
    name: str
    blocks: List[TimeBlock]
    current_block_idx: int
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

