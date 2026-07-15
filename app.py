import os
from typing import TypedDict

from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import requests


# ==========================================
# Load Environment Variables
# ==========================================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
LLM_PROVIDER = os.getenv("LLM_PROVIDER")

if not LLM_PROVIDER:
    LLM_PROVIDER = "ollama" if os.getenv("USE_OLLAMA") else "openai" if OPENAI_API_KEY else "gemini"

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


# ==========================================
# Node
# ==========================================

def chatbot(state: AgentState):

    if LLM_PROVIDER == "ollama":
        provider_name = "Ollama"
    elif LLM_PROVIDER == "openai":
        provider_name = "OpenAI"
    else:
        provider_name = "Gemini"

    print(f"\nExecuting {provider_name} Node...")

    try:
        if LLM_PROVIDER == "ollama":
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": state["question"],
                    "stream": False,
                },
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
            return {
                "answer": payload.get("response", "")
            }

        response = llm.invoke(state["question"])
        return {
            "answer": response.content
        }
    except Exception as exc:
        if LLM_PROVIDER == "ollama":
            return {
                "answer": (
                    "Sorry, I could not reach Ollama. "
                    "Make sure Ollama is installed, running, and that the model is pulled. "
                    f"Error: {exc}"
                )
            }

        return {
            "answer": f"Sorry, I could not generate a response. Error: {exc}"
        }


# ==========================================
# Build Graph
# ==========================================

graph = StateGraph(AgentState)

graph.add_node("chatbot", chatbot)

graph.add_edge(START, "chatbot")

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
                "question": question
            }
        )
        print("\nBot :")
        print(result["answer"])