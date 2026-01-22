from scripts.retrieve import BibleRetriever
from scripts.context_builder import build_context
from prompts.bible_centric import BIBLE_SYSTEM_PROMPT
from scripts.ollama_client import ollama_chat
from scripts.guarded_answer import answer_with_guardrails

def llm_fn(system_prompt, context, question, allowed_refs):
    return ollama_chat("llama3:8b", system_prompt, context, question, allowed_refs)

q = "I am having trouble with money. What does the Bible say about handling money?"
retriever = BibleRetriever(top_k=8)
passages = retriever.search([q])
context, allowed_refs = build_context(passages)

answer, found, invalid, tries = answer_with_guardrails(
    BIBLE_SYSTEM_PROMPT, context, q, allowed_refs, llm_fn, max_tries=2
)

print("ALLOWED:", allowed_refs)
print("FOUND:", found)
print("INVALID:", invalid)
print("TRIES:", tries)
print(answer)
