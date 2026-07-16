from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.models import ChatRequest, ChatResponse
from app.graph.builder import run_agent

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"


def create_app() -> FastAPI:
    api_app = FastAPI(title="LangGraph AI Agent", version="1.0.0")

    api_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @api_app.get("/health")
    async def health():
        return {"status": "ok"}

    @api_app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        result = run_agent(request.question, request.resume_path)
        return ChatResponse(answer=result.get("answer", ""), intent=result.get("intent"))

    # Serve the plain HTML/CSS/JS frontend at "/"
    api_app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

    return api_app


app = create_app()