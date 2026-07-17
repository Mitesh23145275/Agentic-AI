# Resume Chatbot — LangGraph Multi-Agent + FastAPI

A resume-analysis chatbot built with a multi-node LangGraph pipeline
(Resume Reader → Intent Classifier → Retriever → Response Generator),
served through FastAPI, with a plain HTML/CSS/JS frontend.

## Folder structure

```
resume_chatbot/
├── app/
│   ├── main.py                # FastAPI app + routes (/chat, /health)
│   ├── config.py              # env vars & provider selection
│   ├── models.py              # Pydantic request/response schemas
│   ├── graph/
│   │   ├── state.py           # AgentState (shared "notebook")
│   │   ├── nodes.py           # resume_extraction, intent_classifier, retriever, chatbot
│   │   └── builder.py         # build_graph() + run_agent()
│   ├── llm/
│   │   └── providers.py       # build_llm() for Gemini/OpenAI + Ollama REST call
│   └── utils/
│       └── pdf_reader.py      # extract_resume_text_from_pdf()
├── data/
│   └── sample.pdf             # put your resume PDF here
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── tests/
│   └── test_agent.py
├── .env.example
├── requirements.txt
├── run.py                     # start the FastAPI server
└── run_cli.py                 # terminal chat loop
```

## Why this structure

- **`graph/state.py`** — the shared state ("notebook") every node reads/writes, matching Part 6 of the workshop.
- **`graph/nodes.py`** — one function per node, one responsibility each (Part 7).
- **`graph/builder.py`** — wires nodes into edges, i.e. the routing (Part 8).
- **`llm/providers.py`** — isolates the provider-specific code (Gemini/OpenAI/Ollama) so `nodes.py` doesn't need to know which one is active.
- **`app/main.py`** — only routes; no business logic, so it's trivial to add more endpoints later (e.g. `/upload-resume`).
- **`frontend/`** — served directly by FastAPI's `StaticFiles`, so one `uvicorn` process runs both API and UI.

This mirrors the Day 10 architecture diagram: `FastAPI → LangGraph → [PDF Reader, Intent Agent, ...] → Gemini → Final Answer`.

## Setup

```bash
cd resume_chatbot
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env            # then fill in your API key(s)
```

Place your resume PDF at `data/sample.pdf` (or pass `resume_path` in the request).

## Run the API + frontend

```bash
python run.py
```

Visit `http://localhost:8000` for the chat UI, or call the API directly:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Summarize this candidate's experience"}'
```

## Run the terminal chat loop instead

```bash
python run_cli.py
```

## Run tests

```bash
pytest tests/
```
