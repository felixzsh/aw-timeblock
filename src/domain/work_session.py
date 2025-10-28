from typing import List
from enum import Enum
from datetime import datetime
from .timebox import TimeBox



class WorkState(Enum):
    ACTIVE = 0,
    BREAK = 2



class WorkSession:
    name: str
    workspaces: List[int]
    boxes: List[TimeBox]
    current_box_idx: int
    state: WorkState
    started_at: datetime

    @property
    def total_worked(self) -> float:
        return sum(box.actual_worked for box in self.boxes)

    @property
    def total_breaks(self) -> float:
        return sum(box.actual_breaks for box in self.boxes)

    @property
    def total_extended(self) -> float:
        return sum(box.extended_time for box in self.boxes)


