from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.services.nlp_parser import NLPSymptomParser
from app.db.session import get_db

router = APIRouter(prefix="/nlp", tags=["NLP Parser"])

# ============ PYDANTIC MODELS ============

class PatientInputRequest(BaseModel):
    text: str

class DurationModel(BaseModel):
    value: int
    unit: str

class ParsedResultResponse(BaseModel):
    age: Optional[int]
    age_band: Optional[str] = "20-29"
    gender: Optional[str]
    symptoms: List[str]
    duration: Optional[DurationModel]
    severity: str
    confidence_score: float
    warnings: List[str]
    raw_input: str

class FormPrefillResponse(BaseModel):
    age: Optional[int]
    age_band: str
    gender: Optional[str]
    symptom_names: List[str]
    duration_value: Optional[int]
    duration_unit: Optional[str]
    severity: str

class ParseAndPrefillResponse(BaseModel):
    parsed_result: ParsedResultResponse
    form_prefill: FormPrefillResponse

# ============ ENDPOINTS ============

@router.post("/parse-patient-input", response_model=ParsedResultResponse)
def parse_patient_input(
    request: PatientInputRequest,
    db: Session = Depends(get_db)
):
    """
    Parse natural language patient input and extract medical information
    with SQL Server database lookup and fuzzy string matching.
    """
    if not request.text or len(request.text.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please write at least 3 characters to describe your symptoms."
        )

    try:
        result = NLPSymptomParser.parse(request.text, db)
        if "error" in result and result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        age = result.get("age")
        age_band = NLPSymptomParser.map_age_to_band(age)
        duration_data = result.get("duration")

        return ParsedResultResponse(
            age=age,
            age_band=age_band,
            gender=result.get("gender"),
            symptoms=result.get("symptoms", []),
            duration=DurationModel(**duration_data) if duration_data else None,
            severity=result.get("severity", "moderate"),
            confidence_score=result.get("confidence_score", 0.7),
            warnings=result.get("warnings", []),
            raw_input=result.get("raw_input", request.text)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing input: {str(e)}"
        )

@router.post("/parse-and-prefill", response_model=ParseAndPrefillResponse)
def parse_and_prefill(
    request: PatientInputRequest,
    db: Session = Depends(get_db)
):
    """
    Parse patient input AND return structured form prefill data.
    """
    if not request.text or len(request.text.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide more details about your symptoms."
        )

    try:
        parsed = NLPSymptomParser.parse(request.text, db)
        if "error" in parsed and parsed.get("error"):
            raise HTTPException(status_code=500, detail=parsed["error"])

        age = parsed.get("age")
        age_band = NLPSymptomParser.map_age_to_band(age)
        duration_data = parsed.get("duration")

        parsed_resp = ParsedResultResponse(
            age=age,
            age_band=age_band,
            gender=parsed.get("gender"),
            symptoms=parsed.get("symptoms", []),
            duration=DurationModel(**duration_data) if duration_data else None,
            severity=parsed.get("severity", "moderate"),
            confidence_score=parsed.get("confidence_score", 0.7),
            warnings=parsed.get("warnings", []),
            raw_input=parsed.get("raw_input", request.text)
        )

        form_prefill = FormPrefillResponse(
            age=age,
            age_band=age_band,
            gender=parsed.get("gender") or "Male",
            symptom_names=parsed.get("symptoms", []),
            duration_value=duration_data["value"] if duration_data else 3,
            duration_unit=duration_data["unit"] if duration_data else "days",
            severity=parsed.get("severity", "moderate")
        )

        return ParseAndPrefillResponse(
            parsed_result=parsed_resp,
            form_prefill=form_prefill
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing input: {str(e)}"
        )

@router.get("/health")
def health_check():
    """NLP service health check"""
    return {"status": "NLP fuzzy matching service is online", "version": "2.0"}
