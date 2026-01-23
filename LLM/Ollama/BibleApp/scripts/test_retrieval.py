import sys
import pickle
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

INDEX_DIR = Path("index")
FAISS_PATH = INDEX_DIR / "bible_kjv.faiss"
META_PATH = INDEX_DIR / "bible_kjv_meta.pkl"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 5

TEST_CASES = [
    {
        "name": "money_stewardship",
        "query": "I am having trouble with money. What does the Bible say about handling money?",
        "anchors": ["money", "rich", "treasure", "silver", "gold", "mammon", "steward", "poverty", "lend", "debt"],
    },
    {
        "name": "anxiety",
        "query": "I am anxious and worried. What does the Bible say about anxiety?",
        "anchors": ["fear", "afraid", "anxious", "care", "peace", "worry"],
    },
    {
        "name": "forgiveness",
        "query": "I struggle to forgive someone who hurt me. What does the Bible say about forgiveness?",
        "anchors": ["forgive", "forgiven", "mercy", "trespass", "debt"],
    },
]


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)

def warn(msg: str) -> None:
    print(f"[WARN] {msg}")

def ok(msg: str) -> None:
    print(f"[OK] {msg}")

def fmt_ref(r):
    vs, ve = r["verse_start"], r["verse_end"]
    if vs == ve:
        return f'{r["book"]} {r["chapter"]}:{vs}'
    return f'{r["book"]} {r["chapter"]}:{vs}-{ve}'

def validate_record(r: dict) -> None:
    required = ["id", "book", "chapter", "verse_start", "verse_end", "translation", "text"]
    for k in required:
        if k not in r:
            fail(f"Missing key '{k}' in record: {r}")

    if not isinstance(r["book"], str) or not r["book"].strip():
        fail(f"Invalid book: {r.get('book')}")
    if not isinstance(r["chapter"], int) or r["chapter"] <= 0:
        fail(f"Invalid chapter: {r.get('chapter')}")
    if not isinstance(r["verse_start"], int) or r["verse_start"] <= 0:
        fail(f"Invalid verse_start: {r.get('verse_start')}")
    if not isinstance(r["verse_end"], int) or r["verse_end"] <= 0:
        fail(f"Invalid verse_end: {r.get('verse_end')}")
    if r["verse_start"] > r["verse_end"]:
        fail(f"Verse range inverted: {r['verse_start']} > {r['verse_end']} ({fmt_ref(r)})")
    if not isinstance(r["text"], str) or len(r["text"].strip()) < 10:
        fail(f"Text too short/empty for {fmt_ref(r)}")

def main():
    # 1) Existence checks
    if not FAISS_PATH.exists():
        fail(f"Missing FAISS index: {FAISS_PATH}")
    if not META_PATH.exists():
        fail(f"Missing metadata file: {META_PATH}")
    ok("Index files exist")

    # 2) Load index + meta
    try:
        index = faiss.read_index(str(FAISS_PATH))
    except Exception as e:
        fail(f"Failed to read FAISS index: {e}")

    try:
        recs = pickle.loads(META_PATH.read_bytes())
    except Exception as e:
        fail(f"Failed to load metadata pickle: {e}")

    if not isinstance(recs, list) or len(recs) == 0:
        fail("Metadata is empty or invalid")

    if index.ntotal != len(recs):
        fail(f"Index count mismatch: faiss.ntotal={index.ntotal} meta={len(recs)}")

    ok(f"Loaded index + meta: {len(recs)} records")

    # 3) Model load
    try:
        model = SentenceTransformer(MODEL_NAME)
    except Exception as e:
        fail(f"Failed to load embedding model '{MODEL_NAME}': {e}")
    ok(f"Loaded embedding model: {MODEL_NAME}")

    # 4) Query tests
    for tc in TEST_CASES:
        name = tc["name"]
        query = tc["query"]
        anchors = [a.lower() for a in tc.get("anchors", [])]

        qv = model.encode([query], normalize_embeddings=True).astype("float32")
        D, I = index.search(np.array(qv), k=TOP_K)

        scores = D[0].tolist()
        idxs = I[0].tolist()

        if len(idxs) != TOP_K:
            fail(f"{name}: expected {TOP_K} results, got {len(idxs)}")

        # scores should be descending for IndexFlatIP
        if any(scores[i] < scores[i+1] for i in range(len(scores)-1)):
            fail(f"{name}: scores not sorted descending: {scores}")

        ok(f"{name}: retrieved {TOP_K} results (top score={scores[0]:.4f})")

        # Validate each record
        combined_text = ""
        for rank, (score, idx) in enumerate(zip(scores, idxs), start=1):
            if idx < 0 or idx >= len(recs):
                fail(f"{name}: invalid index returned: {idx}")

            r = recs[idx]
            validate_record(r)
            combined_text += " " + r["text"].lower()

            print("-" * 80)
            print(f"{name} | rank={rank} | score={float(score):.4f} | {fmt_ref(r)}")
            print(r["text"][:300] + ("..." if len(r["text"]) > 300 else ""))

        # Soft anchor check: at least one anchor word appears in retrieved passages
        if anchors:
            hit = any(a in combined_text for a in anchors)
            if not hit:
                warn(f"{name}: no anchor keyword found in top results. Consider changing chunk size or embedding model.")

    ok("All retrieval tests completed")

if __name__ == "__main__":
    main()