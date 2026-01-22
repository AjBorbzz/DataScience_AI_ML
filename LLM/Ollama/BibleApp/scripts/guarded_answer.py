from scripts.verse_guard import extract_refs, validate_refs
from scripts.format_guard import missing_headers

def answer_with_guardrails(system_prompt, context, question, allowed_refs, llm_fn, max_tries=3):
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
        invalid = validate_refs(found, allowed_refs)
        missing = missing_headers(answer)

        if (not invalid) and (not missing):
            return answer, found, invalid, attempt

        tighten = []
        if invalid:
            tighten.append(
                "You cited references not in the allowed list. Cite ONLY from Allowed References."
            )
        if missing:
            tighten.append(
                "Your output is missing required sections. Output ALL required headers exactly."
            )

        question = question + "\n\nSTRICT RULES:\n- " + "\n- ".join(tighten)

    return (
        "Unable to safely generate a properly formatted, citation-valid answer from the retrieved context.",
        extract_refs(last_answer or ""),
        ["fail_closed"],
        max_tries
    )
