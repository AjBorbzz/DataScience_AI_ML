from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, Any
import uuid
import time
import logging
from datetime import datetime

from app.models.email import EmailAnalysisRequest, EmailAnalysisResponse
from app.models.detection import ThreatIndicators
from app.services.ml_service import ml_service
from app.services.threat_intel import threat_intel_service
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analyze", response_model=EmailAnalysisResponse)
async def analyze_email(
    request: EmailAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """Analyze email for phishing indicators"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        # Get ML prediction
        prediction = ml_service.predict_phishing(request.email_content)
        
        # Get threat indicators
        threat_indicators = await threat_intel_service.analyze_threats(
            request.email_content,
            request.analysis_options
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare response
        response = EmailAnalysisResponse(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            prediction=prediction,
            threat_indicators=threat_indicators,
            analysis_metadata={
                "user_id": current_user.get("sub"),
                "analysis_options": request.analysis_options,
                "email_size": len(request.email_content.body)
            },
            processing_time=processing_time
        )
        
        # Log analysis in background
        background_tasks.add_task(
            log_analysis,
            request_id,
            prediction.is_phishing,
            prediction.confidence_score
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing email {request_id}: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@router.post("/batch-analyze")
async def batch_analyze_emails(
    requests: list[EmailAnalysisRequest],
    current_user: Dict = Depends(get_current_user)
):
    """Analyze multiple emails in batch"""
    if len(requests) > 100:
        raise HTTPException(status_code=400, detail="Batch size too large")
    
    results = []
    for req in requests:
        try:
            prediction = ml_service.predict_phishing(req.email_content)
            threat_indicators = await threat_intel_service.analyze_threats(
                req.email_content,
                req.analysis_options
            )
            
            results.append({
                "prediction": prediction,
                "threat_indicators": threat_indicators
            })
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            results.append({"error": "Analysis failed"})
    
    return {"results": results, "total_processed": len(results)}

async def log_analysis(request_id: str, is_phishing: bool, confidence: float):
    """Background task to log analysis results"""
    logger.info(f"Analysis {request_id}: phishing={is_phishing}, confidence={confidence}")