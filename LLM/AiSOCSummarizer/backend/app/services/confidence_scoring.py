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

