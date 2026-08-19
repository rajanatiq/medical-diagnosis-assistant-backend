import os
import csv
import json
import joblib
import numpy as np
from collections import defaultdict
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, f1_score, classification_report

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "app", "ml", "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# 1. Cleaning and normalization helpers
def clean_symptom(s: str) -> str:
    if not s:
        return ""
    s = s.strip().lower()
    s = s.replace("dischromic _patches", "dischromic_patches")
    s = s.replace("foul_smell_of urine", "foul_smell_of_urine")
    s = s.replace("spotting_ urination", "spotting_urination")
    s = s.replace(" ", "_")
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")

def clean_disease(d: str) -> str:
    if not d:
        return ""
    d = d.strip()
    if d == "Dimorphic hemmorhoids(piles)":
        return "Dimorphic hemorrhoids(piles)"
    if d == "Peptic ulcer diseae":
        return "Peptic ulcer disease"
    if d == "(vertigo) Paroymsal  Positional Vertigo":
        return "(vertigo) Paroxysmal Positional Vertigo"
    return d

SPECIALTY_MAPPING = {
    "Heart attack": "Cardiology",
    "Hypertension": "Cardiology",
    "Bronchial Asthma": "Pulmonology",
    "Pneumonia": "Pulmonology",
    "Tuberculosis": "Pulmonology",
    "Diabetes": "Endocrinology",
    "Hyperthyroidism": "Endocrinology",
    "Hypothyroidism": "Endocrinology",
    "Hypoglycemia": "Endocrinology",
    "GERD": "Gastroenterology",
    "Peptic ulcer disease": "Gastroenterology",
    "Gastroenteritis": "Gastroenterology",
    "Chronic cholestasis": "Gastroenterology",
    "Alcoholic hepatitis": "Gastroenterology",
    "Jaundice": "Gastroenterology",
    "hepatitis A": "Gastroenterology",
    "Hepatitis B": "Gastroenterology",
    "Hepatitis C": "Gastroenterology",
    "Hepatitis D": "Gastroenterology",
    "Hepatitis E": "Gastroenterology",
    "Urinary tract infection": "Urology",
    "Dimorphic hemorrhoids(piles)": "Proctology / General Surgery",
    "Varicose veins": "Vascular Surgery",
    "Osteoarthritis": "Orthopedics / Rheumatology",
    "Osteoarthristis": "Orthopedics / Rheumatology",
    "Arthritis": "Rheumatology",
    "Cervical spondylosis": "Orthopedics / Neurology",
    "Acne": "Dermatology",
    "Psoriasis": "Dermatology",
    "Impetigo": "Dermatology",
    "Fungal infection": "Dermatology",
    "Allergy": "Allergy & Immunology",
    "Drug Reaction": "Allergy & Immunology",
    "Migraine": "Neurology",
    "Paralysis (brain hemorrhage)": "Neurology / Emergency",
    "(vertigo) Paroxysmal Positional Vertigo": "ENT / Neurology",
    "Malaria": "Infectious Diseases / General Medicine",
    "Dengue": "Infectious Diseases / General Medicine",
    "Typhoid": "Infectious Diseases / General Medicine",
    "Chicken pox": "Infectious Diseases / Pediatrics",
    "Common Cold": "General Medicine",
    "AIDS": "Infectious Diseases / Immunology"
}

def train_and_export():
    print("=== 1. LOADING DATASETS ===")
    descriptions = {}
    desc_file = os.path.join(DATA_DIR, "symptom_Description.csv")
    with open(desc_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for r in reader:
            if len(r) >= 2:
                descriptions[clean_disease(r[0])] = r[1].strip()

    precautions = {}
    prec_file = os.path.join(DATA_DIR, "symptom_precaution.csv")
    with open(prec_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for r in reader:
            if len(r) >= 2:
                precautions[clean_disease(r[0])] = [p.strip() for p in r[1:] if p and p.strip()]

    severities = {}
    sev_file = os.path.join(DATA_DIR, "Symptom-severity.csv")
    with open(sev_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for r in reader:
            if len(r) >= 2 and r[1].strip().isdigit():
                sym = clean_symptom(r[0])
                severities[sym] = int(r[1].strip())

    dataset_file = os.path.join(DATA_DIR, "dataset.csv")
    raw_records = []
    all_symptoms_set = set()
    all_diseases_set = set()

    with open(dataset_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for r in reader:
            if not r or not r[0].strip():
                continue
            disease = clean_disease(r[0])
            symptoms = [clean_symptom(s) for s in r[1:] if s and s.strip()]
            symptoms = [s for s in symptoms if s]
            raw_records.append((disease, set(symptoms)))
            all_diseases_set.add(disease)
            all_symptoms_set.update(symptoms)

    symptom_list = sorted(list(all_symptoms_set))
    symptom_index = {s: i for i, s in enumerate(symptom_list)}
    disease_list = sorted(list(all_diseases_set))
    disease_index = {d: i for i, d in enumerate(disease_list)}

    for s in symptom_list:
        if s not in severities:
            severities[s] = 3

    print(f"Loaded {len(raw_records)} records across {len(disease_list)} diseases and {len(symptom_list)} unique symptoms.")

    X = np.zeros((len(raw_records), len(symptom_list)), dtype=np.float32)
    y = np.zeros(len(raw_records), dtype=np.int32)

    for i, (disease, sym_set) in enumerate(raw_records):
        y[i] = disease_index[disease]
        for s in sym_set:
            if s in symptom_index:
                X[i, symptom_index[s]] = 1.0

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set shape: {X_train.shape}, Test set shape: {X_test.shape}")
    print("Training base Random Forest Classifier...")
    base_rf = RandomForestClassifier(
        n_estimators=120,
        max_depth=16,
        min_samples_split=2,
        random_state=42,
        class_weight="balanced"
    )
    base_rf.fit(X_train, y_train)

    print("Calibrating probabilities using CalibratedClassifierCV (sigmoid)...")
    calibrated_clf = CalibratedClassifierCV(estimator=base_rf, method="sigmoid", cv=5)
    calibrated_clf.fit(X_train, y_train)

    y_pred_proba = calibrated_clf.predict_proba(X_test)
    y_pred = np.argmax(y_pred_proba, axis=1)

    top1_acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")

    top3_correct = 0
    for i in range(len(y_test)):
        top3_indices = np.argsort(y_pred_proba[i])[::-1][:3]
        if y_test[i] in top3_indices:
            top3_correct += 1
    top3_acc = top3_correct / len(y_test)

    print("\n" + "="*50)
    print("MODEL EVALUATION RESULTS")
    print("="*50)
    print(f"Top-1 Accuracy: {top1_acc * 100:.2f}%")
    print(f"Top-3 Accuracy: {top3_acc * 100:.2f}%")
    print(f"Macro F1-Score: {macro_f1:.4f}")
    print("="*50 + "\n")

    artifact_bundle = {
        "model": calibrated_clf,
        "symptoms": symptom_list,
        "symptom_index": symptom_index,
        "diseases": disease_list,
        "disease_index": disease_index,
        "severities": severities,
        "descriptions": descriptions,
        "precautions": precautions,
        "specialties": {d: SPECIALTY_MAPPING.get(d, "General Practitioner") for d in disease_list},
        "metrics": {
            "top1_accuracy": float(top1_acc),
            "top3_accuracy": float(top3_acc),
            "macro_f1": float(macro_f1)
        },
        "model_version": "v1.0.0"
    }

    joblib_path = os.path.join(ARTIFACTS_DIR, "model_v1.joblib")
    joblib.dump(artifact_bundle, joblib_path)
    print(f"Saved binary model artifact bundle to: {joblib_path}")

    metadata_json = {
        "model_version": "v1.0.0",
        "total_diseases": len(disease_list),
        "total_symptoms": len(symptom_list),
        "diseases": disease_list,
        "symptoms": symptom_list,
        "severities": severities,
        "specialties": {d: SPECIALTY_MAPPING.get(d, "General Practitioner") for d in disease_list},
        "metrics": {
            "top1_accuracy": round(float(top1_acc), 4),
            "top3_accuracy": round(float(top3_acc), 4),
            "macro_f1": round(float(macro_f1), 4)
        }
    }

    json_path = os.path.join(ARTIFACTS_DIR, "metadata.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata_json, f, indent=2)
    print(f"Saved metadata JSON to: {json_path}")
    print("ML Pipeline training and artifact export completed successfully!")

if __name__ == "__main__":
    train_and_export()
