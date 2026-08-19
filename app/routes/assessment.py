import json
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.assessment import Assessment
from app.models.symptom import Symptom
from app.ml.predictor import predictor
from app.services.triage_service import evaluate_triage
from app.services.auth_service import get_current_user_optional, get_current_user_required

logger = logging.getLogger("uvicorn.error")
router = APIRouter(prefix="/assessments", tags=["Assessments & Triage"])

class AssessmentInput(BaseModel):
    symptoms: List[str]
    duration_days: int = 1
    age_band: Optional[str] = "30-39"
    sex: Optional[str] = "Other"
    session_id: Optional[str] = None

@router.get("/symptoms/list")
def get_symptoms_list(db: Session = Depends(get_db)):
    """Fetch symptom list in format expected by frontend IntakeWizard"""
    try:
        db_symptoms = db.query(Symptom).order_by(Symptom.label).all()
        if db_symptoms and len(db_symptoms) > 0:
            return {
                "total": len(db_symptoms),
                "symptoms": [
                    {
                        "id": s.code,
                        "label": s.label,
                        "weight": s.severity_weight,
                        "is_critical": s.is_critical,
                        "category": s.category
                    }
                    for s in db_symptoms
                ]
            }
    except Exception:
        pass

    symptoms_out = []
    for s_code in predictor.symptoms:
        label = s_code.replace("_", " ").title()
        sev = predictor.severities.get(s_code, 3)
        is_crit = s_code in ["chest_pain", "breathlessness", "altered_sensorium", "acute_liver_failure"]
        symptoms_out.append({
            "id": s_code,
            "label": label,
            "weight": sev,
            "is_critical": is_crit,
            "category": "General"
        })
    return {"total": len(symptoms_out), "symptoms": symptoms_out}

@router.post("")
@router.post("/predict")
def run_assessment(
    payload: AssessmentInput,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    if not payload.symptoms or len(payload.symptoms) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select at least one symptom."
        )

    raw_preds = predictor.predict(payload.symptoms, top_k=3)
    predictions = [
        {
            "condition": p["disease"],
            "confidence": p["probability"],
            "specialty": p["specialty"],
            "description": p.get("description", ""),
            "precautions": p.get("precautions", [])
        }
        for p in raw_preds
    ]

    top_prob = predictions[0]["confidence"] if predictions else 50.0

    (
        urgency,
        urgency_label,
        urgency_color,
        urgency_desc,
        red_flag_triggered,
        red_flag_reason,
        composite_severity,
        advice
    ) = evaluate_triage(payload.symptoms, payload.duration_days, top_prob)

    assessment_id = None
    if current_user:
        try:
            record = Assessment(
                user_id=current_user.id,
                session_id=payload.session_id,
                symptoms_json=json.dumps(payload.symptoms),
                duration_days=payload.duration_days,
                age_band=payload.age_band,
                sex=payload.sex,
                model_version="v2.0.0",
                predictions_json=json.dumps(predictions),
                urgency=urgency,
                red_flag_triggered=red_flag_triggered,
                red_flag_reason=red_flag_reason,
                composite_severity=composite_severity
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            assessment_id = record.id
        except Exception as e:
            logger.error(f"Failed to save assessment to DB: {e}")

    return {
        "assessment_id": assessment_id,
        "urgency": urgency,
        "urgency_display": urgency_label,
        "urgency_color": urgency_color,
        "urgency_description": urgency_desc,
        "red_flag_triggered": red_flag_triggered,
        "red_flag_reason": red_flag_reason,
        "composite_severity": composite_severity,
        "predictions": predictions,
        "advice": advice,
        "model_version": "v2.0.0",
        "disclaimer": "This tool provides clinical decision support and is not a substitute for professional medical care."
    }

@router.get("")
@router.get("/history")
def get_user_history(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    assessments = (
        db.query(Assessment)
        .filter(Assessment.user_id == current_user.id)
        .order_by(Assessment.created_at.desc())
        .limit(20)
        .all()
    )

    history = []
    for a in assessments:
        try:
            syms = json.loads(a.symptoms_json) if a.symptoms_json else []
            preds = json.loads(a.predictions_json) if a.predictions_json else []
            top_c = preds[0]["condition"] if (preds and "condition" in preds[0]) else (preds[0].get("disease", "Condition") if preds else "General Check")
            top_p = preds[0].get("confidence", preds[0].get("probability", 50.0)) if preds else 50.0
        except Exception:
            syms = []
            top_c = "Assessment Check"
            top_p = 50.0

        history.append({
            "id": a.id,
            "created_at": a.created_at.isoformat() if a.created_at else "",
            "urgency": a.urgency,
            "red_flag_triggered": a.red_flag_triggered or False,
            "top_condition": top_c,
            "top_confidence": top_p,
            "symptoms_count": len(syms)
        })

    return history

@router.delete("")
def delete_all_assessments(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    deleted_count = db.query(Assessment).filter(Assessment.user_id == current_user.id).delete()
    db.commit()
    return {"status": "success", "deleted_count": deleted_count}

@router.delete("/{assessment_id}")
def delete_single_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    record = db.query(Assessment).filter(Assessment.id == assessment_id, Assessment.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    db.delete(record)
    db.commit()
    return {"status": "success", "deleted_id": assessment_id}
