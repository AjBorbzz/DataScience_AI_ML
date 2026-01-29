import re
from typing import List, Dict
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
        if t.startswith("-"):
            continue
        lines.append(t)

    claims = []
    for ln in lines:
        claims.extend(
            [s.strip() for s in SENT_SPLIT.split(ln) if len(s.strip()) >= 20]
        )
    return claims


def groundedness_supported(answer: str, passages: List[Dict], allowed_refs: List[str]) -> float:
    claims = split_claims(answer)
    if not claims or not passages:
        return 0.0

    allowed = set(allowed_refs)

    ev_texts = []
    ev_refs = []

    for p in passages:
        ev_texts.append(p["text"])
        ev_refs.append(
            f'{p["book"]} {p["chapter"]}:{p["verse_start"]}'
            + (f'-{p["verse_end"]}' if p["verse_end"] != p["verse_start"] else "")
        )

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    vec = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
    )
    X = vec.fit_transform(ev_texts)

    supported = 0

    for c in claims:
        cited = [r for r in extract_refs(c) if r in allowed]
        if not cited:
            continue

        qc = vec.transform([c])
        sims = cosine_similarity(qc, X).ravel()
        j = int(sims.argmax())
        best_sim = float(sims[j])

        if best_sim >= 0.20:
            evr = ev_refs[j]
            if any(r.split(":")[0] in evr or r in evr for r in cited):
                supported += 1

    return supported / max(1, len(claims))
