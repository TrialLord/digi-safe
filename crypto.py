import os
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CryptoManager:
    def __init__(self):
        self.salt = None
        self.master_password_hash = None
        self.key = None
        self.fernet = None
        logger.debug("CryptoManager initialized")

    def set_master_password(self, password: str):
        """Set the master password and generate its hash using Scrypt."""
        logger.debug("Setting master password")
        self.salt = os.urandom(16)
        kdf = Scrypt(
            salt=self.salt,
            length=32,
            n=2**14,
            r=8,
            p=1,
            backend=default_backend()
        )
        self.master_password_hash = kdf.derive(password.encode())
        logger.debug("Master password hash generated")
        # Derive the encryption key immediately
        self.derive_key(password)
        logger.debug("Key derived after setting master password")

    def verify_master_password(self, password: str) -> bool:
        """Verify if the provided password matches the stored hash."""
        logger.debug("Verifying master password")
        if not self.salt or not self.master_password_hash:
            logger.debug("No salt or hash found")
            return False
        
        kdf = Scrypt(
            salt=self.salt,
            length=32,
            n=2**14,
            r=8,
            p=1,
            backend=default_backend()
        )
        try:
            kdf.verify(password.encode(), self.master_password_hash)
            logger.debug("Password verified successfully")
            
            # Derive the key using PBKDF2
            key_kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=100000,
                backend=default_backend()
            )
            self.key = key_kdf.derive(password.encode())
            self.fernet = Fernet(base64.urlsafe_b64encode(self.key))
            
            # Verify the key was derived successfully
            if not self.key or not self.fernet:
                logger.error("Key derivation failed after verification")
                return False
                
            logger.debug("Key derived after verification")
            return True
        except Exception as e:
            logger.debug(f"Password verification failed: {str(e)}")
            return False

    def derive_key(self, password: str) -> None:
        """Derive an encryption key from the master password using PBKDF2."""
        logger.debug("Deriving key")
        if not self.salt:
            logger.debug("No salt found, generating new salt")
            self.salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        self.key = kdf.derive(password.encode())
        self.fernet = Fernet(base64.urlsafe_b64encode(self.key))
        logger.debug("Key derived and Fernet instance created")

    def encrypt_data(self, data: str) -> bytes:
        """Encrypt data using AES-256-GCM."""
        logger.debug("Encrypting data")
        if not self.key:
            logger.error("No key available for encryption")
            raise ValueError("Master password not set")
        
        iv = os.urandom(12)
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
        logger.debug("Data encrypted successfully")
        return iv + encryptor.tag + ciphertext

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt data using AES-256-GCM."""
        logger.debug("Decrypting data")
        if not self.key:
            logger.error("No key available for decryption")
            raise ValueError("Master password not set")
        
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        result = (decryptor.update(ciphertext) + decryptor.finalize()).decode()
        logger.debug("Data decrypted successfully")
        return result

    def encrypt_file(self, file_path: str) -> bytes:
        """Encrypt a file using AES-256-GCM."""
        logger.debug(f"Encrypting file: {file_path}")
        if not self.key:
            logger.error("No key available for file encryption")
            raise ValueError("Master password not set")
        
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        iv = os.urandom(12)
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(file_data) + encryptor.finalize()
        logger.debug("File encrypted successfully")
        return iv + encryptor.tag + ciphertext

    def decrypt_file(self, encrypted_data: bytes, output_path: str):
        """Decrypt a file using AES-256-GCM."""
        logger.debug(f"Decrypting file to: {output_path}")
        if not self.key:
            logger.error("No key available for file decryption")
            raise ValueError("Master password not set")
        
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        logger.debug("File decrypted successfully")

    def generate_password(self, length: int = 16, include_symbols: bool = True) -> str:
        """Generate a secure random password."""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        if include_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        return ''.join(secrets.choice(chars) for _ in range(length)) 