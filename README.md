# LangGraph Agent Setup

This project is a simple LangGraph-based chatbot that can run with Gemini, OpenAI, or a local Ollama model.

## Requirements

- Python 3.9+
- One of the following:
  - a Google API key with access to Gemini, or
  - an OpenAI API key, or
  - Ollama installed locally

## Setup on Windows

1. Open Command Prompt or PowerShell in the project folder.
2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

3. Install the dependencies:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add one of the following configurations:

### Option 1: Use Gemini

```env
GOOGLE_API_KEY=your_google_api_key_here
LLM_PROVIDER=gemini
```

### Option 2: Use OpenAI

```env
OPENAI_API_KEY=your_openai_api_key_here
LLM_PROVIDER=openai
```

### Option 3: Use Ollama locally

```env
LLM_PROVIDER=ollama
USE_OLLAMA=1
OLLAMA_MODEL=mistral:latest
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

If you use Ollama, install it first and run:

```powershell
ollama pull mistral:latest
ollama serve
```

You can also optionally set:

```env
GEMINI_MODEL=gemini-2.0-flash
OPENAI_MODEL=gpt-4o-mini
```

5. Run the app:

```powershell
python app.py
```

## Usage

- The app will start a chat loop in the terminal.
- Type your question and press Enter.
- Type `exit` to quit the program.
- If you place a resume PDF named `sample.pdf` in the project root, the app will extract its text in a dedicated resume node before answering your question.

## Troubleshooting

- If you see an error about `GOOGLE_API_KEY`, make sure the `.env` file exists and contains a valid key.
- If you see an Ollama error, make sure Ollama is installed, the server is running, and the selected model has been pulled.
- If dependencies fail to install, make sure your Python environment is active and `pip` is up to date.