import pytest
from app.ml.predictor import predictor

def test_symptom_catalog_loaded():
    symptoms = predictor.get_symptom_list()
    assert len(symptoms) >= 130
    assert any(s["id"] == "chest_pain" for s in symptoms)
    assert any(s["id"] == "itching" for s in symptoms)

def test_fungal_infection_prediction():
    inputs = ["itching", "skin_rash", "nodal_skin_eruptions", "dischromic_patches"]
    preds = predictor.predict_top_k(inputs, top_k=3)
    assert len(preds) == 3
    assert preds[0]["condition"] == "Fungal infection"
    assert preds[0]["confidence"] > 0.2
    assert preds[0]["specialty"] == "Dermatology"
    assert len(preds[0]["precautions"]) == 4

def test_heart_attack_prediction():
    inputs = ["chest_pain", "breathlessness", "sweating"]
    preds = predictor.predict_top_k(inputs, top_k=3)
    assert len(preds) == 3
    top_conditions = [p["condition"] for p in preds]
    assert "Heart attack" in top_conditions or "Hypertension" in top_conditions
    assert preds[0]["specialty"] in ["Cardiology", "Pulmonology"]

def test_malaria_prediction():
    inputs = ["chills", "vomiting", "high_fever", "sweating", "headache", "nausea"]
    preds = predictor.predict_top_k(inputs, top_k=3)
    assert len(preds) == 3
    assert preds[0]["condition"] == "Malaria"
    assert preds[0]["confidence"] > 0.10
