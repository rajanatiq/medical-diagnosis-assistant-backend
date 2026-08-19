from typing import Optional, List
from pydantic import BaseModel

class DiseaseResponse(BaseModel):
    id: int
    name: str
    specialty: str
    description: Optional[str] = None
    precautions: List[str] = []

    class Config:
        from_attributes = True
