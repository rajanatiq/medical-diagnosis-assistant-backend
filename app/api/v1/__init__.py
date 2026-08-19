from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.assessments import router as assessments_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.patient import router as patient_router
from app.api.v1.health import router as health_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(assessments_router)
api_router.include_router(recommendations_router)
api_router.include_router(patient_router)
