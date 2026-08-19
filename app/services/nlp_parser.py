import re
from typing import Dict, List, Optional, Any, Set
from fuzzywuzzy import fuzz
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import SessionLocal

# Common stop words to exclude from generic token matching
STOP_WORDS = {
    "and", "aur", "the", "for", "hai", "say", "se", "din", "age", "years", "year",
    "old", "have", "severe", "extreme", "bad", "with", "from", "mein", "me", "ka",
    "ki", "ke", "ko", "par", "hain", "kuch", "bohat", "bahot", "bohot", "zyada",
    "شدید", "ہے", "ہیں", "اور", "میں", "سے", "کا", "کی", "کے", "سال", "عمر",
    "patient", "suffering", "feeling", "had", "got", "ho", "gayi", "gaya", "hai",
    "dard", "pain", "ache", "takleef", "problem", "masla", "درد", "تکلیف", "مسئلہ"
}

# Required anatomical / root keywords (anchors) for symptoms with shared words like "pain" / "dard"
SYMPTOM_ANCHORS: Dict[str, Set[str]] = {
    "chest_pain": {"chest", "seena", "seene", "chati", "chaati", "heart", "cardiac", "سینہ", "دل", "چھاتی"},
    "severe_chest_pain": {"chest", "seena", "seene", "chati", "chaati", "heart", "سینہ", "دل"},
    "headache": {"head", "sar", "sir", "migraine", "headache", "سر", "مائیگرین"},
    "abdominal_pain": {"stomach", "abdomen", "abdominal", "belly", "tummy", "pet", "pait", "پیٹ", "معدہ"},
    "back_pain": {"back", "kamar", "peeth", "spine", "کمر", "پیٹھ"},
    "joint_pain": {"joint", "joints", "jod", "jodon", "joron", "ghutna", "ghutno", "knee", "haddi", "bone", "arthritis", "جوڑ", "جوڑوں", "گھٹنا"},
    "muscle_pain": {"muscle", "muscles", "pathon", "patthon", "jism", "body", "myalgia", "پٹھے", "پٹھوں", "جسم"},
    "throat_irritation": {"throat", "gala", "gale", "sore throat", "گلا", "گلے"},
    "breathlessness": {"breath", "breathing", "saans", "sans", "dam", "dyspnea", "shortness", "سانس", "دم"},
    "severe_breathlessness": {"breath", "breathing", "saans", "sans", "dam", "سانس", "دم"},
    "wheezing": {"wheez", "wheezing", "seeti", "سیٹی"},
    "cough": {"cough", "khasi", "khansi", "kasi", "kasee", "khuski", "coughing", "dry cough", "کھانسی", "خانسی"},
    "high_fever": {"fever", "bukhar", "bokhar", "temperature", "temp", "taap", "pyrexia", "بخار", "تپ", "حرارت"},
    "vomiting": {"vomit", "vomiting", "ulti", "ultiyan", "qay", "qaey", "الٹی", "قی"},
    "nausea": {"nausea", "matli", "dil kharab", "jee kharab", "متلی"},
    "diarrhoea": {"diarrhea", "diarrhoea", "dast", "loose motion", "pakhana", "اسہال", "دست"},
    "constipation": {"constipation", "kabz", "qabz", "قبض"},
    "acidity": {"acidity", "heartburn", "jalan", "reflux", "dakar", "جلن", "تیزابیت"},
    "skin_rash": {"rash", "daane", "dhabbe", "eruption", "spots", "دانے"},
    "itching": {"itch", "itching", "itchy", "kharish", "khujli", "خارش", "کھجلی"},
    "congestion": {"congestion", "runny", "stuffy", "nazla", "zukaam", "zukam", "naak", "نزلہ", "زکام", "ناک"},
    "dizziness": {"dizzy", "dizziness", "vertigo", "chakkar", "chakra", "چکر"},
    "fatigue": {"fatigue", "tired", "tiredness", "weakness", "kamzori", "thakan", "thakawat", "susti", "تھکاوٹ", "کمزوری"},
    "sweating": {"sweat", "sweating", "paseena", "پسینہ"},
    "chills": {"chill", "chills", "shivering", "kapkapi", "sardi", "thand", "کپکپی"},
    "loss_of_appetite": {"appetite", "bhook", "hunger", "بھوک"},
    "burning_micturition": {"urination", "urine", "peshab", "micturition", "پیشاب"}
}

# Fallback default variations if DB is momentarily unreachable
DEFAULT_SYMPTOM_VARIATIONS: Dict[str, List[str]] = {
    "cough": ["cough", "khasi", "khansi", "kasi", "kasee", "khuski", "coughhing", "dry cough", "persistent cough", "کھانسی", "خانسی", "خاں سی"],
    "breathlessness": ["breathlessness", "shortness of breath", "difficulty breathing", "saans phulna", "saans chalti", "saans lena", "saans phoolna", "dam ghutna", "سانس لینے میں مشکل", "دم پھولنا", "سانس پھولنا", "دم گھٹنا"],
    "chest_pain": ["chest pain", "chest tightness", "heart pain", "seena dard", "seene mein dard", "chest burning", "cardiac pain", "chati dard", "سینہ درد", "دل کا درد", "سینے میں درد"],
    "wheezing": ["wheezing", "wheze", "breathing sound", "saans mein aavaaz", "saans se awaz", "سانس میں سیٹی"],
    "headache": ["headache", "head ache", "sir dard", "sar dard", "sar me dard", "sar mein dard", "migraine", "headaches", "سر درد", "درد سر", "سر میں درد"],
    "dizziness": ["dizziness", "dizzy", "vertigo", "chakkar", "ghumrana", "chakra", "sar ghoomna", "چکر", "سر چکرانا"],
    "high_fever": ["fever", "temperature", "high temp", "temp", "high fever", "bukhar", "taap", "chalo", "bukhar uthna", "tez bukhar", "بخار", "تپ", "درجہ حرارت"],
    "fatigue": ["fatigue", "tiredness", "weakness", "exhaustion", "kamzori", "thakavat", "thakan", "tired", "susti", "تھکاوٹ", "کمزوری", "تھکن"],
    "nausea": ["nausea", "feeling sick", "queasiness", "ulti ana", "dilkasahi", "jee ghbrana", "matlhi", "matli", "متلی"],
    "vomiting": ["vomiting", "vomit", "throwing up", "ulti", "ultiyan", "qaey", "qay", "الٹی کرنا", "قے", "الٹی"],
    "diarrhoea": ["diarrhea", "diarrhoea", "loose motion", "loose stool", "peshaab", "pakhana", "dast", "pet kharab", "اسہال", "ڈھیلا پاخانہ"],
    "constipation": ["constipation", "kostband", "kabz", "qabz", "locked bowels", "tight stomach", "قبض", "بند پاخانہ"],
    "abdominal_pain": ["abdominal pain", "stomach pain", "belly pain", "pet ka dard", "pet mein dard", "pet mein takleef", "pait dard", "پیٹ درد", "پیٹ میں درد"],
    "acidity": ["acidity", "heartburn", "seene mein jalan", "acid reflux", "khate dakar", "gas", "سینے میں جلن", "تیزابیت"],
    "skin_rash": ["rash", "skin rash", "eruption", "daane", "khilaf", "kharish ke daane", "jild par daane", "خارش والے داغ", "دانے"],
    "itching": ["itching", "itchy", "itching sensation", "scratching", "khuji", "kharish", "khujli", "خارش", "کھجلی"],
    "throat_irritation": ["sore throat", "throat pain", "throat ache", "gale ka dard", "gale mein dard", "throat discomfort", "gala kharab", "gala dukhna", "گلے کا درد", "گلے میں دردیں", "گلا خراب"],
    "congestion": ["runny nose", "cold", "nasal congestion", "runny", "stuffy nose", "naak behna", "nazla", "naak band", "نزلہ", "بہتی ناک"],
    "muscle_pain": ["body ache", "muscle pain", "aches", "muscles pain", "jism dard", "puri jism mein dard", "jism me dard", "pathon me dard", "جسم کا درد", "پٹھوں میں درد"],
    "back_pain": ["back pain", "backache", "peeth ka dard", "kamar dard", "kmar mein dard", "پیٹھ درد", "کمر درد"],
    "joint_pain": ["joint pain", "arthritis", "joint ache", "bone pain", "jod mein dard", "haddi dard", "joron ka dard", "ghutne me dard", "جوڑوں میں درد", "ہڈیوں میں درد"],
    "sweating": ["sweating", "excessive sweat", "night sweats", "paseena", "paseene aana", "پسینہ"],
    "chills": ["chills", "shivering", "shivers", "kapkapi", "sardi lagna", "thand lagna", "کپکپی"],
    "loss_of_appetite": ["loss of appetite", "no appetite", "not hungry", "bhook na lagna", "bhook khatam", "بھوک نہ لگنا"],
    "burning_micturition": ["urinary pain", "painful urination", "peshab mein jalan", "peshab mein dard", "burning urination", "burning micturition", "پیشاب میں جلن"]
}

class NLPSymptomParser:
    """
    NLP Patient Input Parser with Anchor-Validated Database & Fuzzy Matching.
    Extracts age, gender, duration, severity, and normalized symptoms accurately.
    """

    # ============ AGE PATTERNS ============
    AGE_PATTERNS = [
        r"(?:i\s+am|i'm|my\s+age\s+is|meri\s+umar|umar\s+hai|umar|age)\s*(?:is)?\s*(\d{1,3})",
        r"(\d{1,3})\s*(?:years?\s*old|saal\s*ka|saal\s*ki|saal\s*umar|yo\b|yr\b|years?\b|saal\b|سال)",
        r"(?:patient\s*is\s*)(\d{1,3})",
        r"عمر\s*(\d{1,3})\s*سال",
        r"(\d{1,3})\s*سال",
    ]

    # ============ GENDER PATTERNS ============
    GENDER_PATTERNS = {
        "male": [r"\bmale\b", r"\bman\b", r"\bboy\b", r"i'm a man", r"larka", r"mard", r"aadmi", r"bhai", r"he\b", r"his\b", r"آدمی", r"مرد", r"لڑکا"],
        "female": [r"\bfemale\b", r"\bwoman\b", r"\bgirl\b", r"i'm a woman", r"larki", r"aurat", r"khatoon", r"baji", r"she\b", r"her\b", r"عورت", r"لڑکی", r"خاتون"],
    }

    # ============ DURATION PATTERNS ============
    DURATION_PATTERNS = [
        (r"(\d+)\s*(?:day|days|din|rooz|دن|دنوں)", "days"),
        (r"(\d+)\s*(?:week|weeks|hafta|hafte|haftay|ہفتہ|ہفتوں)", "weeks"),
        (r"(\d+)\s*(?:month|months|mahina|mahine|maheenay|مہینہ|مہینوں)", "months"),
        (r"(\d+)\s*(?:hour|hours|hrs?|ghanta|ghante|گھنٹہ|گھنٹے)", "hours"),
        (r"گزشتہ\s+(\d+)\s*(?:دن|دنوں)", "days"),
        (r"پچھلے\s+(\d+)\s*(?:دن|دنوں)", "days"),
    ]

    # ============ SEVERITY PATTERNS ============
    SEVERITY_KEYWORDS = {
        "severe": ["severe", "extreme", "very bad", "cant breathe", "critical", "emergency",
                   "bohat", "bahot", "bohot zyada", "shadeed", "sakht", "bura haal", "unbearable", "شدید", "بہت سخت", "ہنگامی"],
        "moderate": ["moderate", "medium", "somewhat", "darmiyana", "darmiyani", "معمولی", "درمیانی"],
        "mild": ["mild", "slight", "little", "kuch", "thora", "thori", "halka", "halki", "ہلکا", "تھوڑا"],
    }

    # ============ URDU NUMBER CONVERSION ============
    @staticmethod
    def normalize_urdu_numbers(text_input: str) -> str:
        """Convert Urdu numerals to standard English digits"""
        urdu_digits = '۰۱۲۳۴۵۶۷۸۹'
        english_digits = '0123456789'
        translation_table = str.maketrans(urdu_digits, english_digits)
        return text_input.translate(translation_table)

    # ============ TEXT NORMALIZATION ============
    @staticmethod
    def normalize_text(text_input: str) -> str:
        """Normalize text for processing"""
        text_input = text_input.lower().strip()
        text_input = NLPSymptomParser.normalize_urdu_numbers(text_input)
        text_input = re.sub(r'[\,\.\?\!\;\:\-\_]+', ' ', text_input)
        text_input = re.sub(r'\s+', ' ', text_input)
        return text_input

    # ============ AGE EXTRACTION ============
    @staticmethod
    def extract_age(text_input: str) -> Optional[int]:
        normalized = NLPSymptomParser.normalize_text(text_input)
        for pattern in NLPSymptomParser.AGE_PATTERNS:
            match = re.search(pattern, normalized)
            if match:
                try:
                    age = int(match.group(1))
                    if 1 <= age <= 120:
                        return age
                except:
                    continue
        return None

    @staticmethod
    def map_age_to_band(age: Optional[int]) -> str:
        if not age:
            return "20-29"
        if age < 10:
            return "0-9"
        elif age < 20:
            return "10-19"
        elif age < 30:
            return "20-29"
        elif age < 40:
            return "30-39"
        elif age < 50:
            return "40-49"
        elif age < 60:
            return "50-59"
        else:
            return "60+"

    # ============ GENDER EXTRACTION ============
    @staticmethod
    def extract_gender(text_input: str) -> Optional[str]:
        normalized = NLPSymptomParser.normalize_text(text_input)
        for gender, patterns in NLPSymptomParser.GENDER_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, normalized):
                    return "Female" if gender == "female" else "Male"
        return None

    # ============ FETCH SYMPTOM VARIATIONS FROM DATABASE ============
    @staticmethod
    def get_all_symptom_variations(db: Optional[Session] = None) -> Dict[str, List[str]]:
        symptom_variations: Dict[str, List[str]] = dict(DEFAULT_SYMPTOM_VARIATIONS)

        session_to_close = None
        if db is None:
            try:
                db = SessionLocal()
                session_to_close = db
            except:
                pass

        if db is not None:
            try:
                query = text("""
                    SELECT 
                        code,
                        [name],
                        label,
                        alternate_names,
                        urdu_name,
                        urdu_alternate_names
                    FROM dbo.symptoms
                    WHERE code IS NOT NULL OR [name] IS NOT NULL
                """)
                results = db.execute(query).fetchall()

                for row in results:
                    code = str(row[0] or "").lower().strip()
                    name = str(row[1] or "").lower().strip()
                    label = str(row[2] or "").lower().strip()
                    alternate_names = str(row[3] or "")
                    urdu_name = str(row[4] or "")
                    urdu_alternates = str(row[5] or "")

                    canonical_key = code if code else name.replace(" ", "_")
                    if not canonical_key:
                        continue

                    variations = list(symptom_variations.get(canonical_key, []))

                    if code and code.replace("_", " ") not in variations:
                        variations.append(code.replace("_", " "))
                    if name and name not in variations:
                        variations.append(name)
                    if label and label not in variations:
                        variations.append(label)

                    if alternate_names:
                        for item in alternate_names.split(","):
                            c = item.strip().lower()
                            if c and c not in variations:
                                variations.append(c)

                    if urdu_name:
                        for item in urdu_name.split(","):
                            c = item.strip().lower()
                            if c and c not in variations:
                                variations.append(c)

                    if urdu_alternates:
                        for item in urdu_alternates.split(","):
                            c = item.strip().lower()
                            if c and c not in variations:
                                variations.append(c)

                    symptom_variations[canonical_key] = variations
            except Exception as e:
                print(f"Notice loading symptom variations from DB: {e}")
            finally:
                if session_to_close:
                    session_to_close.close()

        return symptom_variations

    # ============ ANCHOR CHECK ============
    @staticmethod
    def passes_anchor_check(full_user_text: str, symptom_key: str) -> bool:
        """
        Ensures a symptom is ONLY matched if at least one of its distinctive
        anatomical root words exists in the user's input.
        This completely prevents 'sir dard' from matching 'chest_pain' or 'abdominal_pain'.
        """
        anchors = SYMPTOM_ANCHORS.get(symptom_key)
        if not anchors:
            return True

        for anchor in anchors:
            # Word boundary search or substring for Urdu
            if re.search(rf"\b{re.escape(anchor)}\b", full_user_text) or anchor in full_user_text:
                return True
        return False

    # ============ FUZZY MATCHING ============
    @staticmethod
    def match_phrase_fuzzy(
        phrase: str,
        full_user_text: str,
        symptom_variations: Dict[str, List[str]],
        threshold: int = 80
    ) -> Optional[str]:
        phrase = NLPSymptomParser.normalize_text(phrase)
        if len(phrase) < 3 or phrase in STOP_WORDS:
            return None

        best_match = None
        best_score = 0

        for canonical_key, variations in symptom_variations.items():
            # Crucial: Must pass anatomical root anchor check
            if not NLPSymptomParser.passes_anchor_check(full_user_text, canonical_key):
                continue

            for var in variations:
                var_norm = NLPSymptomParser.normalize_text(var)
                if not var_norm or var_norm in STOP_WORDS:
                    continue

                # Exact equality
                if phrase == var_norm:
                    return canonical_key

                # Direct Substring match with word boundary
                if (len(var_norm) >= 4 and (f" {var_norm} " in f" {phrase} ")) or (len(phrase) >= 4 and (f" {phrase} " in f" {var_norm} ")):
                    score = 92
                else:
                    # Token and ratio comparison
                    score = fuzz.ratio(phrase, var_norm)

                if score > best_score:
                    best_score = score
                    best_match = canonical_key

        if best_score >= threshold:
            return best_match
        return None

    # ============ SYMPTOM EXTRACTION ============
    @staticmethod
    def extract_symptoms(text_input: str, symptom_variations: Dict[str, List[str]]) -> List[str]:
        normalized = NLPSymptomParser.normalize_text(text_input)
        found_symptoms: List[str] = []

        words = normalized.split()
        num_words = len(words)

        # 1. Check multi-word variations first (4, 3, 2 word windows)
        for n in (4, 3, 2):
            for i in range(num_words - n + 1):
                window_phrase = " ".join(words[i:i + n])
                matched = NLPSymptomParser.match_phrase_fuzzy(
                    window_phrase,
                    normalized,
                    symptom_variations,
                    threshold=80
                )
                if matched and matched not in found_symptoms:
                    found_symptoms.append(matched)

        # 2. Check individual words (single word fuzzy match e.g. khasi, kasi, bukhar, ulti)
        for word in words:
            if len(word) >= 3 and word not in STOP_WORDS:
                matched = NLPSymptomParser.match_phrase_fuzzy(
                    word,
                    normalized,
                    symptom_variations,
                    threshold=78
                )
                if matched and matched not in found_symptoms:
                    found_symptoms.append(matched)

        return found_symptoms

    # ============ DURATION EXTRACTION ============
    @staticmethod
    def extract_duration(text_input: str) -> Optional[Dict[str, Any]]:
        normalized = NLPSymptomParser.normalize_text(text_input)

        for pattern, unit in NLPSymptomParser.DURATION_PATTERNS:
            match = re.search(pattern, normalized)
            if match:
                try:
                    value = int(match.group(1))
                    if 1 <= value <= 365:
                        return {"value": value, "unit": unit}
                except:
                    continue

        if re.search(r"\b(?:yesterday|kal\s*se)\b", normalized):
            return {"value": 1, "unit": "days"}
        if re.search(r"\b(?:today|aaj\s*se|aaj\s*subah)\b", normalized):
            return {"value": 1, "unit": "days"}

        return None

    # ============ SEVERITY EXTRACTION ============
    @staticmethod
    def extract_severity(text_input: str) -> str:
        normalized = NLPSymptomParser.normalize_text(text_input)

        for severity, keywords in NLPSymptomParser.SEVERITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in normalized:
                    return severity

        return "moderate"

    # ============ CONFIDENCE CALCULATION ============
    @staticmethod
    def calculate_confidence(parsed_data: Dict[str, Any]) -> float:
        confidence = 0.30
        if parsed_data.get("age"):
            confidence += 0.20
        if parsed_data.get("gender"):
            confidence += 0.15
        if parsed_data.get("symptoms") and len(parsed_data["symptoms"]) > 0:
            confidence += 0.25
        if parsed_data.get("duration"):
            confidence += 0.10
        return min(round(confidence, 2), 0.98)

    # ============ MAIN PARSE ============
    @staticmethod
    def parse(text_input: str, db: Optional[Session] = None) -> Dict[str, Any]:
        if not text_input or len(text_input.strip()) < 3:
            return {
                "age": None,
                "gender": None,
                "symptoms": [],
                "duration": None,
                "severity": "moderate",
                "confidence_score": 0.0,
                "warnings": ["Please provide more details about your symptoms."],
                "raw_input": text_input
            }

        try:
            # 1. Fetch symptom dictionary with database variations
            symptom_variations = NLPSymptomParser.get_all_symptom_variations(db)

            # 2. Extract fields
            age = NLPSymptomParser.extract_age(text_input)
            gender = NLPSymptomParser.extract_gender(text_input)
            symptoms = NLPSymptomParser.extract_symptoms(text_input, symptom_variations)
            duration = NLPSymptomParser.extract_duration(text_input)
            severity = NLPSymptomParser.extract_severity(text_input)

            # 3. Warnings
            warnings = []
            if not age:
                warnings.append("Age not clearly mentioned (defaulting to 20-29 band)")
            if not gender:
                warnings.append("Gender not specified (optional)")
            if len(symptoms) == 0:
                warnings.append("No recognized clinical symptoms found. Please select from checklist.")
            if not duration:
                warnings.append("Duration not specified - assuming recent onset (1-3 days)")

            # Check critical symptoms
            critical_keys = {"chest_pain", "breathlessness", "severe_chest_pain", "severe_breathlessness", "unconsciousness"}
            if any(s in critical_keys for s in symptoms):
                warnings.append("⚠️ Urgent/Emergency symptom detected. Seek immediate clinical care.")

            parsed_data = {
                "age": age,
                "gender": gender,
                "symptoms": symptoms,
                "duration": duration,
                "severity": severity,
            }

            confidence = NLPSymptomParser.calculate_confidence(parsed_data)

            return {
                "age": age,
                "gender": gender,
                "symptoms": symptoms,
                "duration": duration,
                "severity": severity,
                "confidence_score": confidence,
                "warnings": warnings,
                "raw_input": text_input
            }
        except Exception as e:
            return {
                "error": str(e),
                "age": None,
                "gender": None,
                "symptoms": [],
                "duration": None,
                "severity": "moderate",
                "confidence_score": 0.0,
                "warnings": [f"Parsing error: {str(e)}"],
                "raw_input": text_input
            }
