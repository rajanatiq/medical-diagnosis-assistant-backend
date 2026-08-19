from typing import List, Set, Dict, Any, Tuple
from app.ml.predictor import predictor

# High-priority red flag combinations
CRITICAL_EMERGENCY_PATTERNS = [
    {
        "name": "Cardiac / Acute Coronary Warning",
        "symptoms": {"chest_pain", "breathlessness"},
        "reason": "Chest pain combined with shortness of breath requires immediate emergency evaluation to rule out cardiac events."
    },
    {
        "name": "Altered Consciousness / Coma",
        "symptoms": {"coma"},
        "reason": "Loss of consciousness or coma is a medical emergency requiring immediate resuscitation and hospital admission."
    },
    {
        "name": "Stroke / Neurological Deficit",
        "symptoms": {"weakness_in_limbs", "altered_sensorium"},
        "reason": "Sudden weakness in limbs and altered sensorium are signs of acute neurological emergency or stroke."
    },
    {
        "name": "Acute Gastrointestinal Hemorrhage",
        "symptoms": {"stomach_bleeding"},
        "reason": "Internal stomach bleeding can lead to rapid hemodynamic instability and requires urgent hospital care."
    },
    {
        "name": "Severe Hepatic Failure",
        "symptoms": {"acute_liver_failure"},
        "reason": "Acute liver failure is a life-threatening critical condition."
    },
    {
        "name": "Severe Systemic Fluid Overload",
        "symptoms": {"fluid_overload"},
        "reason": "Severe fluid retention or overload can indicate acute heart or kidney failure."
    }
]

def clean_sym(s: str) -> str:
    return predictor.clean_symptom(s)

def evaluate_safety_and_urgency(
    symptoms: List[str],
    duration_days: int = 1,
    age_band: str = "30-39",
    top_predicted_condition: str = ""
) -> Dict[str, Any]:
    cleaned_symptoms: Set[str] = {clean_sym(s) for s in symptoms if s}
    
    # 1. Check Hardcoded Emergency Red Flags
    for rule in CRITICAL_EMERGENCY_PATTERNS:
        if rule["symptoms"].issubset(cleaned_symptoms):
            return {
                "urgency": "emergency",
                "urgency_display": "Seek Emergency Care Immediately",
                "urgency_color": "red",
                "red_flag_triggered": True,
                "red_flag_reason": rule["reason"],
                "composite_severity": 10.0
            }

    # 2. Check individual critical Weight 7 symptoms
    weight_7_present = [s for s in cleaned_symptoms if predictor.severities.get(s, 0) >= 7]
    if "chest_pain" in cleaned_symptoms:
        return {
            "urgency": "emergency",
            "urgency_display": "Seek Emergency Care Immediately",
            "urgency_color": "red",
            "red_flag_triggered": True,
            "red_flag_reason": "Severe chest pain reported.",
            "composite_severity": 9.5
        }
    
    if "coma" in cleaned_symptoms:
        return {
            "urgency": "emergency",
            "urgency_display": "Seek Emergency Care Immediately",
            "urgency_color": "red",
            "red_flag_triggered": True,
            "red_flag_reason": "Altered state of consciousness reported.",
            "composite_severity": 10.0
        }

    # 3. Calculate Composite Clinical Severity
    raw_severity = sum(predictor.severities.get(s, 3) for s in cleaned_symptoms)
    
    # Age & duration adjustment
    age_multiplier = 1.0
    if age_band in ["0-9", "60+"]:
        age_multiplier = 1.25 # High-risk demographics
    
    duration_multiplier = 1.0
    if duration_days >= 7:
        duration_multiplier = 1.2
    elif duration_days >= 14:
        duration_multiplier = 1.4

    adjusted_severity = raw_severity * age_multiplier * duration_multiplier

    # 4. Critical conditions escalation
    emergency_conditions = {"Heart attack", "Paralysis (brain hemorrhage)", "Pneumonia", "Tuberculosis"}

    if top_predicted_condition in ["Heart attack", "Paralysis (brain hemorrhage)"]:
        return {
            "urgency": "emergency",
            "urgency_display": "Seek Emergency Care Immediately",
            "urgency_color": "red",
            "red_flag_triggered": True,
            "red_flag_reason": f"Symptom profile strongly matches emergency condition: {top_predicted_condition}",
            "composite_severity": round(adjusted_severity, 2)
        }

    # 5. Stratified Urgency Tiers
    if adjusted_severity >= 25 or len(weight_7_present) >= 1 or duration_days >= 10:
        urgency = "see_doctor_within_24h"
        display = "Consult a Doctor Within 24 Hours"
        color = "orange"
    elif adjusted_severity >= 12 or duration_days >= 4:
        urgency = "see_doctor_soon"
        display = "Schedule a Doctor Appointment Soon"
        color = "yellow"
    else:
        urgency = "self_care"
        display = "Self-Care & Home Monitoring"
        color = "green"

    return {
        "urgency": urgency,
        "urgency_display": display,
        "urgency_color": color,
        "red_flag_triggered": False,
        "red_flag_reason": None,
        "composite_severity": round(adjusted_severity, 2)
    }
