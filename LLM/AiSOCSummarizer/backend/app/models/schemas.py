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