import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.database import Base, engine, SessionLocal
from app.services.recommendation_service import seed_providers_if_empty

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_providers_if_empty(db)
    finally:
        db.close()
    yield

def test_health_check_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["supported_conditions"] == 41
    assert data["supported_symptoms"] >= 130

def test_symptoms_list_endpoint():
    response = client.get("/api/v1/assessments/symptoms/list")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 130
    assert len(data["symptoms"]) >= 130

def test_anonymous_triage_assessment():
    payload = {
        "symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"],
        "duration_days": 3,
        "age_band": "20-29",
        "sex": "F"
    }
    response = client.post("/api/v1/assessments", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert len(data["predictions"]) == 3
    assert data["predictions"][0]["condition"] == "Fungal infection"
    assert "urgency" in data
    assert "disclaimer" in data

def test_emergency_triage_assessment():
    payload = {
        "symptoms": ["chest_pain", "breathlessness", "sweating"],
        "duration_days": 1,
        "age_band": "50-59",
        "sex": "M"
    }
    response = client.post("/api/v1/assessments", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["urgency"] == "emergency"
    assert data["red_flag_triggered"] is True
    assert data["urgency_color"] == "red"

def test_auth_and_patient_lifecycle():
    email = "jane.doe@example.com"
    password = "SecurePassword123!"
    
    # 1. Register (or login if exists)
    reg_resp = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Dr. Jane Doe"
    })
    if reg_resp.status_code == 400:
        login_resp = client.post("/api/v1/auth/login", json={
            "email": email,
            "password": password
        })
        token = login_resp.json()["access_token"]
    else:
        assert reg_resp.status_code == 201
        token = reg_resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Login verification
    login_resp = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

    # 3. Get /auth/me
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == email

    # 4. Save Patient Profile (Encrypted PHI)
    profile_payload = {
        "age_band": "30-39",
        "sex": "F",
        "medical_history": "Mild childhood asthma",
        "allergies": "Sulfa drugs",
        "current_medications": "Albuterol inhaler as needed"
    }
    prof_resp = client.put("/api/v1/patient/profile", json=profile_payload, headers=headers)
    assert prof_resp.status_code == 200
    prof_data = prof_resp.json()
    assert prof_data["allergies"] == "Sulfa drugs"

    # 5. Perform Authenticated Assessment
    assess_resp = client.post("/api/v1/assessments", json={
        "symptoms": ["chills", "vomiting", "high_fever", "headache"],
        "duration_days": 4,
        "age_band": "30-39"
    }, headers=headers)
    assert assess_resp.status_code == 200

    # 6. Retrieve History
    hist_resp = client.get("/api/v1/assessments", headers=headers)
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()) >= 1

    # 7. GDPR Right to Deletion
    del_resp = client.delete("/api/v1/patient/data", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "success"

    # Verify history is wiped
    hist_after = client.get("/api/v1/assessments", headers=headers)
    assert hist_after.status_code == 200
    assert len(hist_after.json()) == 0

def test_nearby_recommendations():
    response = client.get("/api/v1/recommendations/nearby?lat=33.6844&lon=73.0479&specialty=Cardiology&radius_km=30")
    assert response.status_code == 200
    providers = response.json()
    assert len(providers) > 0
    assert "name" in providers[0]
    assert "distance_km" in providers[0]
    assert "recommendation_score" in providers[0]
