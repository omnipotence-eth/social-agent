from typing import Optional
import os
from cryptography.fernet import Fernet
from pathlib import Path
from utils import logger

class SecureVault:
    """Secure vault for managing sensitive credentials."""
    
    def __init__(self):
        """Initialize the secure vault."""
        self.vault_dir = Path("vault")
        self.vault_dir.mkdir(exist_ok=True)
        self.key_file = self.vault_dir / "key.key"
        self.credentials_file = self.vault_dir / "credentials.enc"
        self._setup_key()

    def _setup_key(self) -> None:
        """Set up encryption key."""
        if not self.key_file.exists():
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            logger.info("Generated new encryption key")
        else:
            with open(self.key_file, "rb") as f:
                key = f.read()
        self.fernet = Fernet(key)

    def store_credentials(self, credentials: dict) -> None:
        """Store encrypted credentials."""
        try:
            encrypted_data = self.fernet.encrypt(str(credentials).encode())
            with open(self.credentials_file, "wb") as f:
                f.write(encrypted_data)
            logger.info("Stored encrypted credentials")
        except Exception as e:
            logger.error(f"Error storing credentials: {str(e)}")
            raise

    def get_credentials(self) -> Optional[dict]:
        """Retrieve and decrypt credentials."""
        try:
            if not self.credentials_file.exists():
                return None
            with open(self.credentials_file, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return eval(decrypted_data.decode())  # Safe in this context
        except Exception as e:
            logger.error(f"Error retrieving credentials: {str(e)}")
            return None

    def rotate_key(self) -> None:
        """Rotate the encryption key."""
        try:
            # Generate new key
            new_key = Fernet.generate_key()
            
            # Decrypt with old key
            old_credentials = self.get_credentials()
            
            # Update key
            with open(self.key_file, "wb") as f:
                f.write(new_key)
            self.fernet = Fernet(new_key)
            
            # Re-encrypt with new key
            if old_credentials:
                self.store_credentials(old_credentials)
            
            logger.info("Successfully rotated encryption key")
        except Exception as e:
            logger.error(f"Error rotating key: {str(e)}")
            raise

# Create global instance
vault = SecureVault() 