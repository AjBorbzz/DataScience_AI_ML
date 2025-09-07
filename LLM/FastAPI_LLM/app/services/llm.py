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
    
