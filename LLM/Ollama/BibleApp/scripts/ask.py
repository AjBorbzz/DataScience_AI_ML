from prompts import BIBLE_SYSTEM_PROMPT
from verse_guard import extract_refs, validate_refs
from context_builder import build_context

def answer_with_guardrails(question, rewrite_fn, retriever, llm_fn, max_tries=2):
    queries = rewrite_fn(question)
    passages = retriever.search(queries)
    if not passages:
        return "Scripture does not clearly address this question."

    context, allowed_refs = build_context(passages)

    for attempt in range(max_tries):
        answer = llm_fn(
            system_prompt=BIBLE_SYSTEM_PROMPT,
            context=context,
            question=question,
            allowed_refs=allowed_refs
        )

        found = extract_refs(answer)
        invalid = validate_refs(found, allowed_refs)

        if not invalid:
            return answer

        # tighten instruction and retry
        question = (
            question
            + "\n\nSTRICT CITATION RULE: You cited references not provided in the context. "
              "Regenerate the answer and cite ONLY from the allowed references list."
        )

    # fail closed
    return (
        "Unable to safely generate an answer without invalid verse citations. "
        "Try rephrasing the question."
    )
