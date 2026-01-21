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

def llm_fn(**kwargs):
    raise NotImplementedError("Implement your LLM call here.")

def main():
    retriever = BibleRetriever(top_k=8)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = OUTDIR / f"results_{stamp}.jsonl"

    total = 0
    cite_ok = 0 
    fmt_ok = 0
    grounded_sum = 0.0

    with TESTSET.open("r", encoding="utf-8") as f, outfile.open("w", encoding="utf-8") as out:
        for line in f:
            total += 1
            item = json.loads(line)
            q = item['question']

            passages = retriever.search([q])