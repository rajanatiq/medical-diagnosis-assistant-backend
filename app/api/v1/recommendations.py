from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.recommendation import ProviderResponse
from app.services.recommendation_service import find_nearby_providers
from app.ml.predictor import predictor

router = APIRouter(prefix="/recommendations", tags=["Healthcare Provider Recommendations"])

@router.get("/nearby", response_model=List[ProviderResponse])
def get_nearby_care(
    lat: float = Query(..., ge=-90.0, le=90.0, description="User Latitude"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="User Longitude"),
    specialty: Optional[str] = Query(None, description="Recommended medical specialty"),
    urgency: Optional[str] = Query("see_doctor_soon", description="Triage urgency level"),
    radius_km: Optional[float] = Query(50.0, ge=1.0, le=500.0, description="Search radius in KM"),
    limit: Optional[int] = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    providers = find_nearby_providers(
        db=db,
        user_lat=lat,
        user_lon=lon,
        specialty=specialty,
        urgency=urgency or "see_doctor_soon",
        radius_km=radius_km or 50.0,
        limit=limit or 10
    )
    return providers

@router.get("/specialties")
def get_all_specialties():
    """List all supported medical specialties mapped from conditions"""
    unique_specialties = sorted(list(set(predictor.specialties.values())))
    return {
        "total": len(unique_specialties),
        "specialties": unique_specialties
    }
