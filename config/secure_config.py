#!/usr/bin/env python3
"""
Secure configuration manager for handling sensitive credentials.

This module provides functionality to:
- Store and retrieve encrypted credentials
- Manage environment variables securely
- Generate and verify encryption keys
"""

import os
import json
import base64
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime

# Try to import cryptography libraries, otherwise use fallback
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    logging.warning("Cryptography package not installed. Secure encryption unavailable.")

# Configure logging
logger = logging.getLogger(__name__)

# Path configuration
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = BASE_DIR / "lead_generator" / "config"
SECURE_DIR = CONFIG_DIR / ".secure"
KEY_FILE = SECURE_DIR / ".keyfile"
VAULT_FILE = SECURE_DIR / "credential_vault.json"
ENV_FILE = BASE_DIR / ".env"

class SecureConfigManager:
    """Manages secure configuration and credential storage."""
    
    def __init__(self, use_env_file: bool = True, master_password: Optional[str] = None):
        """
        Initialize the secure configuration manager.
        
        Args:
            use_env_file: Whether to load from .env file
            master_password: Optional master password for encryption
        """
        self.use_env_file = use_env_file
        self._encryption_key = None
        self._master_password = master_password or os.getenv("LEAD_GEN_MASTER_PASSWORD")
        self._vault_data = {}
        
        # Ensure secure directory exists
        os.makedirs(SECURE_DIR, exist_ok=True)
        
        # Load environment from .env file if it exists and is enabled
        if self.use_env_file and os.path.exists(ENV_FILE):
            self._load_env_file()
        
        # Initialize encryption key if available
        if ENCRYPTION_AVAILABLE and self._master_password:
            self._init_encryption()
            self._load_vault()
    
    def _load_env_file(self):
        """Load environment variables from .env file."""
        try:
            with open(ENV_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"\'')
            logger.info("Loaded environment variables from .env file")
        except Exception as e:
            logger.error(f"Error loading .env file: {e}")
    
    def _init_encryption(self):
        """Initialize encryption key."""
        if not ENCRYPTION_AVAILABLE:
            return
            
        try:
            if os.path.exists(KEY_FILE):
                # Load existing key
                with open(KEY_FILE, 'rb') as f:
                    salt = f.read(16)
                    
                # Derive key from master password and salt
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(self._master_password.encode()))
                self._encryption_key = Fernet(key)
            else:
                # Generate new salt and key
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(self._master_password.encode()))
                self._encryption_key = Fernet(key)
                
                # Save salt (not the derived key)
                with open(KEY_FILE, 'wb') as f:
                    f.write(salt)
                logger.info("Generated new encryption key")
        except Exception as e:
            logger.error(f"Error initializing encryption: {e}")
            self._encryption_key = None
    
    def _encrypt(self, data: str) -> str:
        """Encrypt data using the encryption key."""
        if not ENCRYPTION_AVAILABLE or not self._encryption_key:
            logger.warning("Encryption unavailable. Returning plaintext data.")
            return data
            
        try:
            return self._encryption_key.encrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return data
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt data using the encryption key."""
        if not ENCRYPTION_AVAILABLE or not self._encryption_key:
            logger.warning("Decryption unavailable. Returning data as-is.")
            return encrypted_data
            
        try:
            return self._encryption_key.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return encrypted_data
    
    def _load_vault(self):
        """Load encrypted credentials from vault file."""
        if not os.path.exists(VAULT_FILE):
            self._vault_data = {
                "credentials": {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_modified": datetime.now().isoformat()
                }
            }
            return
            
        try:
            with open(VAULT_FILE, 'r') as f:
                encrypted_data = json.load(f)
                
            if ENCRYPTION_AVAILABLE and self._encryption_key:
                # Decrypt only the credentials part
                credentials = {}
                for key, value in encrypted_data.get("credentials", {}).items():
                    credentials[key] = self._decrypt(value)
                
                self._vault_data = {
                    "credentials": credentials,
                    "metadata": encrypted_data.get("metadata", {})
                }
            else:
                self._vault_data = encrypted_data
                
            logger.info("Loaded credentials from vault")
        except Exception as e:
            logger.error(f"Error loading vault: {e}")
            self._vault_data = {
                "credentials": {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_modified": datetime.now().isoformat()
                }
            }
    
    def _save_vault(self):
        """Save encrypted credentials to vault file."""
        try:
            # Create an encrypted copy for storing
            encrypted_vault = {
                "credentials": {},
                "metadata": {
                    "created_at": self._vault_data.get("metadata", {}).get("created_at", datetime.now().isoformat()),
                    "last_modified": datetime.now().isoformat()
                }
            }
            
            # Encrypt credential values
            for key, value in self._vault_data.get("credentials", {}).items():
                if ENCRYPTION_AVAILABLE and self._encryption_key:
                    encrypted_vault["credentials"][key] = self._encrypt(value)
                else:
                    encrypted_vault["credentials"][key] = value
            
            with open(VAULT_FILE, 'w') as f:
                json.dump(encrypted_vault, f, indent=2)
                
            logger.info("Saved credentials to vault")
        except Exception as e:
            logger.error(f"Error saving vault: {e}")
    
    def get_credential(self, key: str, default: Any = None) -> Any:
        """
        Get a credential value by key.
        
        Args:
            key: Credential key
            default: Default value if key not found
            
        Returns:
            The credential value or default
        """
        # Try environment variable first
        env_value = os.getenv(key)
        if env_value:
            return env_value
            
        # Then try vault
        return self._vault_data.get("credentials", {}).get(key, default)
    
    def set_credential(self, key: str, value: str):
        """
        Store a credential value.
        
        Args:
            key: Credential key
            value: Credential value
        """
        if not self._vault_data.get("credentials"):
            self._vault_data["credentials"] = {}
            
        self._vault_data["credentials"][key] = value
        self._save_vault()
        
    def get_smtp_config(self) -> Dict[str, Any]:
        """
        Get SMTP configuration from secure storage.
        
        Returns:
            Dictionary with SMTP configuration
        """
        return {
            'smtp_server': self.get_credential('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(self.get_credential('SMTP_PORT', 587)),
            'username': self.get_credential('SMTP_USERNAME', ''),
            'password': self.get_credential('SMTP_PASSWORD', ''),
            'from_email': self.get_credential('FROM_EMAIL', ''),
            'from_name': self.get_credential('FROM_NAME', 'Lead Generator'),
            'rate_limit': int(self.get_credential('EMAIL_RATE_LIMIT', 100)),
            'batch_size': int(self.get_credential('EMAIL_BATCH_SIZE', 10)),
            'delay_between_sends': float(self.get_credential('EMAIL_DELAY', 2.0))
        }
    
    def create_env_template(self, output_file: str = ".env.template"):
        """
        Create a template .env file with required variables.
        
        Args:
            output_file: Path to output file
        """
        template = """# Malaysian Lead Generator Environment Configuration
# Rename this file to .env and fill in the values

# Master password for credential encryption
LEAD_GEN_MASTER_PASSWORD=your_secure_master_password

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_email_password
FROM_EMAIL=your_email@gmail.com
FROM_NAME=Your Name

# Email Rate Limiting
EMAIL_RATE_LIMIT=100
EMAIL_BATCH_SIZE=10
EMAIL_DELAY=2.0
DAILY_EMAIL_LIMIT=200
COOLDOWN_PERIOD=24

# Logging
LOG_DIR=logs
EMAIL_LOG_LEVEL=INFO

# Tracking
TRACK_OPENS=false
"""
        try:
            with open(output_file, 'w') as f:
                f.write(template)
            logger.info(f"Created environment template at {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error creating environment template: {e}")
            return False

# Create a global instance
secure_config = SecureConfigManager() 