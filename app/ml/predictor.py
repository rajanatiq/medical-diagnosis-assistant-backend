import os
import json
import joblib
import numpy as np
from typing import List, Dict, Any, Tuple

class MLPredictor:
    def __init__(self):
        self.model = None
        self.metadata = {}
        self.symptoms = []
        self.diseases = []
        self.specialties = {}
        self.descriptions = {}
        self.precautions = {}
        self.severities = {}
        self.symptom_to_idx = {}
        self.load()

    def load(self):
        artifacts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
        model_path = os.path.join(artifacts_dir, "model.joblib")
        metadata_path = os.path.join(artifacts_dir, "metadata.json")

        if os.path.exists(model_path) and os.path.exists(metadata_path):
            try:
                self.model = joblib.load(model_path)
                with open(metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)

                self.symptoms = self.metadata.get("symptoms", [])
                self.diseases = self.metadata.get("diseases", [])
                self.specialties = self.metadata.get("specialties", {})
                self.descriptions = self.metadata.get("descriptions", {})
                self.precautions = self.metadata.get("precautions", {})
                self.severities = self.metadata.get("severities", {})
                self.symptom_to_idx = {s: i for i, s in enumerate(self.symptoms)}
                print(f"ML Predictor loaded {len(self.symptoms)} symptoms and {len(self.diseases)} conditions.")
            except Exception as e:
                print(f"Failed to load ML artifacts: {e}")

    def predict(self, user_symptoms: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.model or not self.symptoms:
            self.load()

        if not self.model:
            return []

        # Vectorize symptoms
        vec = [0] * len(self.symptoms)
        matched_count = 0
        for s in user_symptoms:
            clean_s = s.strip().lower().replace(" ", "_")
            if clean_s in self.symptom_to_idx:
                vec[self.symptom_to_idx[clean_s]] = 1
                matched_count += 1

        if matched_count == 0:
            # Fallback if no matching symptoms recognized
            return [{
                "disease": "General Health Assessment Needed",
                "probability": 50.0,
                "specialty": "General Practice",
                "description": "Please consult a doctor with more details about your symptoms.",
                "precautions": ["Rest well", "Stay hydrated", "Seek medical evaluation"]
            }]

        X_input = np.array([vec])
        proba = self.model.predict_proba(X_input)[0]

        # Top-K indices sorted by probability descending
        top_indices = np.argsort(proba)[::-1][:top_k]

        results = []
        for idx in top_indices:
            disease_name = self.diseases[idx]
            raw_prob = float(proba[idx])
            # Scale to realistic percentages
            prob_percent = round(min(max(raw_prob * 100.0, 5.0), 99.0), 1)

            results.append({
                "disease": disease_name,
                "probability": prob_percent,
                "specialty": self.specialties.get(disease_name, "General Medicine"),
                "description": self.descriptions.get(disease_name, f"Common medical condition: {disease_name}"),
                "precautions": self.precautions.get(disease_name, ["Rest", "Consult a doctor", "Follow medical advice"])
            })

        return results

predictor = MLPredictor()
