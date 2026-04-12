from typing import Any, Tuple, Dict
from models import State, Action, Observation, Reward
from tasks import TASKS, grade_task

class Environment:
    """
    Traffic AI Simulation Environment.
    Manages the state of urban intersections and simulates traffic flow.
    """
    def __init__(self):
        # Persistent internal state
        self.state: State = None

    def reset(self, task_name: str) -> Observation:
        """
        Resets the simulation to the initial state of a specific task.
        """
        if task_name not in TASKS:
            raise ValueError(f"Unknown task: {task_name}")
        
        # Initialize state from the task registry
        self.state = TASKS[task_name]()
        return self._get_observation()

    def step(self, action: Any) -> Tuple[Observation, float, bool, Dict]:
        """
        Processes one simulation step based on the agent's action.
        """
        if self.state is None:
            raise RuntimeError("Environment must be reset before stepping.")

        # 1. PARSE ACTION
        # Handles both JSON dicts (from API) and objects (from local scripts)
        if isinstance(action, dict):
            toggle_list = action.get("toggle_intersections", [])
        else:
            toggle_list = getattr(action, "toggle_intersections", [])

        step_penalty = 0.0
        
        # 2. APPLY ACTION: Toggle traffic light orientations
        # We only loop once to prevent flipping the light back and forth
        for i_id in toggle_list:
            if i_id in self.state.intersections:
                curr = self.state.intersections[i_id].green_direction
                # Flip: NS -> EW or EW -> NS
                self.state.intersections[i_id].green_direction = "EW" if curr == "NS" else "NS"
            else:
                # Small penalty for invalid intersection IDs
                step_penalty -= 0.01

        # 3. PROCESS TRAFFIC FLOW
        # Cars leave intersections if their direction is currently GREEN
        for i_id, intersection in self.state.intersections.items():
            # Determine which lanes are allowed to move
            dirs_to_flow = ["N", "S"] if intersection.green_direction == "NS" else ["E", "W"]
            for d in dirs_to_flow:
                flow = min(intersection.queues[d], intersection.flow_rate)
                intersection.queues[d] -= flow

        # 4. DYNAMIC EVENTS: Rush Hour Simulation
        # Adds complexity to Medium and Hard tasks by injecting cars mid-simulation
        if self.state.task_name == "task_2_medium" and self.state.step_count < 2:
            for i_id in self.state.intersections:
                self.state.intersections[i_id].queues["N"] += 3

        # 5. UPDATE STATE COUNTERS
        self.state.step_count += 1
        total_cars_now = sum(sum(i.queues.values()) for i in self.state.intersections.values())
        
        # Calculate how many cars were cleared in this specific step
        cars_cleared_this_step = self.state.current_total_cars - total_cars_now
        self.state.current_total_cars = total_cars_now

        # Check for termination: Max steps reached or all cars cleared
        done = self.state.step_count >= self.state.max_steps or total_cars_now == 0
        
        # 6. REWARD CALCULATION
        # Dense reward: percentage of total cars cleared this step
        step_reward = (cars_cleared_this_step / max(1, self.state.initial_total_cars)) + step_penalty
        
        final_score = 0.0
        if done:
            # On the final step, use the official grader logic
            final_score = grade_task(self.state)
            step_reward = final_score

        # 7. PREPARE RETURN VALUES
        obs = self._get_observation()
        info = {"grader_score": final_score} if done else {}

        # Clip reward to strictly follow the 0.0–1.0 range requirement
        clipped_reward = max(0.0, min(1.0, step_reward))

        return obs, clipped_reward, done, info

    def _get_observation(self) -> Observation:
        """
        Generates a structured Observation for the agent.
        """
        intersections_status = {}
        for i_id, inter in self.state.intersections.items():
            intersections_status[i_id] = {
                "green_direction": inter.green_direction,
                "queues": inter.queues
            }
            
        # Returns a structured Observation model
        return Observation(
            step_count=self.state.step_count,
            intersections_status=intersections_status,
            active_events=[e.description for e in self.state.events if e.active],
            total_cars_waiting=self.state.current_total_cars
        )

    def get_state(self) -> State:
        """
        Returns the full internal state for debugging or inspection.
        """
        return self.state
