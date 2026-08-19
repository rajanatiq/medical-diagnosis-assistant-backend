from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.places_service import fetch_live_nearby_healthcare

router = APIRouter(prefix="/recommendations", tags=["Healthcare Recommendations & Nearby Care"])

@router.get("/nearby")
@router.get("")
def get_nearby_care_recommendations(
    lat: float = Query(..., ge=-90.0, le=90.0, description="User Latitude"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="User Longitude"),
    specialty: Optional[str] = Query(None, description="Medical specialty"),
    urgency: Optional[str] = Query("see_doctor_soon", description="Triage urgency"),
    radius_km: Optional[float] = Query(15.0, ge=1.0, le=100.0, description="Search radius in KM"),
    limit: Optional[int] = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    facility_type = "emergency" if urgency == "emergency" else "all"
    facilities = fetch_live_nearby_healthcare(
        user_lat=lat,
        user_lon=lon,
        radius_km=radius_km or 15.0,
        facility_type=facility_type,
        specialty=specialty,
        limit=limit or 20,
        db=db
    )
    return facilities
