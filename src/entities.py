from datetime import datetime
from typing import List
from enum import Enum

class TimeBox:
    name: str
    planned_duration: int
    actual_worked: float
    actual_breaks: float
    started_at: datetime
    completed: bool = False


    @property
    def extended_time(self) -> float:
        return max(0, self.actual_worked - self.planned_duration)


class WorkState(Enum):
    ACTIVE = 0,
    EXTEND = 1,
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
