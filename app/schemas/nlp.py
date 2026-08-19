from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ParseInputRequest(BaseModel):
    text: str = Field(..., min_length=2, description="Free text medical description in English or Urdu/Roman Urdu")

class ParseInputResponse(BaseModel):
    age: Optional[int] = None
    age_band: Optional[str] = "20-29"
    gender: Optional[str] = "Male"
    symptoms: List[str] = []
    symptom_labels: List[str] = []
    duration: Optional[str] = "3 days"
    duration_days: int = 3
    severity: str = "moderate" # mild, moderate, severe
    confidence_score: float = 0.0 # 0.0 to 100.0
    warnings: List[str] = []
    raw_text: str = ""

class ParseAndPrefillResponse(BaseModel):
    parsed: ParseInputResponse
    prefill: Dict[str, Any]
