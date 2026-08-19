<div align="center">

# 🏥 AegisMed™ Backend API
### Enterprise AI Clinical Decision Support & Medical Triage Engine

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQL Server](https://img.shields.io/badge/Microsoft%20SQL%20Server-2025-CC292B?style=for-the-badge&logo=microsoftsqlserver&logoColor=white)](https://www.microsoft.com/sql-server)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4.0-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Security](https://img.shields.io/badge/Encryption-AES--128%20Fernet-10B981?style=for-the-badge&logo=auth0&logoColor=white)](#security--data-sovereignty)
[![License](https://img.shields.io/badge/License-Proprietary-blue?style=for-the-badge)](#)

<p align="center">
  A high-throughput, enterprise-grade Clinical Decision Support System (CDSS) backend API powered by calibrated Machine Learning, zero-dependency multilingual Fuzzy NLP (English, Roman Urdu, Urdu script), real-time OpenStreetMap healthcare geolocation, and Microsoft SQL Server.
</p>

</div>

---

## 📑 Table of Contents
- [Executive Overview](#-executive-overview)
- [System Architecture](#-system-architecture)
- [Key Core Capabilities](#-key-core-capabilities)
- [Directory Structure](#-directory-structure)
- [API Endpoints Reference](#-api-endpoints-reference)
- [Database Schema (Microsoft SQL Server)](#-database-schema-microsoft-sql-server)
- [NLP Multilingual Fuzzy Match Engine](#-nlp-multilingual-fuzzy-match-engine)
- [Machine Learning Diagnostic Inference](#-machine-learning-diagnostic-inference)
- [Security & Data Sovereignty](#-security--data-sovereignty)
- [Installation & Quick Start](#-installation--quick-start)

---

## 🌟 Executive Overview

AegisMed Backend is designed for telemedicine platforms, hospital triage departments, and clinical pre-screening applications. It bridges the gap between patient symptoms and immediate clinical decision-making by offering:
1. **Calibrated Multi-Hot Differential Diagnosis**: Probabilistic inference across 131 clinical symptoms mapped to 41 validated medical conditions.
2. **Multilingual Patient Input Extraction**: Natural language parsing in English, Roman Urdu (`khasi`, `khansi`, `kasi`, `saans phulna`, `seena dard`), and Urdu script (`کھانسی`, `بخار`).
3. **Clinical Urgency Stratification**: 4-tier risk classification (Emergency, 24h, Soon, Self-Care) with red-flag trigger detection.
4. **Real-Time Geolocation Router**: Instant lookup of nearby hospitals and specialist clinics using OpenStreetMap Overpass/Nominatim and Haversine distance.
5. **GDPR / HIPAA PHI Sovereignty**: Zero-knowledge AES-128 Fernet encryption for Protected Health Information with a 1-click right-to-erasure endpoint.

---

## 🏛️ System Architecture

```
[ CLIENT REQUEST ] (Web / Mobile / EHR)
        │
        ▼
[ FASTAPI ASGI LAYER (Uvicorn) ]
  ├── CORS Middleware & Request Throttling
  ├── JWT Auth & Token Verification
  └── Pydantic v2 Request Validation
        │
  ┌─────┴───────────────────────────────┬───────────────────────────────┐
  ▼                                     ▼                               ▼
[ NLP PARSER SERVICE ]        [ ML INFERENCE ENGINE ]       [ PLACES GEO SERVICE ]
• FuzzyWuzzy / Levenshtein    • 131 Symptom Multi-Hot       • OSM Nominatim Query
• Anatomical Root Anchors     • Calibrated Classifiers      • Bounding Box Geofilter
• English & Urdu Extraction   • Top-3 Differentials         • Haversine Distance (KM)
  │                                     │                               │
  └─────────────────────┬───────────────┴───────────────────────────────┘
                        ▼
           [ CLINICAL TRIAGE RULES ENGINE ]
           • 4-Tier Urgency Stratification
           • Red-Flag Safety Screening
           • Specialist Care Mapping
                        │
                        ▼
           [ SQLALCHEMY ORM / DB SESSION ]
                        │
                        ▼
        [ MICROSOFT SQL SERVER 2025 EXPRESS ]
        Database: medical_diagnosis_assistant
        ├── dbo.users
        ├── dbo.patient_profiles (AES-128 Encrypted)
        ├── dbo.symptoms (131 Catalog + Alternate Names)
        ├── dbo.diseases & disease_precautions
        ├── dbo.assessments (Encrypted Assessment Logs)
        └── dbo.audit_logs (SHA-256 IP Hashed)
```

---

## 📁 Directory Structure

```
medical-diagnosis-assistant-backend/
├── app/
│   ├── core/
│   │   ├── config.py              # Application settings, JWT secrets, database connection URLs
│   │   └── security.py            # Password hashing (bcrypt) & Fernet AES-128 cryptographic engine
│   ├── db/
│   │   ├── base.py                # Base metadata class for SQLAlchemy models
│   │   └── session.py             # SQL Server engine, SessionLocal factory, get_db dependency
│   ├── ml/
│   │   ├── predictor.py           # ML Model inference wrapper with calibration & multi-hot vectorizer
│   │   └── artifacts/
│   │       ├── model.joblib       # Trained calibrated machine learning diagnostic model
│   │       └── metadata.json      # Symptoms list, disease classes, specialties & precautions
│   ├── models/
│   │   ├── user.py                # User account ORM model
│   │   ├── patient.py             # Patient baseline health profile model (encrypted PHI)
│   │   ├── symptom.py             # Standardized clinical symptoms model
│   │   ├── disease.py             # Disease definitions, precautions & clinical descriptions
│   │   ├── assessment.py          # Patient triage assessment history ORM model
│   │   └── audit.py               # Security audit log model
│   ├── routes/
│   │   ├── __init__.py            # API router aggregator (mounts /api/v1 and /api)
│   │   ├── auth.py                # POST /auth/login, POST /auth/register
│   │   ├── symptoms.py            # GET /assessments/symptoms/list, categories & catalog
│   │   ├── assessment.py          # POST /assessments (Run ML diagnosis), GET history
│   │   ├── nlp_routes.py          # POST /nlp/parse-patient-input, POST /nlp/parse-and-prefill
│   │   ├── nearby.py              # GET /recommendations/nearby (OSM Geolocation)
│   │   ├── patient.py             # GET/PUT /patient/profile, DELETE /patient/data
│   │   └── health.py              # GET /health system liveness probe
│   ├── schemas/
│   │   ├── auth.py                # Pydantic schemas for auth tokens and user registration
│   │   ├── assessment.py          # Assessment intake requests and diagnostic response models
│   │   ├── nlp.py                 # NLP input/output entities (Age, Gender, Symptoms, Duration)
│   │   ├── nearby.py              # Healthcare provider and coordinate response schemas
│   │   └── patient.py             # Patient profile demographic schemas
│   └── services/
│       ├── nlp_parser.py          # Multilingual NLP Fuzzy Match Parser with Anatomical Anchors
│       ├── triage_service.py      # Diagnostic intake processing and database persistence
│       ├── rules_engine.py        # Clinical safety rules and urgency risk stratification
│       ├── places_service.py      # OpenStreetMap Nominatim live healthcare provider locator
│       └── audit_service.py       # Salted SHA-256 IP hashing and audit logging
├── data/
│   ├── dataset.csv                # Raw training symptom-disease matrix
│   ├── Symptom-severity.csv       # Clinical severity weights (1-7)
│   ├── symptom_Description.csv    # Disease educational descriptions
│   ├── symptom_precaution.csv     # Actionable precaution recommendations
│   ├── medical_diagnosis_assistant.sql # Master SQL Server schema creation script
│   └── symptoms_fuzzy_nlp_setup.sql    # Multilingual symptom variations & Urdu seeds
├── main.py                        # FastAPI application entrypoint and lifespan manager
├── requirements.txt               # Production Python dependencies
└── README.md                      # Backend technical documentation
```

---

## 🔌 API Endpoints Reference

### 1. NLP Patient Input Parser
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/nlp/parse-patient-input` | Extracts Age, Gender, Symptoms, Duration & Severity from English/Urdu text. |
| `POST` | `/api/v1/nlp/parse-and-prefill` | Extracts NLP entities and returns formatted form prefill parameters. |
| `GET` | `/api/v1/nlp/health` | Health check for NLP fuzzy matching service. |

### 2. Clinical Symptom Triage & AI Inference
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/assessments/symptoms/list` | Returns all 131 standardized symptoms with severity weights. |
| `POST` | `/api/v1/assessments` | Submits symptom vector for ML diagnostic inference and triage rating. |
| `GET` | `/api/v1/assessments` | Retrieves authenticated user's past triage timeline. |
| `DELETE` | `/api/v1/assessments/{id}` | Deletes a specific assessment record. |

### 3. Real-Time Healthcare Geolocation
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/recommendations/nearby` | Queries live hospitals/clinics within `radius_km` based on `lat` & `lon`. |

### 4. Patient Profile & GDPR Data Sovereignty
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/patient/profile` | Fetches patient's encrypted baseline profile (Age-band, Sex, History). |
| `PUT` | `/api/v1/patient/profile` | Updates and re-encrypts patient profile in SQL Server. |
| `DELETE` | `/api/v1/patient/data` | **GDPR Right to Erasure**: Permanently wipes all assessments and medical data. |

### 5. Authentication & Health
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Creates a new user account with bcrypt password hashing. |
| `POST` | `/api/v1/auth/login` | Authenticates credentials and issues JWT access token. |
| `GET` | `/api/v1/health` | Liveness check verifying SQL Server connection and ML model readiness. |

---

## 🗄️ Database Schema (Microsoft SQL Server)

All tables are created under the `medical_diagnosis_assistant` database:

```sql
-- 1. Users Table
CREATE TABLE dbo.users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    email NVARCHAR(255) NOT NULL UNIQUE,
    hashed_password NVARCHAR(255) NOT NULL,
    full_name NVARCHAR(255) NULL,
    is_active INT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE()
);

-- 2. Encrypted Patient Profiles
CREATE TABLE dbo.patient_profiles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL UNIQUE FOREIGN KEY REFERENCES dbo.users(id) ON DELETE CASCADE,
    age_band NVARCHAR(50) DEFAULT '20-29',
    sex NVARCHAR(20) DEFAULT 'Male',
    encrypted_medical_history NVARCHAR(MAX) NULL,
    encrypted_allergies NVARCHAR(MAX) NULL,
    encrypted_current_medications NVARCHAR(MAX) NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- 3. Standardized Symptoms & NLP Variations
CREATE TABLE dbo.symptoms (
    id INT IDENTITY(1,1) PRIMARY KEY,
    code NVARCHAR(100) NOT NULL UNIQUE,
    label NVARCHAR(255) NOT NULL,
    [name] NVARCHAR(255) NULL,
    alternate_names NVARCHAR(1000) NULL,
    urdu_name NVARCHAR(255) NULL,
    urdu_alternate_names NVARCHAR(1000) NULL,
    severity_weight INT NOT NULL DEFAULT 3,
    category NVARCHAR(100) NOT NULL DEFAULT 'General',
    is_critical BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 DEFAULT GETDATE()
);
```

---

## 🧠 NLP Multilingual Fuzzy Match Engine

The NLP engine (`app/services/nlp_parser.py`) uses a two-tier matching strategy:
1. **Anatomical Root Anchor Check**: Ensures symptoms with shared descriptor words (like *"pain"* or *"dard"*) are only matched if the specific anatomical body part is present (e.g. `sir dard` strictly matches `headache` and never triggers `chest_pain` or `abdominal_pain`).
2. **Levenshtein Distance & Token Set Ratio**: Tolerates typos and colloquial spellings across languages:
   - `khasi`, `khansi`, `kasi`, `kasee` $\rightarrow$ `cough`
   - `saans phulna`, `shortness of breath` $\rightarrow$ `breathlessness`
   - `seena dard`, `seene me dard` $\rightarrow$ `chest_pain`
   - `کھانسی` $\rightarrow$ `cough`
   - `بخار` $\rightarrow$ `high_fever`

---

## 🚀 Installation & Quick Start

### Prerequisites
- Python 3.11 or 3.12
- Microsoft SQL Server 2019/2022/2025 Express (`localhost\SQLEXPRESS`)
- ODBC Driver 17 or 18 for SQL Server

### 1. Clone & Setup Virtual Environment
```powershell
cd C:\Users\mq202\PycharmProjects\medical-diagnosis-assistant-backend
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
pip install fuzzywuzzy python-Levenshtein
```

### 3. Database Initialization
Execute the setup scripts in SQL Server:
```powershell
.venv\Scripts\python.exe -c "
from app.db.session import engine
from sqlalchemy import text
with open('data/symptoms_fuzzy_nlp_setup.sql', 'r', encoding='utf-8') as f:
    sql = f.read()
with engine.connect() as conn:
    for batch in sql.split('GO'):
        if batch.strip() and not batch.strip().upper().startswith('USE '):
            conn.execute(text(batch.strip()))
            conn.commit()
print('Database setup successfully executed!')
"
```

### 4. Start the FastAPI Server
```powershell
.venv\Scripts\uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
- **API Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger Documentation**: `http://127.0.0.1:8000/docs`
- **ReDoc Technical Schema**: `http://127.0.0.1:8000/redoc`

---

<div align="center">
  <sub>AegisMed™ Backend API • Built with Python & FastAPI • ISO 27001 & HIPAA Compliant Architecture</sub>
</div>
