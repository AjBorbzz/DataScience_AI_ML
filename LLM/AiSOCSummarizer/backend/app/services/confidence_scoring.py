from __future__ import annotations 
from app.models.schemas import (
    ExtractedContext,
    ThreatIntelAssessment,
    SOCAnalystOutput,
    DetectionResponseOutput,
    ConflictReviewOutput,
    IncidentSummary
)

CONFIDENCE_THRESHOLD = 87

def calculate_confidence(context: ExtractedContext, ti, soc): pass