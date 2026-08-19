from fastapi import APIRouter, HTTPException, status
from app.schemas.nlp import ParseInputRequest, ParseInputResponse, ParseAndPrefillResponse
from app.services.nlp_parser import NLPPatientParser

router = APIRouter(prefix="/nlp", tags=["Natural Language Processing"])

@router.post("/parse-patient-input", response_model=ParseInputResponse)
def parse_patient_input(payload: ParseInputRequest):
    """
    Extracts age, gender, symptoms, duration, severity, and confidence score
    from free-form clinical intake text (English & Urdu / Roman Urdu supported).
    """
    if not payload.text or len(payload.text.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient text is too short to parse."
        )
    return NLPPatientParser.parse(payload.text)

@router.post("/parse-and-prefill", response_model=ParseAndPrefillResponse)
def parse_and_prefill(payload: ParseInputRequest):
    """
    Parses natural clinical text and returns both raw NLP extraction
    and structured prefill parameters ready for assessment wizard.
    """
    parsed = NLPPatientParser.parse(payload.text)
    prefill = {
        "symptoms": parsed.symptoms,
        "duration_days": parsed.duration_days,
        "age_band": parsed.age_band,
        "sex": parsed.gender or "Male",
        "severity": parsed.severity,
    }
    return ParseAndPrefillResponse(parsed=parsed, prefill=prefill)
