from scripts.verse_guard import extract_refs, validate_refs
from scripts.format_guard import missing_headers
from scripts.section_guard import section_ref_coverage

def answer_with_guardrails(system_prompt, context, question, allowed_refs, llm_fn, max_tries=4):
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
        missing_sections = section_ref_coverage(answer, allowed_refs)

        if (not invalid) and (not missing) and (not missing_sections):
            return answer, found, invalid, attempt

        tighten = []
        if invalid:
            tighten.append("Cite ONLY from Allowed References. Do not cite anything else.")
        if missing:
            tighten.append("Output ALL required headers exactly as in the template.")
        if missing_sections:
            tighten.append(
                "Every section must include at least one Allowed Reference in parentheses, e.g., (Proverbs 22:7). "
                f"Sections missing refs: {', '.join(missing_sections)}"
            )

        question = question + "\n\nSTRICT RULES:\n- " + "\n- ".join(tighten)

    return (
        "Unable to generate a citation-valid, fully grounded, properly formatted answer from the retrieved context.",
        extract_refs(last_answer or ""),
        ["fail_closed"],
        max_tries
    )
