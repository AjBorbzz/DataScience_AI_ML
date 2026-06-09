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

    context = ExtractedContext(
        incident_name=_safe_str(ctx_raw.get("incident_name")),
        severity=_safe_str(ctx_raw.get("severity")),
        timestamps=_safe_list(ctx_raw.get("timestamps")),
        source_ips=_safe_list(ctx_raw.get("source_ips")),
        destination_ips=_safe_list(ctx_raw.get("destination_ips")),
        domains=_safe_list(ctx_raw.get("domains")),
        urls=_safe_list(ctx_raw.get("urls")),
        hashes=_safe_list(ctx_raw.get("hashes")),
        usernames=_safe_list(ctx_raw.get("usernames")),
        hostnames=_safe_list(ctx_raw.get("hostnames")),
        alert_names=_safe_list(ctx_raw.get("alert_names")),
        detection_rules=_safe_list(ctx_raw.get("detection_rules")),
        enrichment_results=_safe_list(ctx_raw.get("enrichment_results")),
        relevant_events=_safe_list(ctx_raw.get("relevant_events")),
        remediation_actions=_safe_list(ctx_raw.get("remediation_actions")),
        raw_text=_safe_str(ctx_raw.get("raw_text")),
    )

    context_str = json.dumps(ctx_raw, separators=(",", ":"))

    logger.info("Pipeline step 2: threat intelligence.")
    ti_context = get_context("threat_intel")
    ti_raw = await llm.generate_json(
        prompt=p_ti.build_prompt(ti_context),
        system=p_ti.SYSTEM
    )

    ti = ThreatIntelAssessment(
        suspicious_indicators=_safe_list(ti_raw.get("suspicious_indicators")),
        known_bad_signals=_safe_list(ti_raw.get("known_bad_signals")),
        malware_references=_safe_list(ti_raw.get("malware_references")),
        c2_indicators=_safe_list(ti_raw.get("c2_indicators")),
        phishing_indicators=_safe_list(ti_raw.get("phishing_indicators")),
        dga_like_domains=_safe_list(ti_raw.get("dga_like_domains")),
        unknowns=_safe_list(ti_raw.get("unknowns")),
        assessment_text=_safe_str(ti_raw.get("assessment_text")),
    )

    ti_str = json.dumps(ti_raw, separators=(",", ":"))

    logger.info("Pipeline step 3: SOC Analyst")
    soc_context = get_context("soc_analyst")
    soc_raw = await llm.generate_json(
        prompt=p_soc.build_prompt(soc_context, ti_str),
        system=p_soc.SYSTEM,
    )

    soc = SOCAnalystOutput(
        attack_narrative=_safe_str(soc_raw.get("attack_narrative")),
        affected_users=_safe_list(soc_raw.get("affected_users")),
        affected_hosts=_safe_list(soc_raw.get("affected_hosts")),
        scope=_safe_str(soc_raw.get("scope")),
        timeline=_safe_str(soc_raw.get("timeline")),
        confirmed_facts=_safe_list(soc_raw.get("confirmed_facts")),
        assumptions=_safe_str(soc_raw.get("assumptions")),
    )

    soc_str = json.dumps(soc_raw, separators=(",", ":"))

    logger.info("Pipeline step 4: detection and response")