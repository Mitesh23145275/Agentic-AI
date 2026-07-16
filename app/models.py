from typing import Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    resume_path: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    intent: Optional[str] = None