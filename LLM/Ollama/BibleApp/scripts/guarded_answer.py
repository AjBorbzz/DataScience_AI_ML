from scripts.verse_guard import extract_refs, validate_refs
import re

def answer_with_guardrails(system_prompt, context, question, allowed_refs, llm_fn, max_tries=2):
    last_answer = None

    for attempt in range(1, max_tries + 1):
        answer = llm_fn(
            system_prompt=system_prompt,
            context=context,
            question=question,
            allowed_refs=allowed_refs
        )
        last_answer = answer

        found = extract_refs(answer)
        found = list(dict.fromkeys(found))  # dedupe for clean reporting
        invalid = validate_refs(found, allowed_refs)

        if not invalid:
            return answer, found, invalid, attempt

        # retry once with stricter citation rule
        question = (
            question
            + "\n\nSTRICT: Cite ONLY from Allowed References. "
              "Do not cite any verse not listed. Regenerate."
        )

    # fail-closed ONLY for citation safety
    return (
        "Biblical Summary:\n"
        "Unable to safely answer because the model cited verses outside the retrieved context.\n\n"
        "Key Scriptures:\n"
        "- (none)\n\n"
        "Explanation:\n"
        "Citation validation failed.\n\n"
        "Wisdom Applications:\n"
        "- Re-run with improved retrieval or a different phrasing.\n",
        extract_refs(last_answer or ""),
        ["fail_closed_citation"],
        max_tries
    )


SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')
HEADERS = {"Biblical Summary:", "Key Scriptures:", "Explanation:", "Wisdom Applications:"}

def all_claims_have_one_ref(answer: str, allowed_refs: list[str]) -> bool:
    allowed = set(allowed_refs)
    lines = [ln.strip() for ln in answer.splitlines() if ln.strip()]
    content = []
    for ln in lines:
        if ln in HEADERS:
            continue
        content.append(ln)

    # treat bullets as claims too
    claims = []
    for ln in content:
        claims.extend([s.strip() for s in SENT_SPLIT.split(ln) if len(s.strip()) >= 10])

    if not claims:
        return False

    for c in claims:
        refs = [r for r in extract_refs(c) if r in allowed]
        if len(refs) != 1:
            return False
    return True