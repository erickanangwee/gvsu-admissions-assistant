"""Pydantic models for all API request and response bodies."""
from pydantic import BaseModel, Field

class Turn(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str = Field(..., description='UUID identifying the conversation')
    message: str    = Field(..., max_length=500)
    topic: str | None = None
    history: list[Turn] = []

class Source(BaseModel):
    title: str
    url: str

class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    session_id: str
    pages_fetched: int
    fallback: bool