
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
TESTSET_1 = Path("eval/test_questions_1.jsonl")
OUTDIR = Path("eval/out")
OUTDIR.mkdir(parents=True, exist_ok=True)

TARGET_GRD = 0.85
MAX_OUTER_ATTEMPTS = 3  # how many times to re-run guarded generation per question

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
    allowed = set(allowed_refs)
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
        # parse refs from the line the same way you parse from the whole answer
        refs_in_line = set(extract_refs(ln))
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
        "Scripture does address this topic, but no relevant passages were retrieved for this question.\n\n"
        "Key Scriptures:\n"
        "- (none retrieved)\n\n"
        "Explanation:\n"
        "Retrieval returned no passages. Improve query rewriting and retrieval configuration.\n\n"
        "Wisdom Applications:\n"
        "- Re-run with improved retrieval queries.\n"
    )


def fail_closed_answer() -> str:
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

    with TESTSET_1.open("r", encoding="utf-8") as f, outfile.open("w", encoding="utf-8") as out:
        for line in f:
            total += 1
            item = json.loads(line)
            q = item["question"]

            # Defaults per record
            answer = ""
            allowed_refs: list[str] = []
            found: list[str] = []
            invalid: list[str] = []
            cite_valid = 0
            fmt_valid = 0
            grd = 0.0

            queries = rewrite_queries(q)
            passages = retriever.search(queries)

            if total == 1:
                had_passages = 0
                had_found_preclose = 0

            if passages:
                had_passages += 1

            if found:
                had_found_preclose += 1

            if not passages:
                answer = no_retrieval_answer()
                cite_valid = 1
                fmt_valid = 1
                grd = 0.0
            else:
                context, allowed_refs = build_context(passages)

                best = None  # (answer, found, invalid, cite_valid, fmt_valid, grd)
                for _ in range(MAX_OUTER_ATTEMPTS):
                    ans, _, _, _ = answer_with_guardrails(
                        system_prompt=BIBLE_SYSTEM_PROMPT,
                        context=context,
                        question=q,
                        allowed_refs=allowed_refs,
                        llm_fn=llm_fn,
                        max_tries=1,
                    )

                    frefs = list(dict.fromkeys(extract_refs(ans)))
                    inv = validate_refs(frefs, allowed_refs)

                    c_ok = int(len(inv) == 0)
                    f_ok = format_compliance(ans)
                    g = groundedness(ans, allowed_refs)

                    if best is None or g > best[5]:
                        best = (ans, frefs, inv, c_ok, f_ok, g)

                    if c_ok and f_ok and g >= TARGET_GRD:
                        best = (ans, frefs, inv, c_ok, f_ok, g)
                        break

                if best is None:
                    answer = fail_closed_answer()
                    cite_valid = 1
                    fmt_valid = 1
                    grd = 0.0
                    found = []
                    invalid = []
                else:
                    answer, found, invalid, cite_valid, fmt_valid, grd = best
                    if grd < TARGET_GRD:
                        answer = fail_closed_answer()
                        cite_valid = 1
                        fmt_valid = 1
                        grd = 0.0
                        found = []
                        invalid = []

            cite_ok += cite_valid
            fmt_ok += fmt_valid
            grounded_sum_all += grd

            if passages and found:
                answered += 1
                grounded_sum_answered += grd

            rec = {
                "id": item.get("id"),
                "category": item.get("category"),
                "question": q,
                "allowed_refs": allowed_refs,
                "found_refs": found,
                "invalid_refs": invalid,
                "citation_valid": cite_valid,
                "format_valid": fmt_valid,
                "groundedness": grd,
                "answer": answer,
                "had_passages": had_passages,
                "had_found_preclose": had_found_preclose,
            }
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")

    summary = {
        "total": total,
        "citation_valid_rate": (cite_ok / total) if total else 0.0,
        "format_valid_rate": (fmt_ok / total) if total else 0.0,
        "avg_groundedness_all": (grounded_sum_all / total) if total else 0.0,
        "avg_groundedness_answered_only": (grounded_sum_answered / answered) if answered else 0.0,
        "answered_rate": (answered / total) if total else 0.0,
    }

    print("SUMMARY")
    for k, v in summary.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()

