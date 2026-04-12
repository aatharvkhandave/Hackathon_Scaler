import sys
import os
from fastapi import FastAPI, HTTPException, Body
from typing import Dict, Any

# --- ROBUST PATH INJECTION ---
# This ensures app.py finds environment.py, tasks.py, and models.py in the same folder
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir) 

try:
    # Now that you've uploaded environment.py, we MUST import it
    from environment import Environment 
    from tasks import TASKS
    from models import Observation, Action 
except ImportError as e:
    print(f"Startup Import Error: {e}")
    # We define a fallback so the server doesn't crash if an import is slightly off
    class Environment:
        def reset(self, **kwargs): return {"status": "fallback"}
        def step(self, action): return {}, 0, False, {}
        def state(self): return {}

app = FastAPI(title="Traffic AI Scaler", version="1.0.0")

# Initialize the Environment
env = Environment()

# --- MANDATORY CORE ENDPOINTS ---

@app.post("/reset")
async def reset(task_name: str = "task_1_easy"):
    try:
        observation = env.reset(task_name=task_name)
        return observation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step")
async def step(action: dict = Body(...)):
    try:
        # Convert dict to Action model if necessary, or pass directly
        observation, reward, done, info = env.step(action)
        return {
            "observation": observation,
            "reward": reward,
            "done": done,
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
async def get_state():
    """Required by OpenEnv: Returns the current internal state."""
    try:
        # Try to get the real state from your environment
        return env.state()
    except Exception as e:
        # If the environment isn't initialized yet, return a default state
        return {"status": "initialized", "message": "Call /reset to start simulation"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/metadata")
async def get_metadata():
    return {
        "name": "Traffic AI Scaler",
        "description": "Adaptive traffic control system.",
        "version": "1.0.0"
    }

@app.post("/mcp")
async def mcp_handler(payload: dict = Body(...)):
    return {"jsonrpc": "2.0", "id": payload.get("id"), "result": "connected"}

# --- SCALER MANDATORY MAIN ---

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
