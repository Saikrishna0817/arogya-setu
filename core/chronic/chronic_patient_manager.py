"""Manage chronic patient profiles."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PatientProfile:
    """Chronic patient profile."""
    patient_id: str
    name: str
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    
    # Medical history
    conditions: List[str] = None
    allergies: List[str] = None
    chronic_medications: List[str] = None
    
    # Monitoring
    last_checkup: Optional[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []
        if self.allergies is None:
            self.allergies = []
        if self.chronic_medications is None:
            self.chronic_medications = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class ChronicPatientManager:
    """Manage chronic patient data."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        from config.paths import Paths
        self.data_dir = data_dir or (Paths.DATA_DIR / 'chronic_patients')
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_patient_file(self, patient_id: str) -> Path:
        """Get path to patient data file."""
        return self.data_dir / f"{patient_id}.json"
    
    def create_patient(self, patient_id: str, name: str, 
                       **kwargs) -> PatientProfile:
        """Create new patient profile."""
        patient = PatientProfile(patient_id=patient_id, name=name, **kwargs)
        self.save_patient(patient)
        return patient
    
    def save_patient(self, patient: PatientProfile):
        """Save patient profile."""
        file_path = self._get_patient_file(patient.patient_id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(patient), f, indent=2)
    
    def load_patient(self, patient_id: str) -> Optional[PatientProfile]:
        """Load patient profile."""
        file_path = self._get_patient_file(patient_id)
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return PatientProfile(**data)
    
    def update_patient(self, patient_id: str, 
                       updates: Dict) -> Optional[PatientProfile]:
        """Update patient fields."""
        patient = self.load_patient(patient_id)
        if not patient:
            return None
        
        for key, value in updates.items():
            if hasattr(patient, key):
                setattr(patient, key, value)
        
        self.save_patient(patient)
        return patient
    
    def list_patients(self) -> List[Dict]:
        """List all patients."""
        patients = []
        
        for file_path in self.data_dir.glob('*.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                patients.append({
                    'id': data.get('patient_id'),
                    'name': data.get('name'),
                    'age': data.get('age'),
                    'conditions_count': len(data.get('conditions', []))
                })
        
        return patients
    
    def add_condition(self, patient_id: str, condition: str):
        """Add medical condition."""
        patient = self.load_patient(patient_id)
        if patient and condition not in patient.conditions:
            patient.conditions.append(condition)
            self.save_patient(patient)
    
    def add_allergy(self, patient_id: str, allergy: str):
        """Add allergy."""
        patient = self.load_patient(patient_id)
        if patient and allergy not in patient.allergies:
            patient.allergies.append(allergy)
            self.save_patient(patient)
    
    def add_chronic_medication(self, patient_id: str, medication: str):
        """Add chronic medication."""
        patient = self.load_patient(patient_id)
        if patient and medication not in patient.chronic_medications:
            patient.chronic_medications.append(medication)
            self.save_patient(patient)