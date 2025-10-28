from datetime import datetime

class TimeBox:
    name: str
    planned_duration: int #REFERENCE ONLY
    actual_worked: float
    actual_breaks: float
    started_at: datetime
    completed: bool = False



    @property
    def extended_time(self) -> float:
        return max(0, self.actual_worked - self.planned_duration)

    @property
    def is_extended(self) -> bool:
        return self.extended_time > 0
