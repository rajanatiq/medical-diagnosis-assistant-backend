from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class AssessmentRequest(BaseModel):
    symptoms: List[str] = Field(..., min_length=1, description="List of symptom codes or names")
    duration_days: int = Field(1, ge=1, le=90, description="Duration of symptoms in days")
    age_band: Optional[str] = "30-39"
    sex: Optional[str] = "Other"
    save_to_history: bool = True

class DiseasePrediction(BaseModel):
    disease: str
    probability: float  # Percentage 0 - 100
    specialty: str
    description: Optional[str] = None
    precautions: List[str] = []

class AssessmentResponse(BaseModel):
    id: Optional[int] = None
    urgency: str  # emergency, see_doctor_soon, routine_care, self_care
    urgency_label: str
    urgency_color: str
    urgency_description: str
    red_flag_triggered: bool
    red_flag_reason: Optional[str] = None
    composite_severity: float
    recommended_specialty: str
    top_conditions: List[DiseasePrediction]
    symptoms_analyzed: List[str]
    duration_days: int
    advice: List[str] = []

class AssessmentHistoryItem(BaseModel):
    id: int
    created_at: datetime
    symptoms: List[str]
    top_disease: str
    probability: float
    urgency: str
    urgency_label: str
    recommended_specialty: str

    class Config:
        from_attributes = True
