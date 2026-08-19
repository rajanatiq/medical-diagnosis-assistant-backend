from fastapi import APIRouter
from app.ml.predictor import predictor

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Medical Diagnosis & Triage Assistant API",
        "model_version": predictor.model_version,
        "supported_conditions": len(predictor.diseases),
        "supported_symptoms": len(predictor.symptoms)
    }
