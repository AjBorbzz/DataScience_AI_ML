import json
from scripts.ollama_client import ollama_chat

REWRITE_SYSTEM = """You rewrite a user question into Bible passage search queries.
Return ONLY a JSON list of 5 to 8 short search queries (strings).
Use biblical concepts. No commentary. No extra text."""

def rewrite_queries(question: str):
    # use the same model; low temp
    raw = ollama_chat(
        model="llama3:8b",
        system_prompt=REWRITE_SYSTEM,
        context="",
        question=question,
        allowed_refs=[]
    )
    # raw must be JSON list; fail-safe
    try:
        qs = json.loads(raw)
        return [q.strip() for q in qs if isinstance(q, str) and q.strip()][:8]
    except Exception:
        # fallback: simple expansions
        return [question]
