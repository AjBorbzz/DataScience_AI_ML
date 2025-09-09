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