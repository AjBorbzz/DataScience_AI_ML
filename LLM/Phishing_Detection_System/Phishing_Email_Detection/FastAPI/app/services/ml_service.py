import joblib
import numpy as np
from typing import Dict, Any, Tuple
import logging
from pathlib import Path

from app.core.config import settings
from app.models.email import EmailContent, PhishingPrediction
from app.utils.email_utils import extract_features

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        self.model = None
        self.feature_extractor = None
        self.model_version = "1.0.0"
        self.load_model()
    
    def load_model(self):
        """Load the trained ML model"""
        try:
            model_path = Path(settings.MODEL_PATH)
            if model_path.exists():
                self.model = joblib.load(model_path)
                logger.info(f"Model loaded from {model_path}")
            else:
                logger.warning(f"Model file not found at {model_path}")
                # Load a dummy model for development
                self._load_dummy_model()
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self._load_dummy_model()
    
    def _load_dummy_model(self):
        """Load a dummy model for development/testing"""
        from sklearn.ensemble import RandomForestClassifier
        self.model = RandomForestClassifier()
        # Fit with dummy data
        X_dummy = np.random.rand(100, 10)
        y_dummy = np.random.randint(0, 2, 100)
        self.model.fit(X_dummy, y_dummy)
        logger.info("Dummy model loaded for development")
    
    def predict_phishing(self, email_content: EmailContent) -> PhishingPrediction:
        """Predict if email is phishing"""
        try:
            # Extract features from email
            features = self._extract_features(email_content)
            
            # Make prediction
            prediction_proba = self.model.predict_proba([features])[0]
            is_phishing = prediction_proba[1] > settings.CONFIDENCE_THRESHOLD
            confidence_score = float(prediction_proba[1])
            
            # Determine risk level
            risk_level = self._determine_risk_level(confidence_score)
            
            return PhishingPrediction(
                is_phishing=is_phishing,
                confidence_score=confidence_score,
                risk_level=risk_level,
                model_version=self.model_version
            )
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            # Return safe default
            return PhishingPrediction(
                is_phishing=True,
                confidence_score=0.5,
                risk_level="MEDIUM",
                model_version=self.model_version
            )
    
    def _extract_features(self, email_content: EmailContent) -> np.ndarray:
        """Extract features from email content"""
        # This is a simplified feature extraction
        # In production, you'd have more sophisticated feature engineering
        features = []
        
        # Text-based features
        features.append(len(email_content.subject))
        features.append(len(email_content.body))
        features.append(email_content.body.count('http'))
        features.append(email_content.body.count('click'))
        features.append(email_content.body.count('urgent'))
        features.append(len(email_content.recipient))
        features.append(len(email_content.attachments) if email_content.attachments else 0)
        
        # Add more features to make it 10 (matching dummy model)
        features.extend([0.0] * (10 - len(features)))
        
        return np.array(features[:10])
    
    def _determine_risk_level(self, confidence_score: float) -> str:
        """Determine risk level based on confidence score"""
        if confidence_score >= 0.9:
            return "CRITICAL"
        elif confidence_score >= 0.7:
            return "HIGH"
        elif confidence_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"

# Global ML service instance
ml_service = MLService()