from __future__ import annotations 
from app.models.schemas import (
    ExtractedContext,
    ThreatIntelAssessment,
    SOCAnalystOutput,
    DetectionResponseOutput,
    ConflictReviewOutput,
    IncidentSummary
)

from app.utils.logging import get_logger 

logger = get_logger(__name__)

CONFIDENCE_THRESHOLD = 87

def calculate_confidence(context: ExtractedContext, 
                         ti: ThreatIntelAssessment, 
                         soc: SOCAnalystOutput,
                         dr: DetectionResponseOutput,
                         cr: ConflictReviewOutput, 
                         summary: IncidentSummary) -> tuple[int,str]:
    """Rubric-based confidence score 0-100.
    Returns (score, reasoning)
    """

    score = 0
    reasons: list[str] = []

    evidence_fields = sum([
        bool(context.incident_name),
        bool(context.severity),
        bool(context.timestamps),
        bool(context.source_ips or context.destination_ips),
        bool(context.usernames or context.hostnames),
        bool(context.alert_names or context.detection_rules)    
        ])
    
    ec_score = min(evidence_fields * 5, 30)
    score += ec_score 

    reasons.append(f"Evidence coverage: {ec_score}/30 ({evidence_fields}/6 key fields present).")

    has_narrative = bool(soc.attack_narrative and len(soc.attack_narrative) > 50)
    has_timeline = bool(soc.timeline)
    has_scope = bool(soc.scope)
    has_facts = bool(soc.confirmed_facts)
    cc_score = sum([has_narrative * 8, has_timeline * 4, has_scope * 4, has_facts * 4])
    score += cc_score
    reasons.append(f"Context completeness: {cc_score}/20.")


    conflicts = len(cr.conflicts_found)
    if conflicts == 0:
        ag_score = 20 
    elif conflicts <= 2:
        ag_score = 14 
    elif conflicts <= 4:
        ag_score = 8
    else:
        ag_score = 2 
    score += ag_score 
    reasons.append(f"Agent agreement: {ag_score}/20 ({conflicts} conflicts detected).")

    weak = len(cr.weak_claims)
    if weak == 0:
        cs_score = 15
    elif weak <= 2:
        cs_score = 10 
    elif weak <= 5:
        cs_score = 6 
    else:
        cs_score = 2 
    score += cs_score

    reasons.append(f"Conflic severity: {cs_score}/15 ({weak} weak/unsupported claims).")

    evidence_used = len(summary.evidence_used) 
    findings_count = len(summary.key_findings)
    if findings_count == 0:
        hr_score = 0

    else:
        coverage_ratio = min(evidence_used / max(findings_count, 1), 1.0)
        hr_score = int(coverage_ratio * 15)

    score += hr_score 
    reasons.append(f"Hallucination Risk proxy: {hr_score}/15 ({evidence_used} evidence citations for {findings_count} findings).")

    score = max(0, min(score, 100))
    reasoning = " | ".join(reasons)
    logger.info("Confidence score: %d/100 - %s", score, reasoning)
    return score, reasoning 

def is_above_threshold(score: int) -> bool:
    return score >= CONFIDENCE_THRESHOLD

