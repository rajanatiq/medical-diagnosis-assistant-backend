from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Medical Assistant Clinical Triage API",
        "version": "2.0.0"
    }
