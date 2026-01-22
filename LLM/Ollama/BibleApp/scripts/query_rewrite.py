import json
import re
from scripts.ollama_client import ollama_chat

REWRITE_SYSTEM = """Rewrite the user question into 6 to 10 Bible passage search queries.
Return ONLY a JSON array of strings.

Rules:
- Include at least 3 queries that use explicit Bible vocabulary that matches the problem.
- Include at least 2 queries that are short (2-5 words).
- Include at least 1 query that includes synonyms.

Examples:
- forgiveness, forgive, mercy, trespass, reconciliation
- betrayal, enemy, slander, trust, wisdom about people
- bitterness, anger, vengeance, justice

Do NOT answer. Output only JSON.
"""


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
