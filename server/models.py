from pydantic import BaseModel, Field
from typing import List, Dict, Literal

class Intersection(BaseModel):
    id: str
    green_direction: Literal["NS", "EW"] = "NS"
    queues: Dict[Literal["N", "S", "E", "W"], int]
    flow_rate: int = 5  # Cars that can pass per step when green

class Event(BaseModel):
    description: str
    active: bool

class State(BaseModel):
    step_count: int = 0
    max_steps: int = 10
    intersections: Dict[str, Intersection]
    events: List[Event] = []
    initial_total_cars: int = 0
    current_total_cars: int = 0
    task_name: str = ""

class Observation(BaseModel):
    step_count: int
    intersections_status: Dict[str, dict]
    active_events: List[str]
    total_cars_waiting: int

class Action(BaseModel):
    toggle_intersections: List[str] = Field(
        default_factory=list,
        description="List of intersection IDs to toggle their light phase (e.g., from NS to EW)."
    )

class Reward(BaseModel):
    step_reward: float
    message: str
