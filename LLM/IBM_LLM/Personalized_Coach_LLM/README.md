# FastAPI Private Llama Chat

A minimal FastAPI service that connects to a private Llama 3 model (via Ollama
 or llama.cpp
) and exposes a simple API for chat.
This replaces IBM Watson dependencies with a fully local and private setup.

### Features

- Chat endpoint powered by Llama 3 (8B or other variants).

- Configurable backends: Ollama (daemon) or llama.cpp (in-process).

- Production-ready file structure with Docker support.

- Privacy-first: no external cloud APIs required.


## Why private?
- Keep data on your machines (compliance / privacy).
- No vendor lock-in; switch between Ollama or llama.cpp.

## Run (local)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload