import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.agents.groq_agent import run_agent


app = FastAPI(
    title="Apex Manufacturing AI",
    description="AI-powered manufacturing intelligence API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {
        "name": "Apex Manufacturing AI",
        "status": "online",
        "message": "Manufacturing AI API is running.",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post("/chat")
def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    try:
        response = run_agent(message)

        return {
            "response": response,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(exc)}",
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))

    uvicorn.run(
        "src.api.api:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )