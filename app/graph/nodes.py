from app.config import DEFAULT_RESUME_PATH
from app.graph.state import AgentState
from app.llm.providers import call_ollama
from app.utils.pdf_reader import extract_resume_text_from_pdf


# ==========================================
# Node 1: Resume Reader
# ==========================================

def resume_extraction(state: AgentState):
    resume_path = state.get("resume_path") or str(DEFAULT_RESUME_PATH)
    resume_text = extract_resume_text_from_pdf(resume_path)

    return {
        "resume_text": resume_text,
        "resume_path": resume_path,
    }


# ==========================================
# Node 2: Intent Classifier
# ==========================================

def intent_classifier(state: AgentState):
    question = state["question"].lower()

    resume_keywords = [
        "resume", "candidate", "experience", "skills", "education",
        "summary", "project", "job", "fit", "profile", "work", "background",
    ]
    greeting_keywords = ["hello", "hi", "hey", "thanks", "thank you"]

    if any(keyword in question for keyword in resume_keywords):
        intent = "resume_analysis"
        response_style = "detailed"
    elif any(keyword in question for keyword in greeting_keywords):
        intent = "greeting"
        response_style = "friendly"
    else:
        intent = "general"
        response_style = "general"

    return {
        "intent": intent,
        "response_style": response_style,
    }


# ==========================================
# Node 3: Retriever (simple keyword-based RAG)
# ==========================================

def retriever(state: AgentState):
    resume_text = state.get("resume_text", "")
    question = state.get("question", "")

    if not resume_text:
        return {"retrieved_context": ""}

    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    keywords = [word for word in question.lower().split() if len(word) > 3]

    if keywords:
        matched_lines = [line for line in lines if any(keyword in line.lower() for keyword in keywords)]
        selected_lines = matched_lines[:8] if matched_lines else lines[:8]
    else:
        selected_lines = lines[:8]

    return {
        "retrieved_context": "\n".join(selected_lines),
    }


# ==========================================
# Node 4: Response Generator
# ==========================================

def chatbot(state: AgentState):
    print("\nExecuting Ollama Node...")

    resume_context = state.get("resume_text", "")
    retrieved_context = state.get("retrieved_context", "")
    question = state["question"]
    intent = state.get("intent", "general")

    if intent == "resume_analysis" and (resume_context or retrieved_context):
        context_block = retrieved_context or resume_context
        prompt = (
            "Use the resume content below when answering the user question.\n"
            f"Resume context:\n{context_block}\n\n"
            f"User question: {question}"
        )
    else:
        prompt = question

    try:
        answer = call_ollama(prompt)
        return {"answer": answer}

    except Exception as exc:
        preview = " | ".join(
            [line.strip() for line in resume_context.splitlines() if line.strip()][:8]
        ) or "No resume text available"
        return {
            "answer": (
                "Sorry, I could not reach Ollama. Local fallback: please make sure the Ollama service is "
                f"running and the model is available. Resume preview: {preview}. Error: {exc}"
            )
        }