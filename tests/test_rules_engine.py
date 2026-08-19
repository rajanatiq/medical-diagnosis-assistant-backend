import pytest
from app.services.rules_engine import evaluate_safety_and_urgency

def test_cardiac_emergency_rule():
    result = evaluate_safety_and_urgency(
        symptoms=["chest_pain", "breathlessness"],
        duration_days=1,
        age_band="50-59"
    )
    assert result["urgency"] == "emergency"
    assert result["red_flag_triggered"] is True
    assert result["urgency_color"] == "red"

def test_coma_emergency_rule():
    result = evaluate_safety_and_urgency(
        symptoms=["coma", "high_fever"],
        duration_days=1
    )
    assert result["urgency"] == "emergency"
    assert result["red_flag_triggered"] is True

def test_mild_symptom_self_care():
    result = evaluate_safety_and_urgency(
        symptoms=["itching"],
        duration_days=1,
        age_band="20-29"
    )
    assert result["urgency"] == "self_care"
    assert result["red_flag_triggered"] is False
    assert result["urgency_color"] == "green"

def test_moderate_symptoms_doctor_soon():
    result = evaluate_safety_and_urgency(
        symptoms=["cough", "fatigue", "headache"],
        duration_days=5,
        age_band="30-39"
    )
    assert result["urgency"] in ["see_doctor_soon", "see_doctor_within_24h"]
