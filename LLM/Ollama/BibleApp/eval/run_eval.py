import json
from pathlib import Path 
from datetime import datetime 

from scripts.retrieve import BibleRetriever
from scripts.hybrid_retrieve import HybridBibleRetriever
from scripts.context_builder import build_context 
from scripts.verse_guard import extract_refs, validate_refs 
from scripts.guarded_answer import answer_with_guardrails
from prompts.bible_centric import BIBLE_SYSTEM_PROMPT

from scripts.query_rewrite import rewrite_queries
from scripts.ollama_client import ollama_chat

TESTSET = Path("eval/test_questions.jsonl")
OUTDIR = Path("eval/out")
OUTDIR.mkdir(parents=True, exist_ok=True)

TARGET_GRD = 0.75
MAX_OUTER_RETRIES = 3

REQUIRED_HEADERS = [
    "Biblical Summary:",
    "Key Scriptures:",
    "Explanation:",
    "Wisdom Applications:",
]

HEADER_SET = set(REQUIRED_HEADERS)

def format_compliance(answer: str) -> int: 
    return int(all(h in answer for h in REQUIRED_HEADERS))

def groundedness(answer: str, allowed_refs: list[str]) -> float:
    allowed = set(allowed_refs or [])
    lines = [ln.strip() for ln in answer.splitlines()]

    content_lines = []
    for ln in lines:
        if not ln:
            continue
        if ln in HEADER_SET:
            continue
        if ln.lower() in {"- (none)", "- (none retrieved)"}:
            continue
        content_lines.append(ln)

    if not content_lines or not allowed:
        return 0.0

    hits = 0
    for ln in content_lines:
        if any(r in ln for r in allowed):
            hits += 1
    return hits / len(content_lines)


def llm_fn(system_prompt, context, question, allowed_refs):
    return ollama_chat(
        model="llama3:8b",
        system_prompt=system_prompt,
        context=context,
        question=question,
        allowed_refs=allowed_refs
    )

def main():
    retriever = HybridBibleRetriever(top_k_vec=20, top_k_bm25=40)
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

            if not passages:
                # record a structured "no retrieval" answer that is still format-compliant
                answer = (
                    "Biblical Summary:\n"
                    "Scripture does address betrayal and forgiveness, but no relevant passages were retrieved for this question.\n\n"
                    "Key Scriptures:\n"
                    "- (none retrieved)\n\n"
                    "Explanation:\n"
                    "Retrieval returned no passages. Improve query rewriting and retrieval configuration.\n\n"
                    "Wisdom Applications:\n"
                    "- Re-run with improved retrieval queries.\n"
                )
                cite_valid = 1
                fmt_valid = 1
                grd = 0
            else:
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
                found = list(dict.fromkeys(found))
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
                "answer": answer,
                # "status": status
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