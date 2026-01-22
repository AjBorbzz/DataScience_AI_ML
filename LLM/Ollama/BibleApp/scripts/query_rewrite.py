import json
import re
from scripts.ollama_client import ollama_chat

REWRITE_SYSTEM = (
    "Rewrite the user question into Bible passage search queries. "
    "Return ONLY a JSON array of 5 to 8 short strings."
)

JSON_ARRAY_RE = re.compile(r"\[\s*(?:\".*?\"\s*(?:,\s*\".*?\"\s*)*)?\]s*", re.DOTALL)

def rewrite_queries(question: str):
    raw = ollama_chat(
        model="llama3:8b",
        system_prompt=REWRITE_SYSTEM,
        context="",
        question=question,
        allowed_refs=[]
    )

    # Try direct JSON parse
    try:
        qs = json.loads(raw)
        if isinstance(qs, list):
            qs = [q.strip() for q in qs if isinstance(q, str) and q.strip()]
            if len(qs) >= 3:
                return qs[:8]
    except Exception:
        pass

    # Try extracting the first JSON array substring
    m = re.search(r"\[[\s\S]*\]", raw)
    if m:
        try:
            qs = json.loads(m.group(0))
            if isinstance(qs, list):
                qs = [q.strip() for q in qs if isinstance(q, str) and q.strip()]
                if len(qs) >= 3:
                    return qs[:8]
        except Exception:
            pass

    # Fallback expansions (no LLM)
    return [
        question,
        "wisdom",
        "faith",
        "stewardship",
        "prayer",
    ]
