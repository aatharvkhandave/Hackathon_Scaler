---
title: Scaler Hackathon
emoji: 🚦
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
app_file: server/app.py
---
🚦 SmartCity Traffic AI: Autonomous Urban Congestion Controller
An autonomous agent environment built on the OpenEnv specification for evaluating Large Language Models (LLMs) in real-world urban infrastructure management.

📖 Overview & Motivation
Urban traffic congestion is a complex, multi-billion dollar problem. This environment simulates a city grid where an AI agent acts as a centralized traffic controller. The agent must dynamically toggle traffic light orientations across multiple intersections to clear vehicle queues and minimize wait times.
Unlike simple "toy" simulations, this environment features:
Asymmetric Flow Rates: Intersections vary in capacity.
Dynamic Events: Stochastic "Rush Hour" events that inject traffic mid-simulation, testing an agent's ability to react to changing conditions.
Strict Grader Logic: Deterministic programmatic graders that reward efficiency and punish invalid actions.

🛠️ Environment Specification
This project is fully compliant with the OpenEnv HTTP Mode (v0.1.0).

🕹️ Action Space
The agent interacts with the city by toggling the green-light orientation of intersections.
Type: Action (Pydantic Model)
Parameters: toggle_intersections: List[str] (e.g., ["i1", "i5"])
Effect: Flips the signal from North-South (NS) to East-West (EW) or vice-versa.

👁️ Observation Space
Agents receive a rich, typed observation representing the city's current state:
intersections_status: Signal direction and current car counts for all four directions (N, S, E, W) per intersection.
active_events: Descriptive strings of active dynamic conditions (e.g., "Morning Rush Hour").
total_cars_waiting: A global metric for overall city congestion.
step_count: Progress within the current episode.

📈 Task Curriculum
The environment offers three distinct tasks with a clear difficulty progression:
![alt text](image.png)
Grading Logic: Each task provides a grader_score (0.0–1.0) based on the percentage of total traffic cleared within the allotted step limit.

🚀 Setup & Execution
1. Requirements
Docker
Python 3.10+
An API Key (Groq or Google AI Studio)

2. Launching the Environment
The environment is containerized for portability and reproducible evaluation.
# Build the Docker image
docker build -t traffic-ai .
# Run the simulation server (Exposes port 7860)
docker run -p 7860:7860 traffic-ai
3. Running the Baseline Agent
The baseline uses inference.py to run an LLM (default: Llama 3.3 via Groq) against the simulation.
# Set up your credentials in .env
# OPENAI_API_KEY=your_key_here
# API_BASE_URL=[https://api.groq.com/openai/v1](https://api.groq.com/openai/v1)
# MODEL_NAME=llama-3.3-70b-versatile
python -u inference.py
📊 Baseline Performance
Measured using llama-3.3-70b-versatile on standard 2 vCPU / 8GB RAM hardware:
Easy Task: 0.875 🟢
Medium Task: 0.250 🟡 (Struggles with surge events)
Hard Task: 0.005 🔴 (Baseline policy represents near-random toggling)
⚖️ Compliance & Quality
OpenEnv Validation: Passed 6/6 mandatory criteria.
Reward Function: Provides a dense signal based on cars cleared per step to avoid sparse-reward issues.
Safety: Includes "Shield" logic in inference to handle malformed tool calls from smaller LLMs.
🏁 Real-World Deployment Readiness
Based on Phase 1 testing, the current environment-model alignment is summarized as follows:
Environment Fidelity: High. The inclusion of rush-hour surges and asymmetric flow rates mirrors genuine logistics challenges.
Agent Scalability: Low. While the agent excels at isolated logistics (1x1), the performance decay in the 3x3 grid suggests a need for Hierarchical Reinforcement Learning or Spatial Reasoning to handle city-scale logistics.
Safety & Reliability: Moderate. The 'Shield' logic prevents script crashes, but the agent's inability to clear the Hard Task indicates it is not yet safe for mission-critical urban deployment without human-in-the-loop oversight.
Created for the OpenEnv Meta x Hugging Face Challenge
