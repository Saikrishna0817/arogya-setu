"""Handle personally identifiable information."""

import re
import hashlib
from typing import Dict, Optional, List
from cryptography.fernet import Fernet


class PIIHandler:
    """Detect and protect PII in medical data."""
    
    # PII patterns
    PII_PATTERNS = {
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'mrn': r'\b(MRN|Medical Record|Patient ID)[:\s#]*(\d+)\b',
        'aadhaar': r'\b\d{4}\s?\d{4}\s?\d{4}\b',  # Indian Aadhaar
        'pan': r'\b[A-Z]{5}\d{4}[A-Z]\b',  # Indian PAN
    }
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        self.cipher = None
        if encryption_key:
            self.cipher = Fernet(encryption_key)
    
    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """Detect PII in text."""
        findings = {}
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                findings[pii_type] = matches
        
        return findings
    
    def redact_pii(self, text: str, replace_with: str = '[REDACTED]') -> str:
        """Remove PII from text."""
        redacted = text
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            redacted = re.sub(pattern, replace_with, redacted, flags=re.IGNORECASE)
        
        return redacted
    
    def hash_identifier(self, identifier: str) -> str:
        """Create hash of identifier for pseudonymization."""
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]
    
    def encrypt(self, data: str) -> bytes:
        """Encrypt sensitive data."""
        if not self.cipher:
            raise ValueError("Encryption key not provided")
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data."""
        if not self.cipher:
            raise ValueError("Encryption key not provided")
        return self.cipher.decrypt(encrypted_data).decode()
    
    def anonymize_prescription(self, prescription: Dict) -> Dict:
        """Create anonymized version of prescription."""
        anonymized = prescription.copy()
        
        # Hash patient name
        if 'patient_name' in anonymized and anonymized['patient_name']:
            anonymized['patient_name'] = self.hash_identifier(anonymized['patient_name'])
        
        # Remove other PII
        if 'raw_ocr' in anonymized:
            anonymized['raw_ocr'] = self.redact_pii(anonymized['raw_ocr'])
        
        return anonymized
    
    def validate_prescription_data(self, prescription: Dict) -> Dict:
        """Check prescription for unprotected PII."""
        issues = []
        
        if 'raw_ocr' in prescription:
            pii_found = self.detect_pii(prescription['raw_ocr'])
            if pii_found:
                issues.append(f"Unprotected PII found: {list(pii_found.keys())}")
        
        return {
            'safe': len(issues) == 0,
            'issues': issues,
            'recommendation': 'Encrypt or redact PII before storage' if issues else 'OK'
        }