from __future__ import annotations 

import re 
from typing import Any 

from app.utils.logging import get_logger 

logger = get_logger(__name__)


ROLE_KEYWORDS: dict[str, list[str]] = {
    "context_extraction": [],
    "threat_intel": [],
    "soc_analyst": [],
    "detection_response": [],
    "best_practices": [],
}

_MAX_CHUNKS = 4 
_CHUNK_SIZE = 800 # characters per chunk .

def chunk_text(text: str) -> list[tuple[str, str]]:
    """
    Split flat text into (chunk_id, chunk_text) pairs.
    Tries to split at newlines to preserve field boundaries.
    """

    lines = text.split("\n")
    chunks: list[tuple[str, str]] = []
    current: list[str] = []
    current_len = 0
    chunk_idx = 0 

    for line in lines:
        if current_len + len(line) > _CHUNK_SIZE and current:
            chunks.append((f"chunk_{chunk_idx}", "\n".join(current)))
            chunk_idx += 1
            current = []
            current_len = 0
        current.append(line)
        current_len += len(line) + 1

    if current:
        chunks.append(f"chunk_{chunk_idx}", "\n".join(current))

    logger.info("RAG: split text into %d chunks.", len(chunks))
    return chunks

def _score_chunk(chunk: str, keywords: list[str]) -> int:
    lower = chunk.lower()
    return sum(1 for kw in keywords if kw in lower)

def retrieve(
        chunks: list[tuple[str, str]],
        role: str,
        top_k: int = _MAX_CHUNKS
) -> list[tuple[str, str]]:
    """Return the top_k most relevant chunks for a given agent role."""
    keywords = ROLE_KEYWORDS.get(role, [])
    if not keywords:
        return chunks[:top_k]
    
    scored = [(cid, text, _score_chunk(text, keywords)) for cid, text in chunks]
    scored.sort(key=lambda x: x[2], reverse=True)
    results = [(cid, text) for cid, text, _ in scored[:top_k]]
    logger.info("RAG: retrieved %d chunks for role '%s'.", len(results), role)

    return results 

