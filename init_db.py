"""
Comprehensive Database Initialization & Seeding Script
Database: medical_diagnosis_assistant.db
Seeds all 131 symptoms, 41 diseases, healthcare providers, and demo user.
"""
import os
import joblib
from app.core.database import engine, Base, SessionLocal
from app.models import User, PatientProfile, Assessment, HealthcareProvider, AuditLog, Symptom, Disease
from app.services.recommendation_service import seed_providers_if_empty
from app.core.security import hash_password, encrypt_phi

def categorize_symptom(s: str) -> str:
    s_low = s.lower()
    if any(k in s_low for k in ["chest", "breath", "cough", "throat", "phlegm", "mucoid"]):
        return "Chest & Respiratory"
    if any(k in s_low for k in ["stomach", "abdominal", "vomit", "nausea", "diarrhoea", "constipation", "appetite", "liver", "ulcer", "digestion", "bowel", "passage_of_gases"]):
        return "Digestive & Gastrointestinal"
    if any(k in s_low for k in ["head", "dizz", "spinning", "unstead", "weakness", "coma", "vision", "sensorium", "slurred", "paralysis", "loss_of_balance"]):
        return "Neurological & Head"
    if any(k in s_low for k in ["skin", "itch", "rash", "blister", "patch", "peeling", "yellowish_skin", "bruising", "scurring", "eruption"]):
        return "Dermatology & Skin"
    if any(k in s_low for k in ["joint", "muscle", "knee", "hip", "neck", "back_pain", "stiff", "movement"]):
        return "Musculoskeletal & Joints"
    if any(k in s_low for k in ["urine", "micturition", "bladder", "urination"]):
        return "Urinary & Renal"
    return "General & Constitutional"

def seed_symptoms_and_diseases(db):
    bundle_path = os.path.join(os.path.dirname(__file__), "app", "ml", "artifacts", "model_v1.joblib")
    if not os.path.exists(bundle_path):
        print("Model bundle not found; skipping symptom/disease table seed.")
        return

    bundle = joblib.load(bundle_path)
    symptoms = bundle["symptoms"]
    severities = bundle["severities"]
    diseases = bundle["diseases"]
    descriptions = bundle["descriptions"]
    precautions = bundle["precautions"]
    specialties = bundle["specialties"]

    # 1. Seed Symptoms
    existing_syms = {s.code for s in db.query(Symptom).all()}
    added_syms = 0
    for s in symptoms:
        if s not in existing_syms:
            label = s.replace("_", " ").title()
            weight = severities.get(s, 3)
            category = categorize_symptom(s)
            is_crit = weight >= 6
            sym_obj = Symptom(
                code=s,
                label=label,
                severity_weight=weight,
                category=category,
                is_critical=is_crit
            )
            db.add(sym_obj)
            added_syms += 1

    # 2. Seed Diseases
    existing_diseases = {d.name for d in db.query(Disease).all()}
    added_diseases = 0
    for d in diseases:
        if d not in existing_diseases:
            spec = specialties.get(d, "General Practitioner")
            desc = descriptions.get(d, f"{d} is a recognized medical condition.")
            prec = precautions.get(d, ["Consult a doctor", "Rest", "Hydrate", "Monitor"])
            p1 = prec[0] if len(prec) > 0 else ""
            p2 = prec[1] if len(prec) > 1 else ""
            p3 = prec[2] if len(prec) > 2 else ""
            p4 = prec[3] if len(prec) > 3 else ""
            disease_obj = Disease(
                name=d,
                specialty=spec,
                description=desc,
                precaution_1=p1,
                precaution_2=p2,
                precaution_3=p3,
                precaution_4=p4
            )
            db.add(disease_obj)
            added_diseases += 1

    db.commit()
    print(f"      [+] Seeded {added_syms} new symptoms (Total: {db.query(Symptom).count()})")
    print(f"      [+] Seeded {added_diseases} new diseases (Total: {db.query(Disease).count()})")

def initialize_database():
    print("==================================================================")
    print("INITIALIZING DATABASE: medical_diagnosis_assistant.db")
    print("==================================================================")

    # 1. Create all tables
    print("[1/4] Creating all tables according to schema...")
    Base.metadata.create_all(bind=engine)
    print("      [+] symptoms, diseases, users, patient_profiles, assessments, healthcare_providers, audit_logs")

    db = SessionLocal()
    try:
        # 2. Seed Symptoms & Diseases
        print("[2/4] Seeding symptoms (131) and diseases (41) into database tables...")
        seed_symptoms_and_diseases(db)

        # 3. Seed Healthcare Providers
        print("[3/4] Seeding healthcare provider directory across medical specialties...")
        seed_providers_if_empty(db)

        # 4. Create Sample Demo User
        admin_email = "patient.demo@aegismed.org"
        existing = db.query(User).filter(User.email == admin_email).first()
        if not existing:
            demo_user = User(
                email=admin_email,
                hashed_password=hash_password("DemoPassword123!"),
                full_name="Jane Doe (Demo Patient)"
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)

            demo_profile = PatientProfile(
                user_id=demo_user.id,
                age_band="30-39",
                sex="Female",
                encrypted_medical_history=encrypt_phi("Mild Asthma (childhood), seasonal dust allergy"),
                encrypted_allergies=encrypt_phi("Penicillin"),
                encrypted_current_medications=encrypt_phi("Albuterol inhaler (as needed)")
            )
            db.add(demo_profile)
            db.commit()
            print("[4/4] Created sample test account: patient.demo@aegismed.org (Password: DemoPassword123!)")
        else:
            print("[4/4] Demo account already exists.")

        print("==================================================================")
        print("DATABASE FULLY INITIALIZED & SEEDED!")
        print("==================================================================")
    finally:
        db.close()

if __name__ == "__main__":
    initialize_database()
