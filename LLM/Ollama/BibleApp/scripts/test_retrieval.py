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

ef fmt_ref(r):
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