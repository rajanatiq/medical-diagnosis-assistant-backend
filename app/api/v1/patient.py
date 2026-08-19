from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.patient import PatientProfile
from app.models.assessment import Assessment
from app.schemas.patient import PatientProfileCreate, PatientProfileResponse
from app.core.security import encrypt_phi, decrypt_phi
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/patient", tags=["Patient Profile & Privacy"])

@router.get("/profile", response_model=PatientProfileResponse)
def get_patient_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if not profile:
        return PatientProfileResponse(
            user_id=current_user.id,
            age_band="30-39",
            sex="Other",
            medical_history="",
            allergies="",
            current_medications=""
        )

    # Decrypt sensitive columns
    return PatientProfileResponse(
        user_id=current_user.id,
        age_band=profile.age_band,
        sex=profile.sex,
        medical_history=decrypt_phi(profile.encrypted_medical_history or ""),
        allergies=decrypt_phi(profile.encrypted_allergies or ""),
        current_medications=decrypt_phi(profile.encrypted_current_medications or ""),
        updated_at=profile.updated_at
    )

@router.put("/profile", response_model=PatientProfileResponse)
def update_patient_profile(
    request: Request,
    profile_in: PatientProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    
    # Encrypt sensitive PHI at application layer before persistence
    enc_history = encrypt_phi(profile_in.medical_history or "")
    enc_allergies = encrypt_phi(profile_in.allergies or "")
    enc_meds = encrypt_phi(profile_in.current_medications or "")

    if not profile:
        profile = PatientProfile(
            user_id=current_user.id,
            age_band=profile_in.age_band,
            sex=profile_in.sex,
            encrypted_medical_history=enc_history,
            encrypted_allergies=enc_allergies,
            encrypted_current_medications=enc_meds
        )
        db.add(profile)
    else:
        profile.age_band = profile_in.age_band
        profile.sex = profile_in.sex
        profile.encrypted_medical_history = enc_history
        profile.encrypted_allergies = enc_allergies
        profile.encrypted_current_medications = enc_meds

    db.commit()
    db.refresh(profile)

    log_audit_event(
        db=db,
        action="PROFILE_UPDATED",
        resource_type="PatientProfile",
        resource_id=str(profile.id),
        user_id=current_user.id,
        client_ip=request.client.host if request.client else None
    )

    return PatientProfileResponse(
        user_id=current_user.id,
        age_band=profile.age_band,
        sex=profile.sex,
        medical_history=profile_in.medical_history,
        allergies=profile_in.allergies,
        current_medications=profile_in.current_medications,
        updated_at=profile.updated_at
    )

@router.delete("/data", status_code=status.HTTP_200_OK)
def delete_all_patient_health_data(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GDPR / HIPAA Right to Erasure:
    Purges all historical assessment logs, triage records, and patient medical profile for the authenticated user.
    """
    # Delete assessments
    deleted_assessments = db.query(Assessment).filter(Assessment.user_id == current_user.id).delete()
    
    # Delete patient profile
    deleted_profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).delete()

    db.commit()

    log_audit_event(
        db=db,
        action="ALL_HEALTH_DATA_PURGED",
        resource_type="UserHealthRecords",
        resource_id=str(current_user.id),
        user_id=current_user.id,
        client_ip=request.client.host if request.client else None
    )

    return {
        "status": "success",
        "message": "All your health data, assessments, and clinical profiles have been permanently erased.",
        "assessments_purged": deleted_assessments,
        "profile_purged": deleted_profile > 0
    }
