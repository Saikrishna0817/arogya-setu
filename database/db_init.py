"""
Database initialization for VERNACULAR project.
Creates SQLite database with required tables.
"""
import sqlite3
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.paths import Paths


def init_database(db_path=None):
    """
    Initialize the VERNACULAR vault database.
    
    Args:
        db_path: Optional custom database path. Uses Paths.VAULT_DB by default.
    
    Returns:
        Path to the created database file
    """
    if db_path is None:
        db_path = Paths.VAULT_DB
    
    # Ensure vault directory exists
    Paths.VAULT_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create prescriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            drug_name TEXT NOT NULL,
            dosage TEXT,
            frequency TEXT,
            duration TEXT,
            prescribed_date TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create patients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            weight REAL,
            medical_history TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create drugs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            generic_name TEXT,
            drug_class TEXT,
            indications TEXT,
            contraindications TEXT,
            side_effects TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create interactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug1_id INTEGER,
            drug2_id INTEGER,
            severity TEXT,
            description TEXT,
            mechanism TEXT,
            management TEXT,
            FOREIGN KEY (drug1_id) REFERENCES drugs (id),
            FOREIGN KEY (drug2_id) REFERENCES drugs (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized: {db_path}")
    return db_path


if __name__ == "__main__":
    init_database()