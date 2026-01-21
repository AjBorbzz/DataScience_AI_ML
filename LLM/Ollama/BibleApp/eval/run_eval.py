import json
from pathlib import Path 
from datetime import datetime 

from scripts.retrieve import BibleRetriever
from scripts.context_builder import build_context 
from scripts.verse_guard import extract_refs, validate_refs 
from prompts.bible_centric import BIBLE_SYSTEM_PROMPT

TESTSET = Path("eval/test_questions.jsonl")
OUTDIR = Path("eval/out")
OUTDIR.mkdir(parents=True, exist_ok=True)

REQUIRED_HEADERS = [
    "Biblical Summary:",
    "Key Scriptures:",
    "Explanation:",
    "Wisdom Applications:",
]

def format_compliance(answer: str) -> int: 
    return int(all(h in answer for h in REQUIRED_HEADERS))

def groundedness(answer: str) -> float:
    paras = [p.strip() for p in answer.split("\n\n") if p.strip()]

    if not paras: 
        return 0.0
    with_refs = sum(1 for p in paras if ":" in p)
    return with_refs / len(paras)