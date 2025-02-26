from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

origins = [
    "http://localhost:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System configuration
BUFFER_SIZE = 2  # Max buffer size per server
NUM_SERVERS = 3  # Number of servers
STATES = list(range(BUFFER_SIZE + 1))
ACTIONS = [0, 1, 2]  # 0: Discard, 1: Process, 2: Redirect

# Initialize server buffers
server_buffers = [0] * NUM_SERVERS

def get_least_loaded_server():
    return min(range(NUM_SERVERS), key=lambda i: server_buffers[i])

def transition(server, state, action):
    """ Simulates state transitions based on actions """
    arrival_prob = 0.6  # Probability of new request
    processing_prob = 0.7  # Probability of successful processing

    next_state = state
    if action == 1 and state > 0:  # Process request
        if random.random() < processing_prob:
            next_state = max(0, state - 1)
            logging.info(f"Server {server} processed a request. New state: {next_state}")
    elif action == 2 and state == BUFFER_SIZE:  # Redirect only when full
        target_server = get_least_loaded_server()
        if target_server != server and server_buffers[target_server] < BUFFER_SIZE:
            server_buffers[target_server] += 1
            logging.info(f"Redirected request from Server {server} to Server {target_server}")
        else:
            logging.info(f"Server {server} could not redirect; all servers full")
    elif action == 0 and state == BUFFER_SIZE:  # Discard when full
        logging.info(f"Server {server} discarded a request due to full buffer")

    if random.random() < arrival_prob:
        next_state = min(BUFFER_SIZE, next_state + 1)
        logging.info(f"New request arrived at Server {server}. New state: {next_state}")

    server_buffers[server] = next_state  # Update global state
    return next_state

def reward(state, action):
    if action == 1:  # Process request
        return 3 if state > 0 else 0
    elif action == 2:  # Redirect request
        return 1 if state == BUFFER_SIZE else -1
    elif action == 0:  # Discard request
        return -5 if state == BUFFER_SIZE else -1
    return 0

def simulate_mdp(N):
    global server_buffers
    server_buffers = [random.randint(0, BUFFER_SIZE) for _ in range(NUM_SERVERS)]  # Random initial states
    simulation_results = []

    for t in range(N):
        server = random.choice(range(NUM_SERVERS))  # Pick a random server
        state = server_buffers[server]

        if state == BUFFER_SIZE:
            action = 2  # Redirect if full
        elif state > 0:
            action = 1  # Process if there's something in buffer
        else:
            action = 0  # Discard otherwise

        r = reward(state, action)
        next_state = transition(server, state, action)

        logging.info(f"Iteration {t}: Server {server}, Action {action}, Reward {r}, Next State {next_state}")

        simulation_results.append({
            "iteration": t,
            "server": server,
            "action": action,
            "reward": r,
            "next_state": next_state
        })
    return simulation_results

@app.get("/")
def read_root():
    return {"message": "MDP Load Balancer Running"}

class Payload(BaseModel):
    N: int

@app.post("/")
def call_model(payload: Payload):
    results = simulate_mdp(payload.N)
    return {"message": "MDP simulation completed", "simulation_results": results}
