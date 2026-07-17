from typing import TypedDict


class AgentState(TypedDict):
    question: str
    answer: str
    resume_text: str
    resume_path: str
    intent: str
    response_style: str
    retrieved_context: str