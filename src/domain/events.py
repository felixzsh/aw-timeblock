# domain/events.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class domainevent:
    occurred_at: datetime

@dataclass
class planned_time_started(domainevent):
    box_name: str

# minutes refers to total minutes spent in the current timebox

@dataclass
class planned_time_ended(domainevent):
    box_name: str
    minutes: int

@dataclass
class planned_time_warn(domainevent): # planned time almost finish
    box_name: str
    minutes: int

@dataclass
class extended_time_warn(domainevent): # every n minutes in extended time
    box_name: str
    minutes: int

@dataclass
class break_started(domainevent):
    box_name: str
    workspace_from: int
    workspace_to: int

@dataclass
class break_ended(domainevent):
    box_name: str
    break_duration: float
    workspace: int
