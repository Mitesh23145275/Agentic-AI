from typing import Optional

from langgraph.graph import StateGraph, START, END

from app.config import DEFAULT_RESUME_PATH
from app.graph.state import AgentState
from app.graph.nodes import resume_extraction, intent_classifier, retriever, chatbot




def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("resume_extraction", resume_extraction)
        
    graph.add_node("intent_classifier", intent_classifier)
    graph.add_node("retriever", retriever)
    graph.add_node("chatbot", chatbot)

    graph.add_edge(START, "resume_extraction")
    graph.add_edge("resume_extraction", "intent_classifier")
    graph.add_edge("intent_classifier", "retriever")
    graph.add_edge("retriever", "chatbot")
    graph.add_edge("chatbot", END)

    return graph.compile()


agent_graph = build_graph()


def run_agent(question: str, resume_path: Optional[str] = None) -> dict:
    return agent_graph.invoke(
        {
            "question": question,
            "answer": "",
            "resume_text": "",
            "resume_path": resume_path or str(DEFAULT_RESUME_PATH),
            "intent": "",
            "response_style": "",
            "retrieved_context": "",
        }
    )