from fastapi import APIRouter
from app.routes.auth import router as auth_router
from app.routes.symptoms import router as symptoms_router
from app.routes.assessment import router as assessment_router
from app.routes.nearby import router as nearby_router
from app.routes.patient import router as patient_router
from app.routes.health import router as health_router
from app.routes.nlp_routes import router as nlp_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(symptoms_router)
api_router.include_router(assessment_router)
api_router.include_router(nearby_router)
api_router.include_router(patient_router)
api_router.include_router(nlp_router)

# Also expose direct /api/nlp prefix for convenience
direct_nlp_router = APIRouter(prefix="/api")
direct_nlp_router.include_router(nlp_router)

__all__ = ["api_router", "direct_nlp_router"]
