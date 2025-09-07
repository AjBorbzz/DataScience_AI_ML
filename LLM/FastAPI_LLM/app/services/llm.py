from __future__ import annotations
from typing import List, Dict
from app.core.config import settings


class LLMBackend:
    def chat(self, messages: List[Dict[str,str]], max_tokens: int=512) -> str:
        raise NotImplementedError
    
class OllamaLLM(LLMBackend):
    def __init__(self):
        import requests
        self._requests = requests
        self.base = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL

    def chat(self, messages: List[Dict[str,str]], max_tokens: int= 512) -> str:
        url = f"{self.base}/api/chat"
        payload = {"model": self.model, "messages": messages, "stream": False}
        r = self._requests.post(url, json=payload, timeout=180)
        r.raise_for_status()
        data = r.json()
        return data.get("message", {}).get("content", "")
    
class LlamaCppLLM(LLMBackend):
    def __init__(self):
        from llama_cpp import Llama
        self.llm = Llama(
        model_path=str(settings.LLAMA_MODEL_PATH),
        n_ctx=settings.LLAMA_CTX_SIZE,
        n_threads=settings.LLAMA_THREADS,
        chat_format="llama-3",
        )

    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 512) -> str:
        out = self.llm.create_chat_completion(messages=messages, max_tokens=max_tokens)
        return out["choices"][0]["message"]["content"].strip()
    
def get_llm() -> LLMBackend:
    if settings.LLM_BACKEND.upper() == "OLLAMA":
        return OllamaLLM()
    return LlamaCppLLM