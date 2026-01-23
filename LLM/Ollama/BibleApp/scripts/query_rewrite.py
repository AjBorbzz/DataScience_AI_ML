import json
import re
from scripts.ollama_raw import ollama_chat_raw

REWRITE_SYSTEM = """Rewrite the user question into Bible passage search queries.
Return ONLY a JSON array of 8 to 12 short strings.
Use explicit biblical vocabulary and synonyms.
No prose. No markdown. JSON only."""

def rewrite_queries(question: str):
    user = (
        f"User question:\n{question}\n\n"
        "Output JSON array only."
    )
    raw = ollama_chat_raw(
        model="llama3:8b",
        system_prompt=REWRITE_SYSTEM,
        user_content=user,
        temperature=0.0
    )

    # strict JSON extraction
    m = re.search(r"\[[\s\S]*\]", raw)
    if not m:
        return fallback_queries(question)

    try:
        qs = json.loads(m.group(0))
        qs = [q.strip() for q in qs if isinstance(q, str) and q.strip()]
        return qs[:12] if len(qs) >= 5 else fallback_queries(question)
    except Exception:
        return fallback_queries(question)

def fallback_queries(question: str):
    # deterministic safety net (prevents retrieval collapse)
    q = question.lower()
    base = [question]
    if "money" in q or "debt" in q or "paycheck" in q:
        base += ["debt borrowing lender", "stewardship money wealth", "contentment riches", "treasures in heaven", "love of money"]
    if "worry" in q or "anxious" in q or "anxiety" in q:
        base += ["do not fear", "cast your cares", "peace of God", "trust in the Lord", "worry about tomorrow"]
    if "forgive" in q or "betray" in q:
        base += ["forgive seventy times seven", "bitterness anger mercy", "love your enemies", "vengeance belongs to God", "reconciliation"]
    return base[:12]
