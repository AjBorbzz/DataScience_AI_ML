from __future__ import annotations 

import json 
from typing import Any

from app.utils.logging import get_logger 

logger = get_logger(__name__)

def flatten(obj: Any, prefix: str = "") -> dict[str, Any]:
    """Recursively flatten a nested dict/list into dot-path keyed entries."""

    items: dict[str, Any] = {}

    if isinstance(obj, dict):
        for k,v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            items.update(flatten(v, path))

    elif isinstance(obj, list):
        for i,v in enumerate(obj):
            path = f"{prefix}[{i}]"
            items.update(flatten(v, path))
    else:
        items[prefix] = obj

    return items

def normalize(incident_json: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """
    Return (full_text_repr, flat_map),
    full_text_repr: compact JSON string safe to embed in prompts.
    flat_map: path -> value for evidence citation.

    """

    flat = flatten(incident_json)

    lines = [f"{k}: {v}" for k,v in flat.items() if v not in (None, "", [], {})]
    text_repr = "\n".join(lines)
    logger.info("Normalized incident JSON to %d fields", len(flat))
    return text_repr, flat

def safe_json_str(incident_json: dict[str, Any], max_chars: int = 8_000) -> str:
    """
    Compact JSON string, truncated if necessary to protect context window.
    """

    s = json.dumps(incident_json, separators=(",", ":"))
    if len(s) > max_chars:
        logger.warning(
            "Incident JSON truncated from %d to %d chars for LLM context.",
            len(s),
            max_chars
        )
        return s[:max_chars] + "... [TRUNCATED]"
    return s