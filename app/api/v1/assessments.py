from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.core.database import get_db
from app.schemas.assessment import (
    AssessmentRequest,
    AssessmentResponse,
    PredictionItem,
    AssessmentHistoryItem
)
from app.services.rules_engine import evaluate_safety_and_urgency
from app.services.audit_service import log_audit_event
from app.ml.predictor import predictor
from app.models.assessment import Assessment
from app.models.user import User
from app.models.symptom import Symptom
from app.models.disease import Disease
from app.api.v1.auth import get_current_user, get_optional_current_user

router = APIRouter(prefix="/assessments", tags=["Assessments"])

@router.get("/symptoms/list")
def get_symptoms_list(db: Session = Depends(get_db)):
    """
    Returns the comprehensive list of 131 clinical symptoms loaded directly from the database table.
    """
    db_symptoms = db.query(Symptom).order_by(Symptom.label).all()
    
    if db_symptoms and len(db_symptoms) > 0:
        symptom_items = [
            {
                "id": s.code,
                "label": s.label,
                "weight": s.severity_weight,
                "category": s.category or "General"
            }
            for s in db_symptoms
        ]
    else:
        symptom_items = [
            {
                "id": s_id,
                "label": s_id.replace("_", " ").title(),
                "weight": predictor.severities.get(s_id, 3),
                "category": "General"
            }
            for s_id in predictor.symptoms
        ]

    return {
        "total": len(symptom_items),
        "symptoms": symptom_items
    }

@router.get("", response_model=List[AssessmentHistoryItem])
def get_user_assessment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns historical assessments performed by the authenticated user.
    """
    records = db.query(Assessment).filter(Assessment.user_id == current_user.id).order_by(Assessment.created_at.desc()).all()
    
    history_items = []
    for r in records:
        try:
            preds = json.loads(r.predictions_json)
            top_cond = preds[0]["condition"] if preds else "Unknown"
            top_conf = preds[0]["confidence"] if preds else 0.0
        except Exception:
            top_cond = "Unknown"
            top_conf = 0.0

        try:
            syms = json.loads(r.symptoms_json)
            sym_count = len(syms)
        except Exception:
            sym_count = 0

        history_items.append(
            AssessmentHistoryItem(
                id=r.id,
                created_at=r.created_at,
                urgency=r.urgency,
                red_flag_triggered=r.red_flag_triggered or False,
                top_condition=top_cond,
                top_confidence=top_conf,
                symptoms_count=sym_count
            )
        )

    return history_items

@router.post("", response_model=AssessmentResponse, status_code=status.HTTP_200_OK)
def create_assessment(
    assessment_in: AssessmentRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Computes calibrated condition probabilities, evaluates clinical safety red-flags,
    stores assessment in database, and logs privacy-safe audit record.
    """
    if not assessment_in.symptoms:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one symptom must be selected for triage evaluation."
        )

    # 1. Run Calibrated ML Prediction
    predictions_raw = predictor.predict_top_k(assessment_in.symptoms, top_k=3)
    top_cond = predictions_raw[0]["condition"] if predictions_raw else ""

    # 2. Run Clinical Safety Rules Engine
    safety_eval = evaluate_safety_and_urgency(
        symptoms=assessment_in.symptoms,
        duration_days=assessment_in.duration_days or 1,
        age_band=assessment_in.age_band or "30-39",
        top_predicted_condition=top_cond
    )

    final_urgency = safety_eval["urgency"]
    final_urgency_display = safety_eval["urgency_display"]
    final_urgency_color = safety_eval["urgency_color"]

    predictions = [
        PredictionItem(
            condition=p["condition"],
            confidence=p["confidence"],
            specialty=p["specialty"],
            description=p["description"],
            precautions=p["precautions"]
        )
        for p in predictions_raw
    ]

    # 3. Save to Database
    user_id = current_user.id if current_user else None
    client_ip = request.client.host if request.client else "unknown"

    db_assessment = Assessment(
        user_id=user_id,
        session_id=assessment_in.session_id or request.headers.get("X-Session-ID"),
        symptoms_json=json.dumps(assessment_in.symptoms),
        duration_days=assessment_in.duration_days,
        age_band=assessment_in.age_band,
        sex=assessment_in.sex,
        model_version=predictor.model_version,
        predictions_json=json.dumps([p.model_dump() for p in predictions]),
        urgency=final_urgency,
        red_flag_triggered=safety_eval["red_flag_triggered"],
        red_flag_reason=safety_eval["red_flag_reason"],
        composite_severity=safety_eval["composite_severity"]
    )
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)

    # 4. Audit Log (Hashed IP)
    log_audit_event(
        db=db,
        action="ASSESSMENT_PERFORMED",
        resource_type="assessment",
        resource_id=str(db_assessment.id),
        client_ip=client_ip,
        user_id=user_id
    )

    return AssessmentResponse(
        assessment_id=db_assessment.id,
        model_version=predictor.model_version,
        urgency=final_urgency,
        urgency_display=final_urgency_display,
        urgency_color=final_urgency_color,
        red_flag_triggered=safety_eval["red_flag_triggered"],
        red_flag_reason=safety_eval["red_flag_reason"],
        composite_severity=safety_eval["composite_severity"],
        predictions=predictions,
        created_at=db_assessment.created_at
    )
