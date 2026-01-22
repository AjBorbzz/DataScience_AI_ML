## Workplan

1. Build Bible knowledge base

* Choose licensed/public-domain Bible text (KJV easiest).
* Normalize to JSONL chunks with metadata (book/chapter/verse range/translation/text).
* Embed chunks and build index (FAISS/Qdrant).
* Smoke test retrieval with a small query script.

2. Enforce Bible-first answer policy

* Define a single system prompt that locks: Scripture-first, citations required, no invented verses, structured output.
* Keep it constant and injected into every generation call.

3. Route every question through retrieval (RAG)

* Query rewrite: turn user question into 5–10 Bible-centric search queries.
* Retrieve top passages (dedupe).
* Assemble context (cap passages; include only Scripture).
* Call Llama 3 8B with: system prompt + allowed refs + retrieved Scripture + user question.

4. Verse-validation guardrail

* Extract verse references from the model output.
* Validate against `allowed_refs` (whitelist from retrieved passages).
* If invalid refs exist: regenerate once with stricter instruction.
* If still invalid: fail-closed with a format-compliant safe message.
* Keep this guardrail gating on citations (hard safety), not on style.

5. Evaluation harness (current phase)

* Build `eval/test_questions.jsonl` (80–120 questions across categories).
* Run batch eval through full pipeline.
* Metrics per item: citation validity, format compliance, groundedness, retrieval diagnostics.
* Output `eval/out/results_*.jsonl` and a summary.
* Use failures to tune retrieval (rewrite prompt, chunk size, embeddings, hybrid BM25+vector).

6. Retrieval quality upgrades (when eval shows weakness)

* Improve query rewrite with category anchors (money, forgiveness, anxiety, etc.).
* Adjust chunking (2–5 verses vs 8–12 for context).
* Swap embedding model for better semantic search.
* Add hybrid retrieval (BM25 + vector) to prevent empty/irrelevant hits.
* Optional re-ranking (cross-encoder) if needed.

7. Production service wrapper

* FastAPI endpoint `/ask` (question → rewrite → retrieve → guard → answer).
* Endpoints for debugging: `/search`, `/context`, `/health`.
* Logging: retrieved refs, allowed refs, found refs, invalid refs, retries.
* Config: model name, top_k, max_passages, temperature, timeouts.

8. Packaging and deployment

* Containerize (Docker).
* Persist index artifacts and version them.
* Deploy local (single host) or cloud (EC2) depending on your target.

9. Optional fine-tuning (only after eval is stable)

* Use LoRA/QLoRA to improve compliance/style and reduce generic answers.
* Keep RAG anyway; fine-tuning is behavior, RAG is knowledge.
* Re-run the same eval set to prove improvement and no regressions.

10. Extensions (optional)

* Denomination modes (neutral / Reformed / Catholic, etc.) via separate prompts or adapters.
* Add trusted commentaries (licensed/public-domain) as a second retrieval corpus.
* Safety policies for sensitive counseling topics (abuse, self-harm, medical/financial specifics).
