"""Language and voice configuration."""

LANG_CONFIG = {
    "en": {
        "name": "English",
        "tts_language_code": "en",
        "voices": [
            {"id": "en_com", "name": "English (UK)"},
            {"id": "en_us", "name": "English (US)"},
        ],
        "tesseract_lang": "eng",
    },
    "hi": {
        "name": "Hindi",
        "tts_language_code": "hi",
        "voices": [
            {"id": "hi_male", "name": "Hindi - Male"},
            {"id": "hi_female", "name": "Hindi - Female"},
        ],
        "tesseract_lang": "hin+eng",  # Hindi + English for mixed scripts
    },
    "te": {
        "name": "Telugu",
        "tts_language_code": "te",
        "voices": [
            {"id": "te_male", "name": "Telugu - Male"},
            {"id": "te_female", "name": "Telugu - Female"},
        ],
        "tesseract_lang": "tel+eng",
    },
    "ta": {
        "name": "Tamil",
        "tts_language_code": "ta",
        "voices": [
            {"id": "ta_male", "name": "Tamil - Male"},
        ],
        "tesseract_lang": "tam+eng",
    }
}

# Medical term mappings for better translation
MEDICAL_TERMS = {
    "OD": {
        "en": "once daily",
        "hi": "दिन में एक बार",
        "te": "రోజుకు ఒకసారి"
    },
    "BD": {
        "en": "twice daily", 
        "hi": "दिन में दो बार",
        "te": "రోజుకు రెండుసార్లు"
    },
    "TID": {
        "en": "three times daily",
        "hi": "दिन में तीन बार",
        "te": "రోజుకు మూడుసార్లు"
    },
    "QID": {
        "en": "four times daily",
        "hi": "दिन में चार बार",
        "te": "రోజుకు నాలుగుసార్లు"
    },
    "HS": {
        "en": "at bedtime",
        "hi": "सोने से पहले",
        "te": "నిద్రించే ముందు"
    },
    "SOS": {
        "en": "as needed",
        "hi": "जरूरत पर",
        "te": "అవసరమైనప్పుడు"
    },
    "AC": {
        "en": "before meals",
        "hi": "खाने से पहले",
        "te": "ఆహారం తీసుకోవడానికి ముందు"
    },
    "PC": {
        "en": "after meals",
        "hi": "खाने के बाद",
        "te": "ఆహారం తీసుకున్న తర్వాత"
    }
}