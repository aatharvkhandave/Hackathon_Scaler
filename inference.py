import os
import json
import sys
import httpx
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile") 
API_KEY = os.getenv("OPENAI_API_KEY") 

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
ENV_URL = "http://localhost:7860" 

def check_server():
    try:
        response = httpx.get(f"{ENV_URL}/health", timeout=5.0)
    except Exception:
        sys.exit(1)

# FIX 1: Robust ID Cleaning
def clean_action_ids(ids):
    cleaned = []
    for item in ids:
        digits = "".join(filter(str.isdigit, str(item)))
        if digits:
            cleaned.append(f"i{digits}")
    return list(set(cleaned))

def run_task(task_name: str):
    print(f"[START] task={task_name} env=traffic_ai model={MODEL_NAME}", flush=True) 
    
    step_res = {}
    rewards = []
    done = False
    step_num = 1
    
    try:
        res = httpx.post(f"{ENV_URL}/reset?task_name={task_name}").json()
        obs = res 
    except Exception:
        return

    tools = [{
        "type": "function",
        "function": {
            "name": "take_action",
            "description": "Toggle traffic lights at specific intersections.",
            "parameters": {
                "type": "object",
                "properties": {
                    "toggle_intersections": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["toggle_intersections"]
            }
        }
    }]

    # FIX 2: Better Strategy Prompt
    system_prompt = (
        "You are a traffic AI. Goal: Minimize waiting cars.\n"
        "STRATEGY: Compare waiting cars at RED lights vs flowing cars at GREEN lights.\n"
        "Only toggle an intersection if the RED lane is much more crowded than the GREEN lane.\n"
        "If traffic is moving well, send an empty list []."
    )
    
    messages = [{"role": "system", "content": system_prompt}]

    while not done and step_num <= 10:
        messages.append({"role": "user", "content": f"Observation: {json.dumps(obs)}"})
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "take_action"}},
                temperature=0.0 # Keep it deterministic
            )
            
            message = response.choices[0].message
            if not message.tool_calls: break
            
            tool_call = message.tool_calls[0]
            
            try:
                # FIX 3: Handle Markdown backticks in arguments
                args_raw = tool_call.function.arguments
                if "```" in args_raw:
                    args_raw = re.sub(r"```json|```", "", args_raw).strip()
                
                action_args = json.loads(args_raw)
                
                # Apply ID cleaning
                if "toggle_intersections" in action_args:
                    action_args["toggle_intersections"] = clean_action_ids(action_args["toggle_intersections"])
                else:
                    action_args = {"toggle_intersections": []}
            except Exception:
                action_args = {"toggle_intersections": []}
            
            step_response = httpx.post(f"{ENV_URL}/step", json=action_args)
            step_res = step_response.json()
            
            obs = step_res.get("observation")
            reward = step_res.get("reward", 0.0)
            done = step_res.get("done", False)
            rewards.append(reward)
            
            done_str = str(done).lower()
            action_str = json.dumps(action_args)
            print(f"[STEP] step={step_num} action={action_str} reward={reward:.2f} done={done_str} error=null", flush=True)
            
            messages.append(message)
            messages.append({
                "role": "tool", 
                "tool_call_id": tool_call.id, 
                "name": "take_action", 
                "content": json.dumps({"reward": reward})
            })
            step_num += 1

        except Exception as e:
            print(f"Error: {e}")
            break

    # Final Score Logic
    info = step_res.get("info", {})
    final_score = info.get("grader_score", sum(rewards)/len(rewards) if rewards else 0.0)
    success_str = str(final_score > 0.2).lower() # 0.2 is a more realistic success threshold
    rewards_str = ",".join([f"{r:.2f}" for r in rewards])
    
    print(f"[END] success={success_str} steps={step_num-1} score={final_score:.2f} rewards={rewards_str}", flush=True)

if __name__ == "__main__":
    check_server()
    for t in ["task_1_easy", "task_2_medium", "task_3_hard"]:
        run_task(t)
