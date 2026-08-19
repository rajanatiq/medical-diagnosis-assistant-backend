from typing import List, Dict, Any, Tuple

# Red flag symptoms and high-risk combinations
CRITICAL_SYMPTOMS = {
    "chest_pain": "Chest pain may indicate cardiac distress or severe pulmonary condition.",
    "breathlessness": "Severe shortness of breath requires prompt medical attention.",
    "altered_sensorium": "Confusion or altered mental state requires urgent evaluation.",
    "acute_liver_failure": "Acute organ failure requires immediate emergency hospital care.",
    "high_fever": "Persistent high fever accompanied by other symptoms.",
    "loss_of_balance": "Sudden loss of balance can indicate neurological involvement."
}

def evaluate_triage(
    symptoms: List[str],
    duration_days: int,
    top_disease_probability: float
) -> Tuple[str, str, str, str, bool, str, float, List[str]]:
    """
    Evaluates urgency, red flags, plain English advice, and composite severity.
    Returns:
      (urgency_key, urgency_label, urgency_color, urgency_description, red_flag_triggered, red_flag_reason, severity_score, advice_list)
    """
    symptoms_set = {s.strip().lower().replace(" ", "_") for s in symptoms}
    
    red_flag_triggered = False
    red_flag_reasons = []

    # Check emergency red flags
    if "chest_pain" in symptoms_set and "breathlessness" in symptoms_set:
        red_flag_triggered = True
        red_flag_reasons.append("Combined chest pain and breathing difficulty.")

    for crit, reason in CRITICAL_SYMPTOMS.items():
        if crit in symptoms_set:
            if crit in ["altered_sensorium", "acute_liver_failure"]:
                red_flag_triggered = True
                red_flag_reasons.append(reason)

    # Calculate severity score (0 to 10 scale)
    base_severity = min(len(symptoms) * 1.5, 6.0)
    duration_factor = min(duration_days * 0.4, 2.5)
    severity_score = round(min(base_severity + duration_factor + (2.0 if red_flag_triggered else 0.0), 10.0), 1)

    # Determine Urgency
    if red_flag_triggered or severity_score >= 8.0:
        urgency = "emergency"
        urgency_label = "Emergency Care Needed"
        urgency_color = "#ef4444"  # Red
        urgency_desc = "Your symptoms suggest an urgent medical situation. Please seek immediate medical care or visit the nearest emergency department."
        advice = [
            "Do not wait or drive yourself if feeling faint or in severe pain.",
            "Go to the nearest hospital emergency room immediately.",
            "Bring your current medications and emergency contact information."
        ]
    elif severity_score >= 5.0 or duration_days >= 5:
        urgency = "see_doctor_soon"
        urgency_label = "Doctor Visit Recommended Soon"
        urgency_color = "#f59e0b"  # Amber / Orange
        urgency_desc = "Your symptoms should be evaluated by a healthcare professional within 24 to 48 hours to prevent complications."
        advice = [
            "Book an appointment with a doctor or visit an outpatient clinic soon.",
            "Keep track of any changes or worsening in your symptoms.",
            "Stay well hydrated and get plenty of rest."
        ]
    elif severity_score >= 3.0:
        urgency = "routine_care"
        urgency_label = "Routine Consultation"
        urgency_color = "#3b82f6"  # Blue
        urgency_desc = "These symptoms can usually be checked during a normal clinic visit or telehealth consultation if they do not improve."
        advice = [
            "Schedule a standard check-up with a general physician if symptoms persist.",
            "Avoid strenuous physical exertion.",
            "Eat light, nutritious meals and drink warm fluids."
        ]
    else:
        urgency = "self_care"
        urgency_label = "Mild Symptoms / Self Care"
        urgency_color = "#10b981"  # Emerald Green
        urgency_desc = "Your reported symptoms appear mild. Rest, hydration, and monitoring at home are recommended."
        advice = [
            "Get sufficient sleep and drink plenty of water.",
            "Monitor yourself over the next 48 hours.",
            "Consult a doctor if symptoms become more severe or new symptoms appear."
        ]

    reason_str = "; ".join(red_flag_reasons) if red_flag_reasons else None
    return urgency, urgency_label, urgency_color, urgency_desc, red_flag_triggered, reason_str, severity_score, advice
