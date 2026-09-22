from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from src.agents.groq_agent import run_agent


app = FastAPI(
    title="Apex Manufacturing AI",
    description=(
        "AI-powered manufacturing analytics, "
        "machine investigation, ML prediction, "
        "and knowledge assistance API."
    ),
    version="1.0.0",
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    question: str
    answer: str


@app.get("/")
def root():
    """
    Basic API health endpoint.
    """

    return {
        "name": "Apex Manufacturing AI",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    """
    Health-check endpoint.
    """

    return {
        "status": "healthy",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Send a natural-language manufacturing question
    to the AI agent.
    """

    question = request.question.strip()

    if not question:

        return ChatResponse(
            question="",
            answer=(
                "Please provide a manufacturing question."
            ),
        )

    answer = run_agent(question)

    return ChatResponse(
        question=question,
        answer=answer,
    )