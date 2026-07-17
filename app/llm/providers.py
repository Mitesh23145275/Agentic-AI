import requests

from app.config import OLLAMA_MODEL, OLLAMA_BASE_URL, OLLAMA_TIMEOUT


def call_ollama(prompt: str) -> str:
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
    return payload.get("response", "")