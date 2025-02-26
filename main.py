from openai import OpenAI
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

def answering(word: str) -> str:
    return {"word": "mock", "answer": "mock message"}

@app.get("/")
def read_root():
    return {"It's Working": "Keep Coding!"}

class Payload(BaseModel):
    name: str
    description: str | None = None

@app.post("/")
def call_model(payload: Payload):
    return {"name": payload.name, "description": payload.description}

