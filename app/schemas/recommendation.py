from pydantic import BaseModel, Field
from typing import List, Optional

class ProviderResponse(BaseModel):
    id: int
    name: str
    facility_type: str
    specialty: str
    latitude: float
    longitude: float
    address: str
    city: Optional[str] = None
    phone: Optional[str] = None
    emergency_capable: bool
    rating: float
    hours: str
    distance_km: float
    recommendation_score: float

class RecommendationQuery(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    specialty: Optional[str] = None
    condition: Optional[str] = None
    urgency: Optional[str] = "see_doctor_soon"
    radius_km: Optional[float] = 50.0
    limit: Optional[int] = 10
