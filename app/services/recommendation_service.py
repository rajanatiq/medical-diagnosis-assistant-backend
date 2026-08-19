import math
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.provider import HealthcareProvider

# Haversine distance in kilometers
def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def calculate_recommendation_score(
    distance_km: float,
    provider_specialty: str,
    target_specialty: Optional[str],
    rating: float,
    is_emergency: bool = False
) -> float:
    # 1. Proximity component (decays smoothly with distance)
    dist_score = 1.0 / (1.0 + 0.08 * distance_km)
    
    # 2. Specialty match component
    spec_score = 0.2
    if target_specialty:
        target_norm = target_specialty.lower()
        prov_norm = provider_specialty.lower()
        if target_norm in prov_norm or prov_norm in target_norm:
            spec_score = 1.0
        elif "general" in prov_norm or "hospital" in prov_norm:
            spec_score = 0.6
    else:
        spec_score = 0.5

    # 3. Rating normalized
    norm_rating = min(max(rating / 5.0, 0.0), 1.0)

    # If emergency, prioritize pure proximity and emergency capability
    if is_emergency:
        return round(0.85 * dist_score + 0.15 * norm_rating, 4)

    # Standard weighted formula
    total_score = (0.50 * dist_score) + (0.35 * spec_score) + (0.15 * norm_rating)
    return round(total_score, 4)

def find_nearby_providers(
    db: Session,
    user_lat: float,
    user_lon: float,
    specialty: Optional[str] = None,
    urgency: str = "see_doctor_soon",
    radius_km: float = 50.0,
    limit: int = 10
) -> List[Dict[str, Any]]:
    is_emergency = urgency == "emergency"
    
    query = db.query(HealthcareProvider)
    if is_emergency:
        # Emergency departments and hospitals only
        query = query.filter(HealthcareProvider.emergency_capable == True)

    all_providers = query.all()
    results = []

    for p in all_providers:
        dist = calculate_haversine_distance(user_lat, user_lon, p.latitude, p.longitude)
        
        # Include if within radius (or expand radius for emergencies if none found)
        if dist <= radius_km or is_emergency:
            score = calculate_recommendation_score(
                distance_km=dist,
                provider_specialty=p.specialty,
                target_specialty=specialty,
                rating=p.rating or 4.0,
                is_emergency=is_emergency
            )
            results.append({
                "id": p.id,
                "name": p.name,
                "facility_type": p.facility_type,
                "specialty": p.specialty,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "address": p.address,
                "city": p.city,
                "phone": p.phone,
                "emergency_capable": p.emergency_capable,
                "rating": p.rating,
                "hours": p.hours,
                "distance_km": dist,
                "recommendation_score": score
            })

    # Sort descending by recommendation score
    results.sort(key=lambda x: x["recommendation_score"], reverse=True)
    return results[:limit]

# Pre-seeded realistic healthcare providers
SAMPLE_PROVIDERS = [
    {"name": "Central Emergency & Trauma Hospital", "facility_type": "Hospital", "specialty": "Emergency / General Medicine", "latitude": 33.6844, "longitude": 73.0479, "address": "Jinnah Avenue, Sector G-8", "city": "Islamabad", "phone": "+92 51 9261170", "emergency_capable": True, "rating": 4.8, "hours": "24/7 Open"},
    {"name": "St. Jude Heart & Vascular Institute", "facility_type": "Specialist Hospital", "specialty": "Cardiology", "latitude": 33.6931, "longitude": 73.0685, "address": "Health Avenue, Blue Area", "city": "Islamabad", "phone": "+92 51 8440022", "emergency_capable": True, "rating": 4.9, "hours": "24/7 Open"},
    {"name": "City Pulmonology & Chest Clinic", "facility_type": "Clinic", "specialty": "Pulmonology", "latitude": 33.7012, "longitude": 73.0521, "address": "Plaza 14, F-7 Markaz", "city": "Islamabad", "phone": "+92 51 2654321", "emergency_capable": False, "rating": 4.7, "hours": "9:00 AM - 7:00 PM"},
    {"name": "Apex Gastroenterology & Liver Center", "facility_type": "Specialist Clinic", "specialty": "Gastroenterology", "latitude": 33.7150, "longitude": 73.0380, "address": "Margalla Road, F-8/3", "city": "Islamabad", "phone": "+92 51 2259988", "emergency_capable": False, "rating": 4.6, "hours": "8:30 AM - 6:00 PM"},
    {"name": "DermaCare Skin & Laser Institute", "facility_type": "Clinic", "specialty": "Dermatology", "latitude": 33.7220, "longitude": 73.0610, "address": "Executive Complex, F-6 Markaz", "city": "Islamabad", "phone": "+92 51 2821144", "emergency_capable": False, "rating": 4.8, "hours": "10:00 AM - 8:00 PM"},
    {"name": "NeuroSpine Advanced Hospital", "facility_type": "Hospital", "specialty": "Neurology", "latitude": 33.6650, "longitude": 73.0210, "address": "I-8 Center, Sector I-8", "city": "Islamabad", "phone": "+92 51 4432100", "emergency_capable": True, "rating": 4.7, "hours": "24/7 Open"},
    {"name": "Endocrine & Diabetes Care Center", "facility_type": "Clinic", "specialty": "Endocrinology", "latitude": 33.6780, "longitude": 73.0720, "address": "Commercial Block, G-9 Markaz", "city": "Islamabad", "phone": "+92 51 2267711", "emergency_capable": False, "rating": 4.5, "hours": "9:00 AM - 5:00 PM"},
    {"name": "Hope Community Health Center", "facility_type": "Clinic", "specialty": "General Practice", "latitude": 33.6520, "longitude": 73.0850, "address": "Main Service Road, I-10", "city": "Islamabad", "phone": "+92 51 4445566", "emergency_capable": False, "rating": 4.4, "hours": "8:00 AM - 10:00 PM"},
    {"name": "Metro General Hospital", "facility_type": "Hospital", "specialty": "General Medicine", "latitude": 33.6410, "longitude": 73.0420, "address": "Peshawar Road, H-13", "city": "Rawalpindi / Islamabad", "phone": "+92 51 5567890", "emergency_capable": True, "rating": 4.6, "hours": "24/7 Open"},
    {"name": "Arthritis & Rheumatology Clinic", "facility_type": "Clinic", "specialty": "Rheumatology", "latitude": 33.7310, "longitude": 73.0750, "address": "Sector E-7 Medical Complex", "city": "Islamabad", "phone": "+92 51 2618822", "emergency_capable": False, "rating": 4.7, "hours": "9:00 AM - 6:00 PM"}
]

def seed_providers_if_empty(db: Session):
    count = db.query(HealthcareProvider).count()
    if count == 0:
        for p in SAMPLE_PROVIDERS:
            provider = HealthcareProvider(**p)
            db.add(provider)
        db.commit()
        print(f"Successfully seeded {len(SAMPLE_PROVIDERS)} healthcare providers.")
