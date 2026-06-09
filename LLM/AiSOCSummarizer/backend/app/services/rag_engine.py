from __future__ import annotations 

import re 
from typing import Any 

from app.utils.logging import get_logger 

logger = get_logger(__name__)


ROLE_KEYWORDS: dict[str, list[str]] = {
    "context_extraction": [
        "incident", "severity", "timestamp", "time", "date", "ip","src", "dst",
        "source", "destination", "domain", "url", "hash", "md5", "sha", "user",
        "host", "alert", "rule", "enrich", "event", "remediate"
    ],
    "threat_intel": [
        "malware", "c2", "command", "control", "phish", "dga", "reputation",
        "indicator", "ioc", "threat", "actor", "campaign", "exploit", "payload",
        "domain", "ip", "hash", "url", "blacklist", "bad", "suspicious"
    ],
    "soc_analyst": [
        "user", "host", "asset", "account", "scope", "timeline", "attack",
        "lateral", "privilege", "escalate", "persistence", "execution", "access",
        "login", "process", "network", "connection", "session"
    ],
    "detection_response": [
        "alert", "rule", "detect", "trigger", "block", "contain", "isolate",
        "quarantine", "response", "action", "kill", "terminate", "disable",
        "firewall", "edr", "siem", "telemetry"
    ],
    "best_practices": [
        "patch", "update", "harden", "policy", "control", "mfa", "password",
        "config", "segment", "monitor", "log", "audit", "backup", "prevent"
    ],
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

def chunks_to_context(chunks: list[tuple[str, str]]) -> str:
    return "\n\n---\n\n".join(f"[{cid}]\n{text}" for cid, text in chunks)

def extract_evidence_paths(
                                flat_map: dict[str, Any],
                                used_values: list[str]
                        ) -> list[str]:
    """
    Given a list of values that appeared in the LLM output,
    return the JSON paths that contain those values.
    """
    evidence: list[str] = []
    for val in used_values:
        val_lower = str(val).lower()
        for path, fval in flat_map.items():
            if val_lower and val_lower in str(fval).lower():
                evidence.append(f"{path}: {fval}")

    seen: set[str] = set()
    unique: list[str] = []
    for e in evidence:
        if e not in seen:
            seen.add(e)
            unique.append(e)
    return unique