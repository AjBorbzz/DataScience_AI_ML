import json
from pathlib import Path
from datetime import datetime

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

TARGET_GRD = 0.85
MAX_OUTER_ATTEMPTS = 3

REQUIRED_HEADERS = [
    "Biblical Summary:",
    "Key Scriptures:",
    "Explanation:",
    "Wisdom Applications:",
]
HEADER_SET = set(REQUIRED_HEADERS)


def format_compliance(answer: str) -> int:
    return int(all(h in answer for h in REQUIRED_HEADERS))


def _norm_ref(r: str) -> str:
    # normalize "(Luke 6:11-15)" -> "Luke 6:11-15"
    r = (r or "").strip()
    if r.startswith("(") and r.endswith(")"):
        r = r[1:-1].strip()
    return " ".join(r.split())


def groundedness(answer: str, allowed_refs: list[str]) -> float:
    allowed = {_norm_ref(r) for r in (allowed_refs or [])}
    if not allowed:
        return 0.0

    lines = [ln.strip() for ln in answer.splitlines()]
    content_lines: list[str] = []
    for ln in lines:
        if not ln:
            continue
        if ln in HEADER_SET:
            continue
        if ln.lower() in {"- (none)", "- (none retrieved)"}:
            continue
        content_lines.append(ln)

    if not content_lines:
        return 0.0

    hits = 0
    for ln in content_lines:
        refs_in_line = {_norm_ref(r) for r in extract_refs(ln)}
        if refs_in_line & allowed:
            hits += 1

    return hits / len(content_lines)


def llm_fn(system_prompt: str, context: str, question: str, allowed_refs: list[str]) -> str:
    return ollama_chat(
        model="llama3:8b",
        system_prompt=system_prompt,
        context=context,
        question=question,
        allowed_refs=allowed_refs,
    )


def no_retrieval_answer() -> str:
    return (
        "Biblical Summary:\n"
        "No relevant passages were retrieved for this question.\n\n"
        "Key Scriptures:\n"
        "- (none retrieved)\n\n"
        "Explanation:\n"
        "Retrieval returned no passages. Improve query rewriting and retrieval configuration.\n\n"
        "Wisdom Applications:\n"
        "- Re-run with improved retrieval queries.\n"
    )


def fail_closed_groundedness_answer() -> str:
    return (
        "Biblical Summary:\n"
        "Unable to answer with required citation density using the retrieved passages.\n\n"
        "Key Scriptures:\n"
        "- (none retrieved)\n\n"
        "Explanation:\n"
        "Fail-closed: groundedness requirement not met.\n\n"
        "Wisdom Applications:\n"
        "- Re-run with improved retrieval.\n"
    )


def main():
    retriever = HybridBibleRetriever(top_k_vec=20, top_k_bm25=40)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = OUTDIR / f"results_{stamp}.jsonl"

    total = 0
    cite_ok = 0
    fmt_ok = 0
    grounded_sum_all = 0.0

    answered = 0
    grounded_sum_answered = 0.0

    with TESTSET.open("r", encoding="utf-8") as f, outfile.open("w", encoding="utf-8") as out:
        for line in f:
            total += 1
            item = json.loads(line)
            q = item["question"]

            queries = rewrite_queries(q)
            passages = retriever.search(queries)

            if not passages:
                answer = no_retrieval_answer()
                allowed_refs = []
                found = []
                invalid = []
                cite_valid = 0  # no citations present -> not valid for your objective
                fmt_valid = 1
                grd = 0.0
            else:
                context, allowed_refs = build_context(passages)

                best = None  # (answer, found, invalid, cite_valid, fmt_valid, grd)
                for _ in range(MAX_OUTER_ATTEMPTS):
                    answer, _, _, _ = answer_with_guardrails(
                        system_prompt=BIBLE_SYSTEM_PROMPT,
                        context=context,
                        question=q,
                        allowed_refs=allowed_refs,
                        llm_fn=llm_fn,
                        max_tries=1,
                    )

                    found = list(dict.fromkeys(extract_refs(answer)))
                    invalid = validate_refs(found, allowed_refs)

                    fmt_valid = format_compliance(answer)
                    grd = groundedness(answer, allowed_refs)

                    # IMPORTANT: require at least 1 ref found, otherwise "citation_valid" is meaningless
                    cite_valid = int(len(found) > 0 and len(invalid) == 0)

                    cand = (answer, found, invalid, cite_valid, fmt_valid, grd)
                    if best is None or grd > best[-1]:
                        best = cand

                    if cite_valid and fmt_valid and grd >= TARGET_GRD:
                        break

                answer, found, invalid, cite_valid, fmt_valid, grd = best

                if grd < TARGET_GRD:
                    # keep your current behavior: fail closed
                    answer = fail_closed_groundedness_answer()
                    found = []
                    invalid = []
                    cite_valid = 0
                    fmt_valid = 1
                    grd = 0.0

            cite_ok += cite_valid
            fmt_ok += fmt_valid
            grounded_sum_all += grd

            if passages and len(found) > 0:
                answered += 1
                grounded_sum_answered += grd

            rec = {
                "id": item.get("id"),
                "category": item.get("category"),
                "question": q,
                "queries": queries,
                "retrieved_count": len(passages) if passages else 0,
                "allowed_refs": allowed_refs,
                "found_refs": found,
                "invalid_refs": invalid,
                "citation_valid": cite_valid,
                "format_valid": fmt_valid,
                "groundedness": grd,
                "answer": answer,
            }
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")

    summary = {
        "total": total,
        "citation_valid_rate": cite_ok / total if total else 0.0,
        "format_valid_rate": fmt_ok / total if total else 0.0,
        "avg_groundedness_all": grounded_sum_all / total if total else 0.0,
        "avg_groundedness_answered_only": grounded_sum_answered / answered if answered else 0.0,
        "answered_rate": answered / total if total else 0.0,
    }

    print("SUMMARY")
    for k, v in summary.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
