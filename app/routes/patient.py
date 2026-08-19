import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.patient import PatientProfile
from app.models.assessment import Assessment
from app.schemas.patient import PatientProfileUpdate, PatientProfileResponse
from app.services.auth_service import get_current_user_required

logger = logging.getLogger("uvicorn.error")
router = APIRouter(prefix="/patient", tags=["Patient Profile & Data Privacy"])

@router.get("/profile", response_model=PatientProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if not profile:
        profile = PatientProfile(user_id=current_user.id, age_band="30-39", sex="Other")
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return profile

@router.put("/profile", response_model=PatientProfileResponse)
def update_profile(
    payload: PatientProfileUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if not profile:
        profile = PatientProfile(user_id=current_user.id)
        db.add(profile)

    if payload.age_band is not None:
        profile.age_band = payload.age_band
    if payload.sex is not None:
        profile.sex = payload.sex
    if payload.medical_history is not None:
        profile.encrypted_medical_history = payload.medical_history
    if payload.allergies is not None:
        profile.encrypted_allergies = payload.allergies
    if payload.current_medications is not None:
        profile.encrypted_current_medications = payload.current_medications

    db.commit()
    db.refresh(profile)
    return profile

@router.delete("/data")
def delete_all_health_data(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    GDPR / HIPAA Right to Erasure:
    Permanently deletes all past triage assessments and encrypted medical profile data
    for the current user from Microsoft SQL Server database.
    """
    try:
        # 1. Delete all assessments for this user from SQL Server
        deleted_count = db.query(Assessment).filter(Assessment.user_id == current_user.id).delete()

        # 2. Reset patient profile health data
        profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
        if profile:
            profile.encrypted_medical_history = None
            profile.encrypted_allergies = None
            profile.encrypted_current_medications = None

        db.commit()
        logger.info(f"Purged {deleted_count} assessment records and profile data for user {current_user.id}")

        return {
            "status": "success",
            "message": f"Successfully and permanently deleted {deleted_count} assessment records and health data from database.",
            "deleted_records": deleted_count
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error during health data erasure for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to erase health data from database. Please try again."
        )
