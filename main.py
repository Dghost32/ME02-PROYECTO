from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

# Definir tamaño máximo del buffer
BUFFER_SIZE = 2  # Capacidad máxima del buffer

# Definimos los estados del sistema
# S = {0 (vacío), 1 (parcialmente lleno), ..., BUFFER_SIZE (lleno)}
STATES = list(range(BUFFER_SIZE + 1))

# Definimos las acciones posibles
# A = {0 (descartar paquete), 1 (reenviar paquete)}
ACTIONS = [0, 1]

# Definimos la función de transición de probabilidad P(s' | s, a)
def transition(state, action):
    """
    Simula la transición del estado actual `state` al siguiente estado basado en la acción `action`.
    """
    import random

    # Probabilidad de llegada de un nuevo paquete en cada tiempo
    arrival_prob = 0.6  # Probabilidad de que llegue un paquete nuevo

    if action == 1:  # Si reenviamos el paquete
        next_state = max(0, state - 1)  # Reducimos el nivel del buffer si no está vacío
    else:  # Si descartamos el paquete
        next_state = state  # El buffer se mantiene igual

    # Si llega un nuevo paquete, el buffer aumenta su ocupación
    if random.random() < arrival_prob:
        next_state = min(BUFFER_SIZE, next_state + 1)

    return next_state

# Definimos la función de recompensa R(s, a)
def reward(state, action):
    """
    Retorna la recompensa según el estado y la acción tomada.
    """
    if action == 1:  # Si reenviamos un paquete
        return 1 if state > 0 else 0  # Gana +1 si hay paquetes para reenviar
    else:  # Si descartamos el paquete
        return -1 if state == BUFFER_SIZE else 0  # Penaliza -1 si el buffer está lleno

def simulate_mdp(N, initial_state):
    state = initial_state
    simulation_results = []
    for t in range(N):
        action = 1 if state > 0 else 0  # Política simple: reenvía si hay paquetes
        r = reward(state, action)
        next_state = transition(state, action)
        simulation_results.append({
            "iteration": t,
            "state": state,
            "action": action,
            "reward": r,
            "next_state": next_state
        })
        state = next_state
    return simulation_results

@app.get("/")
def read_root():
    return {"It's Working": "Keep Coding!"}

class Payload(BaseModel):
    N: int
    initial_state: int

@app.post("/")
def call_model(payload: Payload):
    simulation_results = simulate_mdp(payload.N, payload.initial_state)
    return {"message": "MDP simulation completed", "simulation_results": simulation_results}
