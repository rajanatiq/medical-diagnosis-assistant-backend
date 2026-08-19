from typing import List, Optional
from pydantic import BaseModel

class SymptomResponse(BaseModel):
    id: int
    code: str
    label: str
    severity_weight: int
    category: str
    is_critical: bool

    class Config:
        from_attributes = True

class SymptomCategoryGroup(BaseModel):
    category: str
    symptoms: List[SymptomResponse]
