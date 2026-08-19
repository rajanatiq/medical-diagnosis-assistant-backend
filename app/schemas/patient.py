from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class PatientProfileUpdate(BaseModel):
    age_band: Optional[str] = "30-39"
    sex: Optional[str] = "Other"
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None

class PatientProfileResponse(BaseModel):
    id: int
    user_id: int
    age_band: str
    sex: str
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
