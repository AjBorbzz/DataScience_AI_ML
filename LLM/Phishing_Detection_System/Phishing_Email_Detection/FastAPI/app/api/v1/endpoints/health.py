from fastapi import APIRouter
from datetime import datetime
import psutil
import os
from services import ml_service

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "service": "phishing-detection-api"
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system metrics"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
        },
        "model": {
            "loaded": ml_service.model is not None,
            "version": ml_service.model_version
        },
        "process": {
            "pid": os.getpid(),
            "threads": psutil.Process().num_threads()
        }
    }