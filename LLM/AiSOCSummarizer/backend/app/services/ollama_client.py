from __future__ import annotations

import json 
import re 
from typing import Any 

import httpx 
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type 

from app.utils.logging import get_logger 

logger = get_logger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2:3b"
TIMEOUT_SECONDS = 600

class OllamaUnavailableError(Exception):
    pass 

class ModelUnavailableError(Exception):
    pass 

class MalformedLLMOutputError(Exception):
    pass 


@retry(
    retry=retry_if_exception_type(MalformedLLMOutputError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True
) 
async def generate(prompt: str, system: str="", num_predict: int=1024) -> str:
    """Send a prompt to Ollama and return the raw text response."""
    payload: dict[str, Any] = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False, 
        "format": "json", 
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "num_predict": num_predict
        }
    }

    if system:
        payload["system"] = system 

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        try:
            resp = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
            )
            resp.raise_for_status() 
        except httpx.ConnectError as exc:
            raise OllamaUnavailableError(
                "Cannot reach Ollama at localhost:11434. Is `ollama serve` running?"
            ) from exc
        except httpx.TimeoutException as exc:
            raise OllamaUnavailableError("Ollama request timed out.") from exc 
        
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise ModelUnavailableError(f"Model '{MODEL_NAME}' not found. Run : ollama pull {MODEL_NAME}") from exc
            raise OllamaUnavailableError(
                f"Ollama returned HTTP {exc.response.status_code}"
            ) from exc
        
    data = resp.json() 
    text: str = data.get("response", "").strip() 
    if not text:
        raise MalformedLLMOutputError("Ollama returned an empty response.")
    return text


@retry(
    retry=retry_if_exception_type(MalformedLLMOutputError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True
) 
async def generate_json(prompt: str, system: str = "", num_predict: int = 1024) -> dict[str, Any]:
    """
    Generate and parse a JSON response from Ollama, retrying on bad JSON
    """
    raw = await generate(prompt, system, num_predict=num_predict)
    text = re.sub(r"```(?:json)?\s*", "", raw).strip()

    decoder = json.JSONDecodeError()
    for m in re.finditer(r"[{\[]", text):
        try:
            obj, _ = decoder.raw_decode(text, m.start())
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue 

    logger.warning("LLM response contained no valid JSON object; retrying.")
    raise MalformedLLMOutputError("No valid JSON object found in LLM Response.")

async def check_health() -> tuple[bool, bool]:
    """Return (ollama_reachable, model_available)"""
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            resp.raise_for_status() 
        except Exception:
            return False, False
    tags = resp.json().get("models", [])
    model_available = any(
        t.get("name", "").startswith(MODEL_NAME.split(":")[0]) for t in tags
    )
    return True, model_available
