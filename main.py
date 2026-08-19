import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base
from app.routes import api_router, direct_nlp_router
from app.ml.predictor import predictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.info")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    try:
        # Verify / Create SQL Server tables if needed
        Base.metadata.create_all(bind=engine)
        logger.info("Connected to Microsoft SQL Server database successfully.")
    except Exception as e:
        logger.warning(f"Database connection notice: {e}")

    # Ensure ML model is loaded
    if not predictor.model:
        predictor.load()
    logger.info(f"AI Clinical Predictor ready: {len(predictor.diseases)} conditions, {len(predictor.symptoms)} symptoms.")
    
    yield
    # Shutdown event
    logger.info("Medical Assistant Backend stopped.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Medical Diagnosis & Triage Assistant API with Real-Time Healthcare Geolocation and NLP Intake Parsing",
    lifespan=lifespan
)

# Enable CORS for frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API Routers under /api/v1 and /api
app.include_router(api_router)
app.include_router(direct_nlp_router)

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "database": "Microsoft SQL Server (medical_diagnosis_assistant)",
        "features": [
            "Clinical Symptom Triage ML",
            "Real-Time Healthcare Geolocation",
            "NLP Patient Input Parser (English & Urdu)",
            "GDPR / HIPAA PHI Encryption & Erasure"
        ],
        "docs": "/docs",
        "disclaimer": "This tool provides decision support and symptom triage. It does not replace a doctor."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
