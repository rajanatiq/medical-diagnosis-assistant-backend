from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import defaultdict
from app.db.session import get_db
from app.models.symptom import Symptom
from app.schemas.symptom import SymptomResponse, SymptomCategoryGroup
from app.ml.predictor import predictor

router = APIRouter(prefix="/symptoms", tags=["Symptoms"])

CATEGORY_MAPPINGS = {
    "abdominal_pain": "Digestive & Stomach",
    "acidity": "Digestive & Stomach",
    "acute_liver_failure": "Digestive & Stomach",
    "vomiting": "Digestive & Stomach",
    "diarrhoea": "Digestive & Stomach",
    "constipation": "Digestive & Stomach",
    "stomach_pain": "Digestive & Stomach",
    "indigestion": "Digestive & Stomach",
    "nausea": "Digestive & Stomach",
    "loss_of_appetite": "Digestive & Stomach",
    "pain_during_bowel_movements": "Digestive & Stomach",
    "pain_in_anal_region": "Digestive & Stomach",
    "bloody_stool": "Digestive & Stomach",
    "irritation_in_anus": "Digestive & Stomach",
    "stomach_bleeding": "Digestive & Stomach",
    "distention_of_abdomen": "Digestive & Stomach",
    "swelling_of_stomach": "Digestive & Stomach",
    "passage_of_gases": "Digestive & Stomach",
    "belly_pain": "Digestive & Stomach",

    "cough": "Respiratory & Chest",
    "breathlessness": "Respiratory & Chest",
    "chest_pain": "Respiratory & Chest",
    "phlegm": "Respiratory & Chest",
    "throat_irritation": "Respiratory & Chest",
    "sinus_pressure": "Respiratory & Chest",
    "runny_nose": "Respiratory & Chest",
    "congestion": "Respiratory & Chest",
    "continuous_sneezing": "Respiratory & Chest",
    "blood_in_sputum": "Respiratory & Chest",
    "mucoid_sputum": "Respiratory & Chest",
    "rusty_sputum": "Respiratory & Chest",

    "headache": "Brain & Nervous System",
    "dizziness": "Brain & Nervous System",
    "loss_of_balance": "Brain & Nervous System",
    "altered_sensorium": "Brain & Nervous System",
    "lack_of_concentration": "Brain & Nervous System",
    "unsteadiness": "Brain & Nervous System",
    "spinning_movements": "Brain & Nervous System",
    "blurred_and_distorted_vision": "Brain & Nervous System",
    "visual_disturbances": "Brain & Nervous System",

    "joint_pain": "Bones, Joints & Muscles",
    "muscle_weakness": "Bones, Joints & Muscles",
    "stiff_neck": "Bones, Joints & Muscles",
    "swelling_joints": "Bones, Joints & Muscles",
    "movement_stiffness": "Bones, Joints & Muscles",
    "painful_walking": "Bones, Joints & Muscles",
    "muscle_pain": "Bones, Joints & Muscles",
    "knee_pain": "Bones, Joints & Muscles",
    "hip_joint_pain": "Bones, Joints & Muscles",
    "muscle_wasting": "Bones, Joints & Muscles",
    "back_pain": "Bones, Joints & Muscles",
    "cramps": "Bones, Joints & Muscles",

    "skin_rash": "Skin & Hair",
    "itching": "Skin & Hair",
    "nodal_skin_eruptions": "Skin & Hair",
    "skin_peeling": "Skin & Hair",
    "silver_like_dusting": "Skin & Hair",
    "small_dents_in_nails": "Skin & Hair",
    "inflammatory_nails": "Skin & Hair",
    "blister": "Skin & Hair",
    "red_sore_around_nose": "Skin & Hair",
    "yellow_crust_ooze": "Skin & Hair",
    "pus_filled_pimples": "Skin & Hair",
    "blackheads": "Skin & Hair",
    "scurring": "Skin & Hair",
    "yellowish_skin": "Skin & Hair",
    "bruising": "Skin & Hair",
    "brittle_nails": "Skin & Hair",

    "high_fever": "Fever & General",
    "mild_fever": "Fever & General",
    "chills": "Fever & General",
    "sweating": "Fever & General",
    "fatigue": "Fever & General",
    "lethargy": "Fever & General",
    "malaise": "Fever & General",
    "weight_loss": "Fever & General",
    "weight_gain": "Fever & General",
    "restlessness": "Fever & General"
}

@router.get("", response_model=List[SymptomResponse])
def get_all_symptoms(db: Session = Depends(get_db)):
    """Fetch all 131 clinical symptoms from SQL Server database with fallback to ML list"""
    try:
        db_symptoms = db.query(Symptom).order_by(Symptom.label).all()
        if db_symptoms and len(db_symptoms) > 0:
            return db_symptoms
    except Exception:
        pass

    # Fallback to predictor metadata
    result = []
    for i, s_code in enumerate(predictor.symptoms):
        label = s_code.replace("_", " ").title()
        category = CATEGORY_MAPPINGS.get(s_code, "General & Other")
        is_crit = s_code in ["chest_pain", "breathlessness", "altered_sensorium", "acute_liver_failure"]
        sev = predictor.severities.get(s_code, 3)
        result.append(SymptomResponse(
            id=i + 1,
            code=s_code,
            label=label,
            severity_weight=sev,
            category=category,
            is_critical=is_crit
        ))
    return result

@router.get("/by-category", response_model=List[SymptomCategoryGroup])
def get_symptoms_by_category(db: Session = Depends(get_db)):
    """Return symptoms organized neatly into body system categories for UI selector"""
    all_syms = get_all_symptoms(db)
    grouped = defaultdict(list)
    for s in all_syms:
        cat = getattr(s, "category", "General & Other") or "General & Other"
        grouped[cat].append(s)

    return [
        SymptomCategoryGroup(category=cat, symptoms=syms)
        for cat, syms in sorted(grouped.items())
    ]
