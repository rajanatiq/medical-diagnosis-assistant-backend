import os
import csv
import json
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

SPECIALTY_MAP = {
    "Fungal infection": "Dermatology",
    "Allergy": "Allergy & Immunology",
    "GERD": "Gastroenterology",
    "Chronic cholestasis": "Hepatology / Gastroenterology",
    "Drug Reaction": "Allergy / Dermatology",
    "Peptic ulcer diseae": "Gastroenterology",
    "AIDS": "Infectious Disease",
    "Diabetes": "Endocrinology",
    "Gastroenteritis": "Gastroenterology",
    "Bronchial Asthma": "Pulmonology",
    "Hypertension": "Cardiology",
    "Migraine": "Neurology",
    "Cervical spondylosis": "Orthopedics / Neurology",
    "Paralysis (brain hemorrhage)": "Neurology / Emergency",
    "Jaundice": "Hepatology",
    "Malaria": "Infectious Disease",
    "Chicken pox": "Infectious Disease / Pediatrics",
    "Dengue": "Infectious Disease",
    "Typhoid": "Infectious Disease / Internal Medicine",
    "hepatitis A": "Hepatology",
    "Hepatitis B": "Hepatology",
    "Hepatitis C": "Hepatology",
    "Hepatitis D": "Hepatology",
    "Hepatitis E": "Hepatology",
    "Alcoholic hepatitis": "Hepatology",
    "Tuberculosis": "Pulmonology / Infectious Disease",
    "Common Cold": "General Practice / ENT",
    "Pneumonia": "Pulmonology / Internal Medicine",
    "Dimorphic hemmorhoids(piles)": "Proctology / General Surgery",
    "Heart attack": "Cardiology / Emergency",
    "Varicose veins": "Vascular Surgery",
    "Hypothyroidism": "Endocrinology",
    "Hyperthyroidism": "Endocrinology",
    "Hypoglycemia": "Endocrinology",
    "Osteoarthristis": "Orthopedics / Rheumatology",
    "Arthritis": "Rheumatology",
    "(vertigo) Paroymsal  Positional Vertigo": "ENT / Neurology",
    "Acne": "Dermatology",
    "Urinary tract infection": "Urology / Nephrology",
    "Psoriasis": "Dermatology",
    "Impetigo": "Dermatology"
}

def train():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir))
    data_dir = os.path.join(base_dir, "data")
    artifacts_dir = os.path.join(current_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    dataset_csv = os.path.join(data_dir, "dataset.csv")
    desc_csv = os.path.join(data_dir, "symptom_Description.csv")
    prec_csv = os.path.join(data_dir, "symptom_precaution.csv")
    sev_csv = os.path.join(data_dir, "Symptom-severity.csv")

    descriptions = {}
    if os.path.exists(desc_csv):
        with open(desc_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for r in reader:
                if len(r) >= 2:
                    descriptions[r[0].strip()] = r[1].strip()

    precautions = {}
    if os.path.exists(prec_csv):
        with open(prec_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for r in reader:
                if len(r) >= 2:
                    prec = [p.strip().capitalize() for p in r[1:] if p and p.strip()]
                    precautions[r[0].strip()] = prec

    severities = {}
    if os.path.exists(sev_csv):
        with open(sev_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for r in reader:
                if len(r) >= 2 and r[1].strip().isdigit():
                    severities[r[0].strip().lower().replace(" ", "_")] = int(r[1].strip())

    with open(dataset_csv, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        raw_rows = [r for r in reader if r]

    all_symptoms_set = set()
    for r in raw_rows:
        for s in r[1:]:
            s_clean = s.strip().lower().replace(" ", "_")
            if s_clean:
                all_symptoms_set.add(s_clean)

    symptoms_list = sorted(list(all_symptoms_set))
    symptom_to_idx = {s: i for i, s in enumerate(symptoms_list)}

    diseases_set = sorted(list(set(r[0].strip() for r in raw_rows if r)))
    disease_to_idx = {d: i for i, d in enumerate(diseases_set)}

    X = []
    y = []

    for r in raw_rows:
        disease = r[0].strip()
        vec = [0] * len(symptoms_list)
        for s in r[1:]:
            s_clean = s.strip().lower().replace(" ", "_")
            if s_clean in symptom_to_idx:
                vec[symptom_to_idx[s_clean]] = 1
        X.append(vec)
        y.append(disease_to_idx[disease])

    X = np.array(X)
    y = np.array(y)

    print(f"Fitting model on {len(X)} samples, {len(symptoms_list)} symptoms, {len(diseases_set)} diseases...")
    model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=1)
    model.fit(X, y)

    model_path = os.path.join(artifacts_dir, "model.joblib")
    joblib.dump(model, model_path)

    metadata = {
        "model_version": "v2.0.0",
        "symptoms": symptoms_list,
        "diseases": diseases_set,
        "specialties": {d: SPECIALTY_MAP.get(d, "General Medicine") for d in diseases_set},
        "descriptions": descriptions,
        "precautions": precautions,
        "severities": severities
    }

    metadata_path = os.path.join(artifacts_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("Success: Model and metadata created successfully!")

if __name__ == "__main__":
    train()
