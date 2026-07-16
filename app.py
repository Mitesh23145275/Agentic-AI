import os
from pathlib import Path
from typing import Optional, TypedDict

from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import requests

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - optional dependency fallback
    PdfReader = None


# ==========================================
# Load Environment Variables
# ==========================================

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_RESUME_PATH = ROOT_DIR / "sample.pdf"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))
LLM_PROVIDER = os.getenv("LLM_PROVIDER")

if not LLM_PROVIDER:
    if os.getenv("USE_OLLAMA"):
        LLM_PROVIDER = "ollama"
    elif OPENAI_API_KEY:
        LLM_PROVIDER = "openai"
    elif GOOGLE_API_KEY:
        LLM_PROVIDER = "gemini"
    else:
        LLM_PROVIDER = "ollama"

if LLM_PROVIDER not in {"ollama", "openai", "gemini"}:
    LLM_PROVIDER = "ollama"

LLM_PROVIDER = LLM_PROVIDER.lower()


# ==========================================
# LLM Setup
# ==========================================

def build_llm():
    if LLM_PROVIDER == "ollama":
        return None

    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found!")

        return ChatOpenAI(
            model=OPENAI_MODEL,
            temperature=0.3,
            api_key=OPENAI_API_KEY,
        )

    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found!")

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0.3,
        google_api_key=GOOGLE_API_KEY,
    )


llm = build_llm()


# ==========================================
# State
# ==========================================

class AgentState(TypedDict):
    question: str
    answer: str
    resume_text: str
    resume_path: str
    intent: str
    response_style: str


# ==========================================
# Nodes
# ==========================================

def extract_resume_text_from_pdf(pdf_path: Optional[str] = None) -> str:
    resume_path = pdf_path or str(DEFAULT_RESUME_PATH)

    if not os.path.exists(resume_path):
        return ""

    if PdfReader is None:
        return "Resume extraction is unavailable because pypdf is not installed."

    try:
        reader = PdfReader(resume_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(page for page in pages if page).strip()
    except Exception as exc:
        return f"Unable to read resume PDF: {exc}"


def resume_extraction(state: AgentState):
    resume_path = state.get("resume_path") or str(DEFAULT_RESUME_PATH)
    resume_text = extract_resume_text_from_pdf(resume_path)

    return {
        "resume_text": resume_text,
        "resume_path": resume_path,
    }


def build_local_fallback_answer(question: str, resume_text: str, error_message: str = "") -> str:
    error_suffix = f" Error: {error_message}" if error_message else ""

    if not resume_text:
        return (
            "Sorry, I could not reach an LLM service. Local fallback: no resume text was found. "
            "Place a PDF named sample.pdf in the project root or provide a resume file for analysis."
            f"{error_suffix}"
        )

    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    preview = " | ".join(lines[:8])
    lowered_question = question.lower()

    if "summar" in lowered_question:
        return (
            "Sorry, I could not reach an LLM service. Local fallback: here is a simple summary based on the resume text:\n"
            f"{preview}{error_suffix}"
        )

    return (
        "Sorry, I could not reach an LLM service. Local fallback: I am using the resume text below to answer your question:\n"
        f"{preview}{error_suffix}"
    )


def intent_classifier(state: AgentState):
    question = state["question"].lower()

    if any(keyword in question for keyword in ["resume", "candidate", "experience", "skills", "education", "summary", "project", "job", "fit", "profile", "work", "background"]):
        intent = "resume_analysis"
        response_style = "detailed"
    elif any(keyword in question for keyword in ["hello", "hi", "hey", "thanks", "thank you"]):
        intent = "greeting"
        response_style = "friendly"
    else:
        intent = "general"
        response_style = "general"

    return {
        "intent": intent,
        "response_style": response_style,
    }


def chatbot(state: AgentState):

    if LLM_PROVIDER == "ollama":
        provider_name = "Ollama"
    elif LLM_PROVIDER == "openai":
        provider_name = "OpenAI"
    else:
        provider_name = "Gemini"

    print(f"\nExecuting {provider_name} Node...")
    if LLM_PROVIDER == "ollama":
        print("Using live Ollama response...")

    try:
        resume_context = state.get("resume_text", "")
        question = state["question"]
        intent = state.get("intent", "general")

        if intent == "resume_analysis" and resume_context:
            prompt = (
                "Use the resume content below when answering the user question.\n"
                f"Resume:\n{resume_context}\n\n"
                f"User question: {question}"
            )
        else:
            prompt = question

        if LLM_PROVIDER == "ollama":
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=OLLAMA_TIMEOUT,
            )
            response.raise_for_status()
            payload = response.json()
            return {
                "answer": payload.get("response", "")
            }

        response = llm.invoke(prompt)
        return {
            "answer": response.content
        }
    except Exception as exc:
        if LLM_PROVIDER == "ollama":
            resume_text = state.get("resume_text", "")
            preview = " | ".join([line.strip() for line in resume_text.splitlines() if line.strip()][:8]) or "No resume text available"
            return {
                "answer": (
                    "Sorry, I could not reach Ollama. Local fallback: please make sure the Ollama service is running "
                    f"and the model is available. Resume preview: {preview}. Error: {exc}"
                )
            }

        return {
            "answer": build_local_fallback_answer(question, state.get("resume_text", ""), str(exc))
        }


# ==========================================
# Build Graph
# ==========================================

graph = StateGraph(AgentState)

graph.add_node("resume_extraction", resume_extraction)
graph.add_node("intent_classifier", intent_classifier)
graph.add_node("chatbot", chatbot)

graph.add_edge(START, "resume_extraction")
graph.add_edge("resume_extraction", "intent_classifier")
graph.add_edge("intent_classifier", "chatbot")
graph.add_edge("chatbot", END)

app = graph.compile()


# ==========================================
# Chat Loop
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("LangGraph AI Agent")
    print("Type 'exit' to quit")
    print("=" * 60)

    while True:

        question = input("\nYou : ")

        if question.lower() == "exit":
            print("\nGoodbye!")
            break

        result = app.invoke(
            {
                "question": question,
                "resume_path": str(DEFAULT_RESUME_PATH),
            }
        )

        print("\nBot :")
        print(result["answer"])