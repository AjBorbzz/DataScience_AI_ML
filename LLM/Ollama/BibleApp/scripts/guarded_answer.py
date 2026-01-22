from scripts.verse_guard import extract_refs, validate_refs

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
        invalid = validate_refs(found, allowed_refs)

        if not invalid:
            return answer, found, invalid, attempt

        # tighten and retry
        question = (
            question
            + "\n\nSTRICT RULE: You cited references not in the allowed list. "
              "Regenerate and cite ONLY from the Allowed References list. "
              "If you cannot, produce Key Scriptures using ONLY those references."
        )

    # fail-closed (do not return hallucinated citations)
    return (
        "Unable to safely answer without citing verses outside the retrieved context.",
        extract_refs(last_answer or ""),
        ["fail_closed"],
        max_tries
    )
