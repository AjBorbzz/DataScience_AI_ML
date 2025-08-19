from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field


class Settings(BaseSettings):
    ollama_base_url : str = Field(default="http://localhost:11434/v1", alias="OLLAMA_BASE_URL")
    ollama_api_key : str = Field(default="ollama", alias="OLLAMA_API_KEY")
    model_name: str = Field(default="llama3:7b", alias="MODEL_NAME")
    request_timeout: int = Field(default=60, alias="REQUEST_TIMEOUT")
    max_tokens: int = Field(default=512, alias="MAX_TOKENS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()