"""Manage encrypted prescription history."""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging
from cryptography.fernet import Fernet

from config.paths import Paths
from config.settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VaultManager:
    """Encrypted storage for prescription history."""
    
    def __init__(self, db_path: Optional[Path] = None, 
                 encryption_key: Optional[bytes] = None):
        self.db_path = db_path or Paths.VAULT_DB
        self.encryption_enabled = Settings.ENABLE_ENCRYPTION
        
        # Initialize encryption
        if self.encryption_enabled:
            self.cipher = self._init_encryption(encryption_key)
        else:
            self.cipher = None
        
        # Ensure DB exists
        self._init_db()
    
    def _init_encryption(self, key: Optional[bytes]) -> Fernet:
        """Initialize encryption."""
        if key is None:
            # Generate or load key
            key_file = self.db_path.parent / '.vault_key'
            if key_file.exists():
                key = key_file.read_bytes()
            else:
                key = Fernet.generate_key()
                key_file.write_bytes(key)
                key_file.chmod(0o600)  # Restrict permissions
        
        return Fernet(key)
    
    def _init_db(self):
        """Initialize database schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prescriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_name TEXT,
                    doctor_name TEXT,
                    date TEXT,
                    diagnosis TEXT,
                    medications TEXT,  -- JSON array
                    raw_ocr TEXT,
                    explanation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    encrypted INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_date ON prescriptions(date)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_patient ON prescriptions(patient_name)
            """)
            
            conn.commit()
        
        logger.info(f"Vault initialized at {self.db_path}")
    
    def _encrypt(self, text: str) -> bytes:
        """Encrypt text."""
        if self.cipher:
            return self.cipher.encrypt(text.encode())
        return text.encode()
    
    def _decrypt(self, data: bytes) -> str:
        """Decrypt data."""
        if self.cipher:
            return self.cipher.decrypt(data).decode()
        return data.decode()
    
    def save_prescription(self, prescription: Dict, 
                         explanation: str,
                         raw_ocr: str) -> int:
        """
        Save prescription to vault.
        
        Returns:
            ID of saved record
        """
        # Prepare data
        data = {
            'patient_name': prescription.get('patient_name'),
            'doctor_name': prescription.get('doctor_name'),
            'date': prescription.get('date'),
            'diagnosis': prescription.get('diagnosis'),
            'medications': json.dumps(prescription.get('medications', [])),
            'raw_ocr': raw_ocr,
            'explanation': explanation
        }
        
        # Encrypt sensitive fields
        if self.encryption_enabled:
            data['medications'] = self._encrypt(data['medications'])
            data['raw_ocr'] = self._encrypt(data['raw_ocr'])
            data['explanation'] = self._encrypt(data['explanation'])
            encrypted_flag = 1
        else:
            encrypted_flag = 0
        
        # Insert
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO prescriptions 
                (patient_name, doctor_name, date, diagnosis, medications, 
                 raw_ocr, explanation, encrypted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['patient_name'],
                data['doctor_name'],
                data['date'],
                data['diagnosis'],
                data['medications'] if self.encryption_enabled else data['medications'],
                data['raw_ocr'] if self.encryption_enabled else data['raw_ocr'],
                data['explanation'] if self.encryption_enabled else data['explanation'],
                encrypted_flag
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_prescription(self, record_id: int) -> Optional[Dict]:
        """Retrieve single prescription."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM prescriptions WHERE id = ?", 
                (record_id,)
            ).fetchone()
            
            if not row:
                return None
            
            return self._row_to_dict(row)
    
    def list_prescriptions(self, patient_name: Optional[str] = None,
                          limit: int = 50) -> List[Dict]:
        """List prescriptions, optionally filtered."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if patient_name:
                rows = conn.execute(
                    """SELECT * FROM prescriptions 
                       WHERE patient_name LIKE ? 
                       ORDER BY created_at DESC LIMIT ?""",
                    (f"%{patient_name}%", limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT * FROM prescriptions 
                       ORDER BY created_at DESC LIMIT ?""",
                    (limit,)
                ).fetchall()
            
            return [self._row_to_dict(row) for row in rows]
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert DB row to dict with decryption."""
        result = dict(row)
        
        # Decrypt if needed
        if result.get('encrypted') and self.cipher:
            try:
                result['medications'] = json.loads(
                    self._decrypt(result['medications'])
                )
                result['raw_ocr'] = self._decrypt(result['raw_ocr'])
                result['explanation'] = self._decrypt(result['explanation'])
            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                result['medications'] = []
                result['raw_ocr'] = "[Encrypted]"
                result['explanation'] = "[Encrypted]"
        else:
            result['medications'] = json.loads(result['medications'])
        
        return result
    
    def delete_prescription(self, record_id: int) -> bool:
        """Delete prescription."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM prescriptions WHERE id = ?", 
                (record_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def get_statistics(self) -> Dict:
        """Get vault statistics."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM prescriptions"
            ).fetchone()[0]
            
            unique_patients = conn.execute(
                "SELECT COUNT(DISTINCT patient_name) FROM prescriptions"
            ).fetchone()[0]
            
            recent = conn.execute(
                """SELECT COUNT(*) FROM prescriptions 
                   WHERE created_at > date('now', '-30 days')"""
            ).fetchone()[0]
            
            return {
                'total_records': total,
                'unique_patients': unique_patients,
                'last_30_days': recent,
                'encrypted': self.encryption_enabled
            }