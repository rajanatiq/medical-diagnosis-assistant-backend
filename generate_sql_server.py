import os
import joblib
import json

bundle_path = r"C:\Users\mq202\PycharmProjects\medical-diagnosis-assistant-backend\app\ml\artifacts\model_v1.joblib"
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

# Generate SQL Server T-SQL Script
sql_lines = []
sql_lines.append("-- ============================================================================")
sql_lines.append("-- AegisMed: Medical Diagnosis & Triage Assistant")
sql_lines.append("-- Microsoft SQL Server (T-SQL) Database Schema & Complete Seed Script")
sql_lines.append("-- Database Name: medical_diagnosis_assistant")
sql_lines.append("-- ============================================================================")
sql_lines.append("USE master;")
sql_lines.append("GO")
sql_lines.append("")
sql_lines.append("IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'medical_diagnosis_assistant')")
sql_lines.append("BEGIN")
sql_lines.append("    CREATE DATABASE medical_diagnosis_assistant;")
sql_lines.append("END")
sql_lines.append("GO")
sql_lines.append("")
sql_lines.append("USE medical_diagnosis_assistant;")
sql_lines.append("GO")
sql_lines.append("")

# Table: symptoms
sql_lines.append("-- ============================================================================")
sql_lines.append("-- TABLE 1: symptoms (All 131 Clinical Symptoms Catalog)")
sql_lines.append("-- ============================================================================")
sql_lines.append("IF OBJECT_ID(N'dbo.symptoms', N'U') IS NULL")
sql_lines.append("BEGIN")
sql_lines.append("    CREATE TABLE dbo.symptoms (")
sql_lines.append("        id INT IDENTITY(1,1) PRIMARY KEY,")
sql_lines.append("        code NVARCHAR(100) NOT NULL UNIQUE,")
sql_lines.append("        label NVARCHAR(255) NOT NULL,")
sql_lines.append("        severity_weight INT NOT NULL DEFAULT 3,")
sql_lines.append("        category NVARCHAR(100) NOT NULL DEFAULT 'General',")
sql_lines.append("        is_critical BIT NOT NULL DEFAULT 0,")
sql_lines.append("        created_at DATETIME2 DEFAULT GETDATE()")
sql_lines.append("    );")
sql_lines.append("    CREATE NONCLUSTERED INDEX idx_symptoms_code ON dbo.symptoms(code);")
sql_lines.append("    CREATE NONCLUSTERED INDEX idx_symptoms_category ON dbo.symptoms(category);")
sql_lines.append("END")
sql_lines.append("GO")
sql_lines.append("")

# Table: diseases
sql_lines.append("-- ============================================================================")
sql_lines.append("-- TABLE 2: diseases (41 Supported Conditions, Specialties & Precautions)")
sql_lines.append("-- ============================================================================")
sql_lines.append("IF OBJECT_ID(N'dbo.diseases', N'U') IS NULL")
sql_lines.append("BEGIN")
sql_lines.append("    CREATE TABLE dbo.diseases (")
sql_lines.append("        id INT IDENTITY(1,1) PRIMARY KEY,")
sql_lines.append("        name NVARCHAR(255) NOT NULL UNIQUE,")
sql_lines.append("        specialty NVARCHAR(100) NOT NULL,")
sql_lines.append("        description NVARCHAR(MAX) NULL,")
sql_lines.append("        precaution_1 NVARCHAR(255) NULL,")
sql_lines.append("        precaution_2 NVARCHAR(255) NULL,")
sql_lines.append("        precaution_3 NVARCHAR(255) NULL,")
sql_lines.append("        precaution_4 NVARCHAR(255) NULL,")
sql_lines.append("        created_at DATETIME2 DEFAULT GETDATE()")
sql_lines.append("    );")
sql_lines.append("    CREATE NONCLUSTERED INDEX idx_diseases_name ON dbo.diseases(name);")
sql_lines.append("    CREATE NONCLUSTERED INDEX idx_diseases_specialty ON dbo.diseases(specialty);")
sql_lines.append("END")
sql_lines.append("GO")
sql_lines.append("")

# Table: users
sql_lines.append("-- ============================================================================")
sql_lines.append("-- TABLE 3: users (User Authentication & Accounts)")
sql_lines.append("-- ============================================================================")
sql_lines.append("IF OBJECT_ID(N'dbo.users', N'U') IS NULL")
sql_lines.append("BEGIN")
sql_lines.append("    CREATE TABLE dbo.users (")
sql_lines.append("        id INT IDENTITY(1,1) PRIMARY KEY,")
sql_lines.append("        email NVARCHAR(255) NOT NULL UNIQUE,")
sql_lines.append("        hashed_password NVARCHAR(255) NOT NULL,")
sql_lines.append("        full_name NVARCHAR(255) NULL,")
sql_lines.append("        is_active INT DEFAULT 1,")
sql_lines.append("        created_at DATETIME2 DEFAULT GETDATE()")
sql_lines.append("    );")
sql_lines.append("    CREATE NONCLUSTERED INDEX idx_users_email ON dbo.users(email);")
sql_lines.append("END")
sql_lines.append("GO")
sql_lines.append("")

# Table: patient_profiles
sql_lines.append("-- ============================================================================")
sql_lines.append("-- TABLE 4: patient_profiles (Encrypted PHI Health Baseline)")
sql_lines.append("-- ============================================================================")
sql_lines.append("IF OBJECT_ID(N'dbo.patient_profiles', N'U') IS NULL")
sql_lines.append("BEGIN")
sql_lines.append("    CREATE TABLE dbo.patient_profiles (")
sql_lines.append("        id INT IDENTITY(1,1) PRIMARY KEY,")
sql_lines.append("        user_id INT NOT NULL UNIQUE FOREIGN KEY REFERENCES dbo.users(id) ON DELETE CASCADE,")
sql_lines.append("        age_band NVARCHAR(50) DEFAULT '30-39',")
sql_lines.append("        sex NVARCHAR(20) DEFAULT 'Other',")
sql_lines.append("        encrypted_medical_history NVARCHAR(MAX) NULL,")
sql_lines.append("        encrypted_allergies NVARCHAR(MAX) NULL,")
sql_lines.append("        encrypted_current_medications NVARCHAR(MAX) NULL,")
sql_lines.append("        created_at DATETIME2 DEFAULT GETDATE(),")
sql_lines.append("        updated_at DATETIME2 DEFAULT GETDATE()")
sql_lines.append("    );")
sql_lines.append("END")
sql_lines.append("GO")
sql_lines.append("")

# Table: assessments
sql_lines.append("-- ============================================================================")
sql_lines.append("-- TABLE 5: assessments (Triage Assessments & Top-3 Probabilities)")
sql_lines.append("-- ============================================================================")
sql_lines.append("IF OBJECT_ID(N'dbo.assessments', N'U') IS NULL")
sql_lines.append("BEGIN")
sql_lines.append("    CREATE TABLE dbo.assessments (")
sql_lines.append("        id INT IDENTITY(1,1) PRIMARY KEY,")
sql_lines.append("        user_id INT NULL FOREIGN KEY REFERENCES dbo.users(id) ON DELETE CASCADE,")
sql_lines.append("        session_id NVARCHAR(100) NULL,")
sql_lines.append("        symptoms_json NVARCHAR(MAX) NOT NULL,")
sql_lines.append("        duration_days INT DEFAULT 1,")
sql_lines.append("        age_band NVARCHAR(50) NULL,")
sql_lines.append("        sex NVARCHAR(20) NULL,")
sql_lines.append("        model_version NVARCHAR(50) DEFAULT 'v1.0.0',")
sql_lines.append("        predictions_json NVARCHAR(MAX) NOT NULL,")
sql_lines.append("        urgency NVARCHAR(50) NOT NULL,")
sql_lines.append("        red_flag_triggered BIT DEFAULT 0,")
sql_lines.append("        red_flag_reason NVARCHAR(255) NULL,")
sql_lines.append("        composite_severity FLOAT DEFAULT 0.0,")
sql_lines.append("        created_at DATETIME2 DEFAULT GETDATE()")
sql_lines.append("    );")
sql_lines.append("    CREATE NONCLUSTERED INDEX idx_assessments_user ON dbo.assessments(user_id);")
sql_lines.append("    CREATE NONCLUSTERED INDEX idx_assessments_urgency ON dbo.assessments(urgency);")
sql_lines.append("END")
sql_lines.append("GO")
sql_lines.append("")

# Table: healthcare_providers
sql_lines.append("-- ============================================================================")
sql_lines.append("-- TABLE 6: healthcare_providers (Geospatial Hospital & Doctor Registry)")
sql_lines.append("-- ============================================================================")
sql_lines.append("IF OBJECT_ID(N'dbo.healthcare_providers', N'U') IS NULL")
sql_lines.append("BEGIN")
sql_lines.append("    CREATE TABLE dbo.healthcare_providers (")
sql_lines.append("        id INT IDENTITY(1,1) PRIMARY KEY,")
sql_lines.append("        name NVARCHAR(255) NOT NULL,")
sql_lines.append("        facility_type NVARCHAR(100) DEFAULT 'Clinic',")
sql_lines.append("        specialty NVARCHAR(100) NOT NULL,")
sql_lines.append("        latitude FLOAT NOT NULL,")
sql_lines.append("        longitude FLOAT NOT NULL,")
sql_lines.append("        address NVARCHAR(255) NOT NULL,")
sql_lines.append("        city NVARCHAR(100) DEFAULT 'Islamabad',")
sql_lines.append("        phone NVARCHAR(50) NULL,")
sql_lines.append("        emergency_capable BIT DEFAULT 0,")
sql_lines.append("        rating FLOAT DEFAULT 4.5,")
sql_lines.append("        hours NVARCHAR(100) DEFAULT '24/7 Open'")
sql_lines.append("    );")
sql_lines.append("    CREATE NONCLUSTERED INDEX idx_providers_specialty ON dbo.healthcare_providers(specialty);")
sql_lines.append("END")
sql_lines.append("GO")
sql_lines.append("")

# Table: audit_logs
sql_lines.append("-- ============================================================================")
sql_lines.append("-- TABLE 7: audit_logs (Privacy Audit Trail with Hashed IPs)")
sql_lines.append("-- ============================================================================")
sql_lines.append("IF OBJECT_ID(N'dbo.audit_logs', N'U') IS NULL")
sql_lines.append("BEGIN")
sql_lines.append("    CREATE TABLE dbo.audit_logs (")
sql_lines.append("        id INT IDENTITY(1,1) PRIMARY KEY,")
sql_lines.append("        user_id INT NULL,")
sql_lines.append("        action NVARCHAR(100) NOT NULL,")
sql_lines.append("        resource_type NVARCHAR(50) NOT NULL,")
sql_lines.append("        resource_id NVARCHAR(100) NULL,")
sql_lines.append("        ip_hash NVARCHAR(64) NOT NULL,")
sql_lines.append("        timestamp DATETIME2 DEFAULT GETDATE()")
sql_lines.append("    );")
sql_lines.append("END")
sql_lines.append("GO")
sql_lines.append("")

# SEED DATA: Symptoms (All 131)
sql_lines.append("-- ============================================================================")
sql_lines.append("-- SEED DATA: 131 Symptoms")
sql_lines.append("-- ============================================================================")
sql_lines.append("IF NOT EXISTS (SELECT 1 FROM dbo.symptoms)")
sql_lines.append("BEGIN")
sql_lines.append("    INSERT INTO dbo.symptoms (code, label, severity_weight, category, is_critical) VALUES")

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

sql_lines.append(",\n".join(sym_values) + ";")
sql_lines.append("END")
sql_lines.append("GO")
sql_lines.append("")

# SEED DATA: Diseases (All 41)
sql_lines.append("-- ============================================================================")
sql_lines.append("-- SEED DATA: 41 Diseases with Descriptions & Precautions")
sql_lines.append("-- ============================================================================")
sql_lines.append("IF NOT EXISTS (SELECT 1 FROM dbo.diseases)")
sql_lines.append("BEGIN")
sql_lines.append("    INSERT INTO dbo.diseases (name, specialty, description, precaution_1, precaution_2, precaution_3, precaution_4) VALUES")

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

sql_lines.append(",\n".join(disease_values) + ";")
sql_lines.append("END")
sql_lines.append("GO")
sql_lines.append("")

# SEED DATA: Providers
sql_lines.append("-- ============================================================================")
sql_lines.append("-- SEED DATA: Healthcare Providers")
sql_lines.append("-- ============================================================================")
sql_lines.append("IF NOT EXISTS (SELECT 1 FROM dbo.healthcare_providers)")
sql_lines.append("BEGIN")
sql_lines.append("    INSERT INTO dbo.healthcare_providers (name, facility_type, specialty, latitude, longitude, address, city, phone, emergency_capable, rating, hours) VALUES")
sql_lines.append("    (N'Central Emergency & Trauma Hospital', N'Hospital', N'Emergency / General Medicine', 33.6844, 73.0479, N'Jinnah Avenue, Sector G-8', N'Islamabad', N'+92 51 9261170', 1, 4.8, N'24/7 Open'),")
sql_lines.append("    (N'St. Jude Heart & Vascular Institute', N'Specialist Hospital', N'Cardiology', 33.6931, 73.0685, N'Health Avenue, Blue Area', N'Islamabad', N'+92 51 8440022', 1, 4.9, N'24/7 Open'),")
sql_lines.append("    (N'City Pulmonology & Chest Clinic', N'Clinic', N'Pulmonology', 33.7012, 73.0521, N'Plaza 14, F-7 Markaz', N'Islamabad', N'+92 51 2654321', 0, 4.7, N'9:00 AM - 7:00 PM'),")
sql_lines.append("    (N'Apex Gastroenterology & Liver Center', N'Specialist Clinic', N'Gastroenterology', 33.7150, 73.0380, N'Margalla Road, F-8/3', N'Islamabad', N'+92 51 2259988', 0, 4.6, N'8:30 AM - 6:00 PM'),")
sql_lines.append("    (N'DermaCare Skin & Laser Institute', N'Clinic', N'Dermatology', 33.7220, 73.0610, N'Executive Complex, F-6 Markaz', N'Islamabad', N'+92 51 2821144', 0, 4.8, N'10:00 AM - 8:00 PM'),")
sql_lines.append("    (N'NeuroSpine Advanced Hospital', N'Hospital', N'Neurology', 33.6650, 73.0210, N'I-8 Center, Sector I-8', N'Islamabad', N'+92 51 4432100', 1, 4.7, N'24/7 Open'),")
sql_lines.append("    (N'Endocrine & Diabetes Care Center', N'Clinic', N'Endocrinology', 33.6780, 73.0720, N'Commercial Block, G-9 Markaz', N'Islamabad', N'+92 51 2267711', 0, 4.5, N'9:00 AM - 5:00 PM'),")
sql_lines.append("    (N'Hope Community Health Center', N'Clinic', N'General Practice', 33.6520, 73.0850, N'Main Service Road, I-10', N'Islamabad', N'+92 51 4445566', 0, 4.4, N'8:00 AM - 10:00 PM'),")
sql_lines.append("    (N'Metro General Hospital', N'Hospital', N'General Medicine', 33.6410, 73.0420, N'Peshawar Road, H-13', N'Rawalpindi / Islamabad', N'+92 51 5567890', 1, 4.6, N'24/7 Open'),")
sql_lines.append("    (N'Arthritis & Rheumatology Clinic', N'Clinic', N'Rheumatology', 33.7310, 73.0750, N'Sector E-7 Medical Complex', N'Islamabad', N'+92 51 2618822', 0, 4.7, N'9:00 AM - 6:00 PM');")
sql_lines.append("END")
sql_lines.append("GO")

target_file = r"C:\Users\mq202\PycharmProjects\medical-diagnosis-assistant-backend\data\sql_server_schema.sql"
with open(target_file, "w", encoding="utf-8") as f:
    f.write("\n".join(sql_lines))

print(f"Generated SQL Server T-SQL script with {len(symptoms)} symptoms and {len(diseases)} diseases at: {target_file}")
