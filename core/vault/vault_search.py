"""Search capabilities for prescription vault."""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime


class VaultSearch:
    """Full-text search for prescriptions."""
    
    def __init__(self, db_path: Optional[str] = None):
        from config.paths import Paths
        self.db_path = db_path or Paths.VAULT_DB
    
    def search_by_drug(self, drug_name: str) -> List[Dict]:
        """Find prescriptions containing specific drug."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Search in medications JSON
            rows = conn.execute(
                """SELECT * FROM prescriptions 
                   WHERE medications LIKE ? 
                   ORDER BY date DESC""",
                (f'%{drug_name}%',)
            ).fetchall()
            
            return [dict(row) for row in rows]
    
    def search_by_date_range(self, start_date: str, 
                            end_date: str) -> List[Dict]:
        """Find prescriptions in date range."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            rows = conn.execute(
                """SELECT * FROM prescriptions 
                   WHERE date BETWEEN ? AND ?
                   ORDER BY date DESC""",
                (start_date, end_date)
            ).fetchall()
            
            return [dict(row) for row in rows]
    
    def search_by_doctor(self, doctor_name: str) -> List[Dict]:
        """Find prescriptions by doctor."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            rows = conn.execute(
                """SELECT * FROM prescriptions 
                   WHERE doctor_name LIKE ?
                   ORDER BY date DESC""",
                (f'%{doctor_name}%',)
            ).fetchall()
            
            return [dict(row) for row in rows]
    
    def get_drug_history(self, patient_name: str, 
                        drug_name: str) -> List[Dict]:
        """Get history of specific drug for patient."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            rows = conn.execute(
                """SELECT * FROM prescriptions 
                   WHERE patient_name = ? AND medications LIKE ?
                   ORDER BY date DESC""",
                (patient_name, f'%{drug_name}%')
            ).fetchall()
            
            return [dict(row) for row in rows]
    
    def find_duplicates(self, patient_name: str, 
                       days: int = 30) -> List[Dict]:
        """Find potential duplicate prescriptions."""
        # This would check for same drugs prescribed recently
        pass