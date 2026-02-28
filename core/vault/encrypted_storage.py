"""Encrypted storage operations for vault."""

import sqlite3
import json
from pathlib import Path
from typing import Dict, Optional, List, Union
from cryptography.fernet import Fernet

from config.settings import Settings


class EncryptedStorage:
    """Handle encryption for vault data."""
    
    def __init__(self, key_file: Optional[Path] = None):
        self.key_file = key_file or (Settings.DATA_DIR / 'vault' / '.encryption_key')
        self.cipher = self._get_or_create_cipher()
    
    def _get_or_create_cipher(self) -> Fernet:
        """Get or create encryption key."""
        if self.key_file.exists():
            key = self.key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)
            self.key_file.chmod(0o600)  # Restrict permissions
        
        return Fernet(key)
    
    def encrypt_dict(self, data: Dict) -> bytes:
        """Encrypt dictionary."""
        json_str = json.dumps(data)
        return self.cipher.encrypt(json_str.encode())
    
    def decrypt_dict(self, encrypted: bytes) -> Dict:
        """Decrypt to dictionary."""
        decrypted = self.cipher.decrypt(encrypted)
        return json.loads(decrypted.decode())
    
    def encrypt_field(self, text: str) -> bytes:
        """Encrypt single field."""
        return self.cipher.encrypt(text.encode())
    
    def decrypt_field(self, encrypted: bytes) -> str:
        """Decrypt single field."""
        return self.cipher.decrypt(encrypted).decode()
    
    def rotate_key(self):
        """Rotate encryption key (re-encrypt all data)."""
        # Implementation would re-encrypt entire database
        pass