import re
from typing import List, Dict, Tuple
from scripts.verse_guard import extract_refs

SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')
HEADER_SET = {
    "Biblical Summary:",
    "Key Scriptures:",
    "Explanation:",
    "Wisdom Applications:",
}

def split_claims(answer: str) -> List[str]:
    lines = []
    for ln in answer.splitlines():
        t = ln.strip()
        if not t:
            continue
        if t in HEADER_SET:
            continue
        # keep bullets too; bullets are often the “claims”
        lines.append(t)

    claims = []
    for ln in lines:
        claims.extend([s.strip() for s in SENT_SPLIT.split(ln) if len(s.strip()) >= 15])
    return claims

def passage_ref(p: Dict) -> str:
    b = p["book"]; c = p["chapter"]; s = p["verse_start"]; e = p["verse_end"]
    return f"{b} {c}:{s}" + (f"-{e}" if e != s else "")

def normalize_ref(ref: str) -> Tuple[str, int, int]:
    # expects format "Book N:M" or "Book N:M-K"
    # keep this simple; your validate_refs already enforces format
    book_ch, vv = ref.rsplit(" ", 1)
    ch, rest = vv.split(":")
    if "-" in rest:
        a, b = rest.split("-")
        return (book_ch.strip(), int(ch), int(a))
    return (book_ch.strip(), int(ch), int(rest))

def build_evidence_map(passages: List[Dict]) -> Dict[str, str]:
    m = {}
    for p in passages:
        r = passage_ref(p)
        m[r] = p["text"]
    return m

def groundedness_supported(answer: str, passages: List[Dict], allowed_refs: List[str]) -> float:
    claims = split_claims(answer)
    if not claims:
        return 0.0

    allowed = set(allowed_refs)
    evidence = build_evidence_map(passages)

    # Support rule:
    # A claim counts as supported if it contains >=1 allowed ref, AND
    # the claim shares enough lexical overlap with the evidence passage text for that ref.
    # (lexical overlap beats TF-IDF here because refs are the anchor)
    supported = 0
    total = 0

    for c in claims:
        refs = [r for r in extract_refs(c) if r in allowed]
        if not refs:
            continue
        total += 1

        ok = False
        c_tokens = set(re.findall(r"[a-zA-Z']+", c.lower()))
        for r in refs:
            ev = evidence.get(r)
            if not ev:
                continue
            ev_tokens = set(re.findall(r"[a-zA-Z']+", ev.lower()))
            overlap = len(c_tokens & ev_tokens)
            # tune this threshold; start low
            if overlap >= 4:
                ok = True
                break

        if ok:
            supported += 1

    return supported / max(1, total)
