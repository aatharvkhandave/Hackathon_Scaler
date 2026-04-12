from models import State, Intersection, Event

def init_task_1_easy() -> State:
    # 2 Intersections. Static traffic, no events. Just toggle to clear.
    intersections = {
        "i1": Intersection(id="i1", green_direction="NS", queues={"N": 0, "S": 0, "E": 10, "W": 10}),
        "i2": Intersection(id="i2", green_direction="NS", queues={"N": 0, "S": 0, "E": 15, "W": 5})
    }
    return State(
        max_steps=5, intersections=intersections, events=[],
        initial_total_cars=40, current_total_cars=40, task_name="task_1_easy"
    )

def init_task_2_medium() -> State:
    # 4 Intersections. Rush hour event will inject traffic during the first 2 steps.
    intersections = {
        f"i{j}": Intersection(id=f"i{j}", green_direction="NS", queues={"N": 5, "S": 5, "E": 5, "W": 5})
        for j in range(1, 5)
    }
    return State(
        max_steps=8, intersections=intersections, 
        events=[Event(description="Rush hour: +3 cars to all N queues on steps 1 and 2.", active=True)],
        initial_total_cars=80, current_total_cars=80, task_name="task_2_medium"
    )

def init_task_3_hard() -> State:
    # 9 Intersections. Accident bottleneck.
    intersections = {
        f"i{j}": Intersection(id=f"i{j}", green_direction="NS", queues={"N": 10, "S": 10, "E": 10, "W": 10})
        for j in range(1, 10)
    }
    # i5 has an accident, heavily reducing flow rate
    intersections["i5"].flow_rate = 1 
    return State(
        max_steps=12, intersections=intersections, 
        events=[Event(description="Accident at i5: Flow rate reduced to 1 car/step. Reroute/prioritize others.", active=True)],
        initial_total_cars=360, current_total_cars=360, task_name="task_3_hard"
    )

TASKS = {
    "task_1_easy": init_task_1_easy,
    "task_2_medium": init_task_2_medium,
    "task_3_hard": init_task_3_hard
}

def grade_task(state: State) -> float:
    """
    Grader returns exactly 0.0 to 1.0 based on percentage of cleared traffic.
    Evaluates the literal final state object.
    """
    if state.initial_total_cars == 0:
        return 1.0
    cleared = state.initial_total_cars - state.current_total_cars
    score = cleared / state.initial_total_cars
    return max(0.0, min(1.0, score))
