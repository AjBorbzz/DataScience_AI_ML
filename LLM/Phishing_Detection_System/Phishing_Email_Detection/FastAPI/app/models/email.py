from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class EmailContent(BaseModel):
    subject: str
    body: str
    sender: EmailStr
    recipient: List[EmailStr]
    cc: Optional[List[EmailStr]] = []
    bcc: Optional[List[EmailStr]] = []
    headers: Optional[Dict[str, str]] = {}
    attachments: Optional[List[Dict[str, Any]]] = []
    
    @validator('body')
    def validate_body_length(cls, v):
        if len(v) > 1000000:  # 1MB text limit
            raise ValueError('Email body too large')
        return v

class EmailAnalysisRequest(BaseModel):
    email_content: EmailContent
    analysis_options: Optional[Dict[str, bool]] = {
        "check_urls": True,
        "check_attachments": True,
        "deep_analysis": False
    }

class PhishingPrediction(BaseModel):
    is_phishing: bool
    confidence_score: float
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    model_version: str

class ThreatIndicators(BaseModel):
    suspicious_urls: List[str] = []
    suspicious_domains: List[str] = []
    suspicious_attachments: List[str] = []
    suspicious_keywords: List[str] = []
    header_anomalies: List[str] = []

class EmailAnalysisResponse(BaseModel):
    request_id: str
    timestamp: datetime
    prediction: PhishingPrediction
    threat_indicators: ThreatIndicators
    analysis_metadata: Dict[str, Any]
    processing_time: float