from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

from rag_engine import ask

load_dotenv()

app = FastAPI(
    title="SmartDoc DSI",
    description="Assistant IA de recherche dans la documentation DSI",
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["Comment redémarrer PostgreSQL ?"])


class AskResponse(BaseModel):
    answer: str
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest):
    answer = ask(payload.question)
    return AskResponse(question=payload.question, answer=answer)
