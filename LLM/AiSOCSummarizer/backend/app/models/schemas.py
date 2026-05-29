from __future__ import annotations 
from typing import Any, Optional 
from pydantic import BaseModel, Field 


class SummarizeRequest(BaseModel):
    incident_json: dict[str, Any] = Field(
        ..., description="Raw incident JSON object to analyse"
    )

class ExtractedContext(BaseModel):
    incident_name: str = ""
    severity: str = ""
    timestamps: list[str] = Field(default_factory=list)
    source_ips: list[str] = Field(default_factory=list)
    destination_ips: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)
    hashes: list[str] = Field(default_factory=list)
    usernames: list[str] = Field(default_factory=list)
    hostnamse: list[str] = Field(default_factory=list)
    alert_names: list[str] = Field(default_factory=list)
    detection_rules: list[str] = Field(default_factory=list)
    enrichment_results: list[str] = Field(default_factory=list)
    related_events: list[str] = Field(default_factory=list)
    remediation_actions: list[str] = Field(default_factory=list)
    raw_text : str = ""


class ThreatIntelAssessment(BaseModel):
    suspicious_indicators: list[str] = Field(default_factory=list)
    known_bad_signals: list[str] = Field(default_factory=list)
    malware_references: list[str] = Field(default_factory=list)
    c2_indicators: list[str] = Field(default_factory=list)
    phishing_indicators: list[str] = Field(default_factory=list)
    dga_like_domains: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    assessment_text: str = ""


class SOCAnalystOutput(BaseModel):
    attack_narrative : str = ""
    affected_users: list[str] = Field(default_factory=list)
    affected_hosts: list[str] = Field(default_factory=list)
    scope: str = ""
    timeline: str = ""
    confirmed_facts: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class DetectionResponseOutput(BaseModel):
    detection_findings: list[str] = Field(default_factory=list)
    immediate_actions: list[str] = Field(default_factory=list)
    investigation_actions: list[str] = Field(default_factory=list)
    containment_actions: list[str] = Field(default_factory=list)
    remediation_actions: list[str] = Field(default_factory=list) 


class BestPracticesOutput(BaseModel):
    prevention_steps: list[str] = Field(default_factory=list)
    hardening_steps: list[str] = Field(default_factory=list)

class ConflictReviewOutput(BaseModel):
    conflicts_found: list[str] = Field(default_factory=list)
    weak_claims: list[str] = Field(default_factory=list)
    removed_claims: list[str] = Field(default_factory=list)
    review_notes: str = ""


    