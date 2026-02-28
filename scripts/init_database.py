"""
Initialize the VERNACULAR vault database.

Usage:
    python scripts/init_database.py
"""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from database.db_init import init_database
except ImportError as e:
    print(f"ERROR: Could not import database module: {e}")
    print("\nMake sure database/db_init.py exists.")
    sys.exit(1)

if __name__ == "__main__":
    init_database()
    print("Vault database created successfully!")