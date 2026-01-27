from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import time
from scripts.hybrid_retrieve import HybridBibleRetriever
from scripts.context_builder import build_context
from scripts.query_rewrite import rewrite_queries
from prompts.bible_centric import BIBLE_SYSTEM_PROMPT
from scripts.ollama_client import ollama_chat
from scripts.guarded_answer import answer_with_guardrails


app = FastAPI()
retriever = HybridBibleRetriever(top_k_vec=20, top_k_bm25=40)

class AskReq(BaseModel):
    question : str 

class SearchReq(BaseModel):
    query: str = Field(..., min_length=1)
    k: int = Field(10, ge=1, le=50)
    use_rewrite: bool = True

@app.post("/ask")
def ask(req: AskReq):
    q = req.question.strip()
    queries = rewrite_queries(q)
    passages = retriever.search(queries)

    if not passages:
        return {"status": "retrieval_empty", "answer": None, "queries": queries}
    
    context, allowed_refs = build_context(passages, max_passages=10)

    def llm_fn(system_prompt, context, question, allowed_refs):
        return ollama_chat(
            model="llama3:8b",
            system_prompt=system_prompt,
            context=context,
            question=question,
            allowed_refs=allowed_refs
        )
    
    answer, found, invalid, tries = answer_with_guardrails(system_prompt=BIBLE_SYSTEM_PROMPT,
                                                                    context=context,
                                                                    question=q,
                                                                    allowed_refs=allowed_refs,
                                                                    llm_fn=llm_fn,
                                                                    max_tries=2
                                                                    )
    
    status = "ok" if not invalid else "fail_closed_citation"
    return {
        "status": status,
        "answer": answer,
        "queries": queries,
        "allowed_refs": allowed_refs,
        "found_refs": found,
        "tries": tries
    }

