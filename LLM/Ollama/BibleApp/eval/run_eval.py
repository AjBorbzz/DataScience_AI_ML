import json
from pathlib import Path 
from datetime import datetime 

from scripts.retrieve import BibleRetriever
from scripts.context_builder import build_context 
from scripts.verse_guard import extract_refs, validate_refs 
from scripts.guarded_answer import answer_with_guardrails
from prompts.bible_centric import BIBLE_SYSTEM_PROMPT

from scripts.query_rewrite import rewrite_queries
from scripts.ollama_client import ollama_chat

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

def groundedness(answer: str, allowed_refs: list[str]) -> float:
    sections = [s.strip() for s in answer.split("\n\n") if s.strip()]
    if not sections:
        return 0.0
    allowed = set(allowed_refs)
    hits = 0
    for sec in sections:
        if any(r in sec for r in allowed):
            hits += 1
    return hits / len(sections)


def llm_fn(system_prompt, context, question, allowed_refs):
    return ollama_chat(
        model="llama3:8b",
        system_prompt=system_prompt,
        context=context,
        question=question,
        allowed_refs=allowed_refs
    )

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

            queries = rewrite_queries(q)
            passages = retriever.search(queries)
            context, allowed_refs = build_context(passages)
            
            answer, found, invalid, tries = answer_with_guardrails(
                    system_prompt=BIBLE_SYSTEM_PROMPT,
                    context=context,
                    question=q,
                    allowed_refs=allowed_refs,
                    llm_fn=llm_fn,
                    max_tries=2
                )

            found = extract_refs(answer)
            invalid = validate_refs(found, allowed_refs)

            cite_valid = int(len(invalid) == 0)
            fmt_valid = format_compliance(answer)
            grd = groundedness(answer, allowed_refs)

            cite_ok += cite_valid 
            fmt_ok += fmt_valid 
            grounded_sum += grd 

            rec = {
                "id": item["id"],
                "category": item["category"],
                "question": q,
                "allowed_refs": allowed_refs,
                "found_refs": found,
                "invalid_refs": invalid,
                "citation_valid": cite_valid,
                "format_valid": fmt_valid,
                "groundedness": grd,
                "answer": answer
            }

            out.write(json.dumps(rec, ensure_ascii=False) + "\n")

    summary = {
        "total": total,
        "citation_valid_rate": cite_ok/ total if total else 0.0,
        "format_valid_rate": fmt_ok / total if total else 0.0,
        "avg_groundedness": grounded_sum / total if total else 0.0
    }

    print("SUMMARY")
    for k,v in summary.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()