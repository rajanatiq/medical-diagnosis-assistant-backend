import os
import joblib

data_dir = r"C:\Users\mq202\PycharmProjects\medical-diagnosis-assistant-backend\data"
bundle_path = r"C:\Users\mq202\PycharmProjects\medical-diagnosis-assistant-backend\app\ml\artifacts\model_v1.joblib"

# 1. Remove old sql files
for old_file in ["database_schema.sql", "sql_server_schema.sql"]:
    p = os.path.join(data_dir, old_file)
    if os.path.exists(p):
        os.remove(p)
        print(f"Deleted old file: {old_file}")

bundle = joblib.load(bundle_path)
symptoms = bundle["symptoms"]
severities = bundle["severities"]
diseases = bundle["diseases"]
descriptions = bundle["descriptions"]
precautions = bundle["precautions"]
specialties = bundle["specialties"]

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

lines = []
lines.append("-- ============================================================================")
lines.append("-- AegisMed: Medical Diagnosis & Triage Assistant System")
lines.append("-- FINAL ALL-IN-ONE COMPLETE DATABASE SCRIPT (SQL Server / Standard SQL)")
lines.append("-- Database Name: medical_diagnosis_assistant")
lines.append("-- ============================================================================")
lines.append("")
lines.append("USE master;")
lines.append("GO")
lines.append("")
lines.append("IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'medical_diagnosis_assistant')")
lines.append("BEGIN")
lines.append("    CREATE DATABASE medical_diagnosis_assistant;")
lines.append("END")
lines.append("GO")
lines.append("")
lines.append("USE medical_diagnosis_assistant;")
lines.append("GO")
lines.append("")

# Table: users
lines.append("-- ============================================================================")
lines.append("-- TABLE 1: users (User Authentication, Roles & Security)")
lines.append("-- ============================================================================")
lines.append("IF OBJECT_ID(N'dbo.users', N'U') IS NULL")
lines.append("BEGIN")
lines.append("    CREATE TABLE dbo.users (")
lines.append("        id INT IDENTITY(1,1) PRIMARY KEY,")
lines.append("        email NVARCHAR(255) NOT NULL UNIQUE,")
lines.append("        hashed_password NVARCHAR(255) NOT NULL,")
lines.append("        full_name NVARCHAR(255) NULL,")
lines.append("        is_active INT DEFAULT 1,")
lines.append("        created_at DATETIME2 DEFAULT GETDATE()")
lines.append("    );")
lines.append("    CREATE NONCLUSTERED INDEX idx_users_email ON dbo.users(email);")
lines.append("END")
lines.append("GO")
lines.append("")

# Table: patient_profiles
lines.append("-- ============================================================================")
lines.append("-- TABLE 2: patient_profiles (Encrypted Patient Baseline Health Data)")
lines.append("-- ============================================================================")
lines.append("IF OBJECT_ID(N'dbo.patient_profiles', N'U') IS NULL")
lines.append("BEGIN")
lines.append("    CREATE TABLE dbo.patient_profiles (")
lines.append("        id INT IDENTITY(1,1) PRIMARY KEY,")
lines.append("        user_id INT NOT NULL UNIQUE FOREIGN KEY REFERENCES dbo.users(id) ON DELETE CASCADE,")
lines.append("        age_band NVARCHAR(50) DEFAULT '30-39',")
lines.append("        sex NVARCHAR(20) DEFAULT 'Other',")
lines.append("        encrypted_medical_history NVARCHAR(MAX) NULL,")
lines.append("        encrypted_allergies NVARCHAR(MAX) NULL,")
lines.append("        encrypted_current_medications NVARCHAR(MAX) NULL,")
lines.append("        created_at DATETIME2 DEFAULT GETDATE(),")
lines.append("        updated_at DATETIME2 DEFAULT GETDATE()")
lines.append("    );")
lines.append("    CREATE NONCLUSTERED INDEX idx_patient_user ON dbo.patient_profiles(user_id);")
lines.append("END")
lines.append("GO")
lines.append("")

# Table: symptoms
lines.append("-- ============================================================================")
lines.append("-- TABLE 3: symptoms (All 131 Standardized Clinical Symptoms)")
lines.append("-- ============================================================================")
lines.append("IF OBJECT_ID(N'dbo.symptoms', N'U') IS NULL")
lines.append("BEGIN")
lines.append("    CREATE TABLE dbo.symptoms (")
lines.append("        id INT IDENTITY(1,1) PRIMARY KEY,")
lines.append("        code NVARCHAR(100) NOT NULL UNIQUE,")
lines.append("        label NVARCHAR(255) NOT NULL,")
lines.append("        severity_weight INT NOT NULL DEFAULT 3,")
lines.append("        category NVARCHAR(100) NOT NULL DEFAULT 'General',")
lines.append("        is_critical BIT NOT NULL DEFAULT 0,")
lines.append("        created_at DATETIME2 DEFAULT GETDATE()")
lines.append("    );")
lines.append("    CREATE NONCLUSTERED INDEX idx_symptoms_code ON dbo.symptoms(code);")
lines.append("    CREATE NONCLUSTERED INDEX idx_symptoms_category ON dbo.symptoms(category);")
lines.append("END")
lines.append("GO")
lines.append("")

# Table: diseases
lines.append("-- ============================================================================")
lines.append("-- TABLE 4: diseases (All 41 Medical Conditions, Specialties & Precautions)")
lines.append("-- ============================================================================")
lines.append("IF OBJECT_ID(N'dbo.diseases', N'U') IS NULL")
lines.append("BEGIN")
lines.append("    CREATE TABLE dbo.diseases (")
lines.append("        id INT IDENTITY(1,1) PRIMARY KEY,")
lines.append("        name NVARCHAR(255) NOT NULL UNIQUE,")
lines.append("        specialty NVARCHAR(100) NOT NULL,")
lines.append("        description NVARCHAR(MAX) NULL,")
lines.append("        precaution_1 NVARCHAR(255) NULL,")
lines.append("        precaution_2 NVARCHAR(255) NULL,")
lines.append("        precaution_3 NVARCHAR(255) NULL,")
lines.append("        precaution_4 NVARCHAR(255) NULL,")
lines.append("        created_at DATETIME2 DEFAULT GETDATE()")
lines.append("    );")
lines.append("    CREATE NONCLUSTERED INDEX idx_diseases_name ON dbo.diseases(name);")
lines.append("    CREATE NONCLUSTERED INDEX idx_diseases_specialty ON dbo.diseases(specialty);")
lines.append("END")
lines.append("GO")
lines.append("")

# Table: assessments
lines.append("-- ============================================================================")
lines.append("-- TABLE 5: assessments (Triage Assessments & Top-3 Probabilities)")
lines.append("-- ============================================================================")
lines.append("IF OBJECT_ID(N'dbo.assessments', N'U') IS NULL")
lines.append("BEGIN")
lines.append("    CREATE TABLE dbo.assessments (")
lines.append("        id INT IDENTITY(1,1) PRIMARY KEY,")
lines.append("        user_id INT NULL FOREIGN KEY REFERENCES dbo.users(id) ON DELETE CASCADE,")
lines.append("        session_id NVARCHAR(100) NULL,")
lines.append("        symptoms_json NVARCHAR(MAX) NOT NULL,")
lines.append("        duration_days INT DEFAULT 1,")
lines.append("        age_band NVARCHAR(50) NULL,")
lines.append("        sex NVARCHAR(20) NULL,")
lines.append("        model_version NVARCHAR(50) DEFAULT 'v1.0.0',")
lines.append("        predictions_json NVARCHAR(MAX) NOT NULL,")
lines.append("        urgency NVARCHAR(50) NOT NULL,")
lines.append("        red_flag_triggered BIT DEFAULT 0,")
lines.append("        red_flag_reason NVARCHAR(255) NULL,")
lines.append("        composite_severity FLOAT DEFAULT 0.0,")
lines.append("        created_at DATETIME2 DEFAULT GETDATE()")
lines.append("    );")
lines.append("    CREATE NONCLUSTERED INDEX idx_assessments_user ON dbo.assessments(user_id);")
lines.append("    CREATE NONCLUSTERED INDEX idx_assessments_urgency ON dbo.assessments(urgency);")
lines.append("END")
lines.append("GO")
lines.append("")

# Table: healthcare_providers
lines.append("-- ============================================================================")
lines.append("-- TABLE 6: healthcare_providers (Geospatial Doctor & Hospital Directory)")
lines.append("-- ============================================================================")
lines.append("IF OBJECT_ID(N'dbo.healthcare_providers', N'U') IS NULL")
lines.append("BEGIN")
lines.append("    CREATE TABLE dbo.healthcare_providers (")
lines.append("        id INT IDENTITY(1,1) PRIMARY KEY,")
lines.append("        name NVARCHAR(255) NOT NULL,")
lines.append("        facility_type NVARCHAR(100) DEFAULT 'Clinic',")
lines.append("        specialty NVARCHAR(100) NOT NULL,")
lines.append("        latitude FLOAT NOT NULL,")
lines.append("        longitude FLOAT NOT NULL,")
lines.append("        address NVARCHAR(255) NOT NULL,")
lines.append("        city NVARCHAR(100) DEFAULT 'Islamabad',")
lines.append("        phone NVARCHAR(50) NULL,")
lines.append("        emergency_capable BIT DEFAULT 0,")
lines.append("        rating FLOAT DEFAULT 4.5,")
lines.append("        hours NVARCHAR(100) DEFAULT '24/7 Open'")
lines.append("    );")
lines.append("    CREATE NONCLUSTERED INDEX idx_providers_specialty ON dbo.healthcare_providers(specialty);")
lines.append("    CREATE NONCLUSTERED INDEX idx_providers_emergency ON dbo.healthcare_providers(emergency_capable);")
lines.append("END")
lines.append("GO")
lines.append("")

# Table: audit_logs
lines.append("-- ============================================================================")
lines.append("-- TABLE 7: audit_logs (Privacy Audit Trail with Hashed IPs)")
lines.append("-- ============================================================================")
lines.append("IF OBJECT_ID(N'dbo.audit_logs', N'U') IS NULL")
lines.append("BEGIN")
lines.append("    CREATE TABLE dbo.audit_logs (")
lines.append("        id INT IDENTITY(1,1) PRIMARY KEY,")
lines.append("        user_id INT NULL,")
lines.append("        action NVARCHAR(100) NOT NULL,")
lines.append("        resource_type NVARCHAR(50) NOT NULL,")
lines.append("        resource_id NVARCHAR(100) NULL,")
lines.append("        ip_hash NVARCHAR(64) NOT NULL,")
lines.append("        timestamp DATETIME2 DEFAULT GETDATE()")
lines.append("    );")
lines.append("    CREATE NONCLUSTERED INDEX idx_audit_user ON dbo.audit_logs(user_id);")
lines.append("END")
lines.append("GO")
lines.append("")

# SEED DATA: Users & Profiles
lines.append("-- ============================================================================")
lines.append("-- SEED DATA: Default Demo User & Patient Profile")
lines.append("-- ============================================================================")
lines.append("IF NOT EXISTS (SELECT 1 FROM dbo.users WHERE email = N'patient.demo@aegismed.org')")
lines.append("BEGIN")
lines.append("    INSERT INTO dbo.users (email, hashed_password, full_name, is_active) VALUES")
lines.append("    (N'patient.demo@aegismed.org', N'$2b$12$eXAmpLeHAsheDPaSSwOrd123456789012345678901234567890123456', N'Jane Doe (Demo Patient)', 1);")
lines.append("")
lines.append("    DECLARE @new_user_id INT = SCOPE_IDENTITY();")
lines.append("    INSERT INTO dbo.patient_profiles (user_id, age_band, sex, encrypted_medical_history, encrypted_allergies, encrypted_current_medications) VALUES")
lines.append("    (@new_user_id, N'30-39', N'Female', N'gAAAAABn...EncryptedHistory', N'gAAAAABn...EncryptedAllergies', N'gAAAAABn...EncryptedMeds');")
lines.append("END")
lines.append("GO")
lines.append("")

# SEED DATA: Symptoms (All 131)
lines.append("-- ============================================================================")
lines.append("-- SEED DATA: All 131 Clinical Symptoms")
lines.append("-- ============================================================================")
lines.append("IF NOT EXISTS (SELECT 1 FROM dbo.symptoms)")
lines.append("BEGIN")
lines.append("    INSERT INTO dbo.symptoms (code, label, severity_weight, category, is_critical) VALUES")

sym_values = []
for s in symptoms:
    label = s.replace("_", " ").title()
    weight = severities.get(s, 3)
    category = categorize_symptom(s)
    is_crit = 1 if weight >= 6 else 0
    safe_code = s.replace("'", "''")
    safe_label = label.replace("'", "''")
    safe_cat = category.replace("'", "''")
    sym_values.append(f"    (N'{safe_code}', N'{safe_label}', {weight}, N'{safe_cat}', {is_crit})")

lines.append(",\n".join(sym_values) + ";")
lines.append("END")
lines.append("GO")
lines.append("")

# SEED DATA: Diseases (All 41)
lines.append("-- ============================================================================")
lines.append("-- SEED DATA: All 41 Medical Conditions, Descriptions & 4 Precautions")
lines.append("-- ============================================================================")
lines.append("IF NOT EXISTS (SELECT 1 FROM dbo.diseases)")
lines.append("BEGIN")
lines.append("    INSERT INTO dbo.diseases (name, specialty, description, precaution_1, precaution_2, precaution_3, precaution_4) VALUES")

disease_values = []
for d in diseases:
    spec = specialties.get(d, "General Practitioner")
    desc = descriptions.get(d, f"{d} is a recognized medical condition.")
    prec = precautions.get(d, ["Consult a doctor", "Rest", "Hydrate", "Monitor"])
    p1 = prec[0] if len(prec) > 0 else ""
    p2 = prec[1] if len(prec) > 1 else ""
    p3 = prec[2] if len(prec) > 2 else ""
    p4 = prec[3] if len(prec) > 3 else ""

    safe_name = d.replace("'", "''")
    safe_spec = spec.replace("'", "''")
    safe_desc = desc.replace("'", "''")
    safe_p1 = p1.replace("'", "''")
    safe_p2 = p2.replace("'", "''")
    safe_p3 = p3.replace("'", "''")
    safe_p4 = p4.replace("'", "''")

    disease_values.append(
        f"    (N'{safe_name}', N'{safe_spec}', N'{safe_desc}', N'{safe_p1}', N'{safe_p2}', N'{safe_p3}', N'{safe_p4}')"
    )

lines.append(",\n".join(disease_values) + ";")
lines.append("END")
lines.append("GO")
lines.append("")

# SEED DATA: Providers
lines.append("-- ============================================================================")
lines.append("-- SEED DATA: 10 Healthcare Facilities & Specialist Centers")
lines.append("-- ============================================================================")
lines.append("IF NOT EXISTS (SELECT 1 FROM dbo.healthcare_providers)")
lines.append("BEGIN")
lines.append("    INSERT INTO dbo.healthcare_providers (name, facility_type, specialty, latitude, longitude, address, city, phone, emergency_capable, rating, hours) VALUES")
lines.append("    (N'Central Emergency & Trauma Hospital', N'Hospital', N'Emergency / General Medicine', 33.6844, 73.0479, N'Jinnah Avenue, Sector G-8', N'Islamabad', N'+92 51 9261170', 1, 4.8, N'24/7 Open'),")
lines.append("    (N'St. Jude Heart & Vascular Institute', N'Specialist Hospital', N'Cardiology', 33.6931, 73.0685, N'Health Avenue, Blue Area', N'Islamabad', N'+92 51 8440022', 1, 4.9, N'24/7 Open'),")
lines.append("    (N'City Pulmonology & Chest Clinic', N'Clinic', N'Pulmonology', 33.7012, 73.0521, N'Plaza 14, F-7 Markaz', N'Islamabad', N'+92 51 2654321', 0, 4.7, N'9:00 AM - 7:00 PM'),")
lines.append("    (N'Apex Gastroenterology & Liver Center', N'Specialist Clinic', N'Gastroenterology', 33.7150, 73.0380, N'Margalla Road, F-8/3', N'Islamabad', N'+92 51 2259988', 0, 4.6, N'8:30 AM - 6:00 PM'),")
lines.append("    (N'DermaCare Skin & Laser Institute', N'Clinic', N'Dermatology', 33.7220, 73.0610, N'Executive Complex, F-6 Markaz', N'Islamabad', N'+92 51 2821144', 0, 4.8, N'10:00 AM - 8:00 PM'),")
lines.append("    (N'NeuroSpine Advanced Hospital', N'Hospital', N'Neurology', 33.6650, 73.0210, N'I-8 Center, Sector I-8', N'Islamabad', N'+92 51 4432100', 1, 4.7, N'24/7 Open'),")
lines.append("    (N'Endocrine & Diabetes Care Center', N'Clinic', N'Endocrinology', 33.6780, 73.0720, N'Commercial Block, G-9 Markaz', N'Islamabad', N'+92 51 2267711', 0, 4.5, N'9:00 AM - 5:00 PM'),")
lines.append("    (N'Hope Community Health Center', N'Clinic', N'General Practice', 33.6520, 73.0850, N'Main Service Road, I-10', N'Islamabad', N'+92 51 4445566', 0, 4.4, N'8:00 AM - 10:00 PM'),")
lines.append("    (N'Metro General Hospital', N'Hospital', N'General Medicine', 33.6410, 73.0420, N'Peshawar Road, H-13', N'Rawalpindi / Islamabad', N'+92 51 5567890', 1, 4.6, N'24/7 Open'),")
lines.append("    (N'Arthritis & Rheumatology Clinic', N'Clinic', N'Rheumatology', 33.7310, 73.0750, N'Sector E-7 Medical Complex', N'Islamabad', N'+92 51 2618822', 0, 4.7, N'9:00 AM - 6:00 PM');")
lines.append("END")
lines.append("GO")

final_target = os.path.join(data_dir, "medical_diagnosis_assistant.sql")
with open(final_target, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Created SINGLE FINAL SQL SCRIPT: {final_target}")
