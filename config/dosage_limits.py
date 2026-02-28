"""Safe dosage ranges based on WHO DDD and clinical guidelines."""

DOSAGE_LIMITS = {
    # Cardiovascular
    "Amlodipine": {
        "adult_standard_mg": 5,
        "max_daily_mg": 10,
        "unit": "mg",
        "frequency": "OD",
        "population_adjustments": {
            "elderly": 0.5,  # 50% dose
            "hepatic_impairment": 0.5
        }
    },
    "Metoprolol": {
        "adult_standard_mg": 50,
        "max_daily_mg": 400,
        "unit": "mg",
        "frequency": "BD",
        "population_adjustments": {
            "renal_impairment": 0.75
        }
    },
    "Losartan": {
        "adult_standard_mg": 50,
        "max_daily_mg": 100,
        "unit": "mg",
        "frequency": "OD"
    },
    # Diabetes
    "Metformin": {
        "adult_standard_mg": 500,
        "max_daily_mg": 2550,
        "unit": "mg",
        "frequency": "BD-TID",
        "population_adjustments": {
            "renal_impairment": 0.0,  # Contraindicated if eGFR < 30
            "elderly": 0.5
        }
    },
    "Glimepiride": {
        "adult_standard_mg": 2,
        "max_daily_mg": 8,
        "unit": "mg",
        "frequency": "OD"
    },
    # Pain/Inflammation
    "Ibuprofen": {
        "adult_standard_mg": 400,
        "max_daily_mg": 2400,
        "unit": "mg",
        "frequency": "TID",
        "otc_max_mg": 1200
    },
    "Paracetamol": {
        "adult_standard_mg": 500,
        "max_daily_mg": 4000,
        "unit": "mg",
        "frequency": "QID",
        "otc_max_mg": 3000
    },
    # Antibiotics (common)
    "Amoxicillin": {
        "adult_standard_mg": 500,
        "max_daily_mg": 6000,
        "unit": "mg",
        "frequency": "TID"
    },
    "Azithromycin": {
        "adult_standard_mg": 500,
        "max_daily_mg": 500,  # Usually 500 OD for 3-5 days
        "unit": "mg",
        "frequency": "OD"
    },
    # GI
    "Omeprazole": {
        "adult_standard_mg": 20,
        "max_daily_mg": 80,  # Severe cases
        "unit": "mg",
        "frequency": "OD"
    },
    "Pantoprazole": {
        "adult_standard_mg": 40,
        "max_daily_mg": 80,
        "unit": "mg",
        "frequency": "OD"
    },
    # Vitamins/Supplements
    "Vitamin D3": {
        "adult_standard_mcg": 25,  # 1000 IU
        "max_daily_mcg": 100,  # 4000 IU
        "unit": "mcg",
        "frequency": "OD"
    },
    "Vitamin B12": {
        "adult_standard_mcg": 2.4,
        "max_daily_mcg": 1000,
        "unit": "mcg",
        "frequency": "OD"
    }
}

# Common Indian brand name to generic mapping
BRAND_TO_GENERIC = {
    # Pain relievers
    "Crocin": "Paracetamol",
    "Calpol": "Paracetamol",
    "Dolo": "Paracetamol",
    "Brufen": "Ibuprofen",
    "Combiflam": "Paracetamol+Ibuprofen",
    
    # Cardiac
    "Amlong": "Amlodipine",
    "Amlokind": "Amlodipine",
    "Metolar": "Metoprolol",
    "Losar": "Losartan",
    "Telma": "Telmisartan",
    
    # Diabetes
    "Glycomet": "Metformin",
    "Amaryl": "Glimepiride",
    "Galvus": "Vildagliptin",
    
    # GI
    "Omez": "Omeprazole",
    "Pantocid": "Pantoprazole",
    "Rantac": "Ranitidine",
    
    # Antibiotics
    "Augmentin": "Amoxicillin+Clavulanate",
    "Azee": "Azithromycin",
    "Ciplox": "Ciprofloxacin",
    
    # Vitamins
    "Shelcal": "Calcium+Vitamin D3",
    "Neurobion": "Vitamin B Complex",
    "Evion": "Vitamin E"
}