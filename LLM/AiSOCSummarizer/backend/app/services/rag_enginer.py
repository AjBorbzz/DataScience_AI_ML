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