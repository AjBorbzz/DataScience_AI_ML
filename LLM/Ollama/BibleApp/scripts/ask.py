from retrieve import BibleRetriever
from context_builder import build_context
from prompts import BIBLE_SYSTEM_PROMPT

def ask_bible_llm(question, rewrite_fn, llm_fn):
    # 1. Rewrite query
    queries = rewrite_fn(question)

    # 2. Retrieve Scripture
    retriever = BibleRetriever()
    passages = retriever.search(queries)

    if not passages:
        return "Scripture does not clearly address this question."

    # 3. Build context
    context = build_context(passages)

    # 4. Call LLM with SYSTEM PROMPT + CONTEXT + QUESTION
    return llm_fn(
        system_prompt=BIBLE_SYSTEM_PROMPT,
        context=context,
        question=question
    )
