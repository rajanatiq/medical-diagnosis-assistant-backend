from typing import Optional
from pydantic import BaseModel, Field

class NearbyCareRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    radius_km: Optional[float] = 15.0
    facility_type: Optional[str] = "all"  # all, hospital, clinic, pharmacy, emergency
    specialty: Optional[str] = None
    limit: Optional[int] = 20

class HealthcareFacilityResponse(BaseModel):
    id: str
    name: str
    facility_type: str
    specialty: str
    latitude: float
    longitude: float
    address: str
    phone: str
    emergency_capable: bool
    rating: float
    hours: str
    distance_km: float
    directions_url: str
    source: str = "Live Realtime (OpenStreetMap)"
