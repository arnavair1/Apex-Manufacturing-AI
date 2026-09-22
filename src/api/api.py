from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.agents.groq_agent import run_agent


app = FastAPI(
    title="Apex Manufacturing AI",
    description=(
        "AI-powered manufacturing analytics "
        "and natural-language manufacturing agent."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    question: str
    answer: str


@app.get("/")
def root():

    return {
        "name": "Apex Manufacturing AI",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    question = request.question.strip()

    if not question:

        return ChatResponse(
            question="",
            answer="Please provide a manufacturing question.",
        )

    answer = run_agent(question)

    return ChatResponse(
        question=question,
        answer=answer,
    )