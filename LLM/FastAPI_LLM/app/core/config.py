from pydantic import BaseSettings, Field
from pathlib import Path 


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI RAG Chatbot"
    API_PREFIX: str = "/api"
    ALLOWED_ORIGINS: str = "*"

    STORAGE_DIR: Path = Path("storage")
    UPLOAD_DIR: Path = STORAGE_DIR / "uploads"
    FAISS_INDEX_PATH: Path = STORAGE_DIR / "index.faiss"
    DOCS_METADATA_PATH: Path = STORAGE_DIR / "docs.pkl"

    LLM_BACKEND: str = Field("OLLAMA", regex="^(OLLAMA|LLAMA_CPP)$")

    # Ollama Config: Replace for production - Currently for POC - local dev env
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b"

    LLAMA_MODEL_PATH: Path = Path("/models/llama3-8b-instruct.Q4_K_M.gguf")
    LLAMA_CTX_SIZE: int = 4096
    LLAMA_THREADS: int = 8

    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
settings.STORAGE_DIR.mkdir(exist_ok=True)
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)