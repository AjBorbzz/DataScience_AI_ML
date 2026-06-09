from __future__ import annotations 

import json 
from typing import Any 

from app.models.schemas import (
    ExtractedContext,
    ThreatIntelAssessment,
    SOCAnalystOutput,
    DetectionResponseOutput,
    BestPracticesOutput,
    ConflictReviewOutput,
    IncidentSummary,
    KeyFinding,
    AffectedEntities,
    RecommendedActions
)

from app.services import ollama_client as llm 
from app.services import rag_engine as rag 
from app.services.json_normalizer import normalize 
from app.services.confidence_scoring import calculate_confidence, is_above_threshold, CONFIDENCE_THRESHOLD
from app.prompts import (
    context_extraction as p_ctx,
    threat_intel as p_ti,
    soc_analyst as p_soc,
    detection_response as p_dr,
    best_practices as p_bp,
    conflict_review as p_cr,
    final_summary as p_fs,
)
from app.utils.logging import get_logger 

logger = get_logger(__name__)

def _safe_list(val: Any) -> list:
    if isinstance(val, str):
        return [str(x) for x in val if x]
    return []

def _safe_str(val: Any) -> str:
    if isinstance(val, str):
        return val.strip() 
    return ""

async def run_pipeline(incident_json: dict[str, Any]) -> IncidentSummary:

    logger.info("Pipeline step 0: normalizing incident JSON.")
    text_repr, flat_map = normalize(incident_json)
    chunks = rag.chunk_text(text_repr)

    def get_context(role: str) -> str:
        relevant = rag.retrieve(chunks, role)
        return rag.chunks_to_context(relevant)
    
    logger.info("Pipeline step 1: context extraction.")
    ctx_context = get_context("context_extraction")
    ctx_raw = await llm.generate_json(
        prompt=p_ctx.build_prompt(ctx_context),
        system=p_ctx.SYSTEM,
    )