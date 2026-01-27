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

class ContextReq(BaseModel):
    question: str = Field(..., min_length=1)
    max_passages: int = Field(10, ge=1, le=20)
    k: int = Field(20, ge=1, le=50)
    use_rewrite: bool = True

def ref_str(r: Dict[str, Any]) -> str:
    vs, ve = r["verse_start"], r["verse_end"]
    base = f'{r["book"]} {r["chapter"]}:{vs}'
    return base if vs == ve else f"{base}-{ve}"

@app.get("/health")
def health():
    return {
        "status": "ok",
        "retriever": {
            "type": retriever.__class__.__name__,
            "top_k_vec": getattr(retriever, "top_k_vec", None),
            "top_k_bm25": getattr(retriever, "top_k_bm25", None),
        },
    }

@app.post("/search")
def search(req: SearchReq):
    """
    Debug retrieval.
    - If use_rewrite=True: query is rewritten into multiple retrieval queries.
    - Returns ranked passages with refs and scores.
    """
    t0 = time.time()

    queries = rewrite_queries(req.query) if req.use_rewrite else [req.query]
    passages = retriever.search(queries)

    # cap to requested k after merge/dedupe
    passages = passages[: req.k]

    results = []
    for p in passages:
        results.append({
            "ref": ref_str(p),
            "book": p["book"],
            "chapter": p["chapter"],
            "verse_start": p["verse_start"],
            "verse_end": p["verse_end"],
            "translation": p.get("translation"),
            "score": p.get("score"),
            "source": p.get("source"),  # if hybrid retriever provides it
            "text": p["text"],
        })

    return {
        "queries_used": queries,
        "count": len(results),
        "latency_ms": int((time.time() - t0) * 1000),
        "results": results,
    }

@app.post("/context")
def context(req: ContextReq):
    """
    Debug the exact model-visible context you will send to LLM.
    - Runs rewrite (optional) + retrieval + context assembly.
    - Returns allowed_refs + context string.
    """
    t0 = time.time()

    queries = rewrite_queries(req.question) if req.use_rewrite else [req.question]

    # widen retrieval by temporarily overriding breadth:
    # If your HybridBibleRetriever doesn't accept per-call k, widen via constructor config.
    passages = retriever.search(queries)

    # build_context will cap to max_passages
    context_text, allowed_refs = build_context(passages, max_passages=req.max_passages)

    return {
        "queries_used": queries,
        "allowed_refs": allowed_refs,
        "context": context_text,
        "retrieved_count_total": len(passages),
        "latency_ms": int((time.time() - t0) * 1000),
    }

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

