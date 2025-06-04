import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from crypto import CryptoManager
import base64

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self):
        logger.debug("Initializing DataManager")
        self.crypto = CryptoManager()
        self.data_dir = Path.home() / '.digital_safe'
        self.data_file = self.data_dir / 'data.enc'
        self.files_dir = self.data_dir / 'files'
        self.config_file = self.data_dir / 'config.enc'
        self.entries = {}
        
        # Create necessary directories
        self.data_dir.mkdir(exist_ok=True)
        self.files_dir.mkdir(exist_ok=True)
        logger.debug("Directories created/verified")
        
        # Load configuration
        self.load_config()
        
        # Only load data if master password is set
        if self.crypto.key:
            self.load_data()

    def load_config(self):
        """Load the configuration file (always plaintext: 16 bytes salt + 32 bytes hash)."""
        logger.debug("Loading configuration (plaintext)")
        if self.config_file.exists():
            with open(self.config_file, 'rb') as f:
                config_data = f.read()
                if config_data and len(config_data) == 48:
                    self.crypto.salt = config_data[:16]
                    self.crypto.master_password_hash = config_data[16:]
                    logger.debug("Configuration loaded successfully (plaintext)")
                else:
                    logger.error("Invalid config file format or empty config file.")
                    self.crypto.salt = None
                    self.crypto.master_password_hash = None
        else:
            logger.debug("No configuration file found")

    def save_config(self):
        """Save the salt and master password hash to the configuration file (always plaintext)."""
        logger.debug("Saving configuration (plaintext)")
        if not self.crypto.salt or not self.crypto.master_password_hash:
            logger.error("Cannot save config: Master password not set")
            raise ValueError("Master password not set")
        config_data = self.crypto.salt + self.crypto.master_password_hash
        with open(self.config_file, 'wb') as f:
            f.write(config_data)
        logger.debug("Configuration saved successfully (plaintext)")

    def is_first_run(self) -> bool:
        """Check if this is the first time running the application."""
        is_first = not self.config_file.exists()
        logger.debug(f"First run check: {is_first}")
        return is_first

    def set_master_password(self, password: str):
        """Set the master password and save configuration."""
        logger.debug("Setting master password")
        self.crypto.set_master_password(password)
        self.save_config()
        logger.debug("Master password set and configuration saved")

    def verify_master_password(self, password: str) -> bool:
        """Verify the master password."""
        logger.debug("Verifying master password")
        result = self.crypto.verify_master_password(password)
        logger.debug(f"Password verification result: {result}")
        
        if result:
            # Load data after successful verification
            try:
                self.load_data()
                logger.debug("Data loaded after password verification")
            except Exception as e:
                logger.error(f"Failed to load data after verification: {str(e)}")
                return False
                
        return result

    def load_data(self):
        """Load encrypted data from file."""
        logger.debug("Loading data")
        if not self.crypto.key:
            logger.error("Cannot load data: Master password not set")
            raise ValueError("Master password not set")
            
        if self.data_file.exists():
            try:
                with open(self.data_file, 'rb') as f:
                    encrypted_data = f.read()
                    if encrypted_data:
                        try:
                            decrypted_data = self.crypto.decrypt_data(encrypted_data)
                            self.entries = json.loads(decrypted_data)
                            logger.debug("Data loaded successfully")
                        except Exception as e:
                            logger.error(f"Failed to decrypt data: {str(e)}")
                            self.entries = {}
                    else:
                        logger.debug("Data file is empty")
                        self.entries = {}
            except Exception as e:
                logger.error(f"Failed to read data file: {str(e)}")
                self.entries = {}
        else:
            logger.debug("No data file found")
            self.entries = {}

    def save_data(self):
        """Save encrypted data to file."""
        logger.debug("Saving data")
        if not self.crypto.key:
            logger.error("Cannot save data: Master password not set")
            raise ValueError("Master password not set")
        encrypted_data = self.crypto.encrypt_data(json.dumps(self.entries))
        with open(self.data_file, 'wb') as f:
            f.write(encrypted_data)
        logger.debug("Data saved successfully")

    def add_entry(self, name: str, username: str, password: str, notes: str = ""):
        """Add a new password entry."""
        logger.debug(f"Adding password entry: {name}")
        if not self.crypto.key:
            logger.error("Cannot add entry: Master password not set")
            raise ValueError("Master password not set")
        self.entries[name] = {
            'type': 'password',
            'username': username,
            'password': password,
            'notes': notes
        }
        self.save_data()
        logger.debug("Password entry added successfully")

    def add_file(self, name: str, file_path: str, notes: str = ""):
        """Add a new file entry."""
        logger.debug(f"Adding file entry: {name}")
        if not self.crypto.key:
            logger.error("Cannot add file: Master password not set")
            raise ValueError("Master password not set")

        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create a unique filename for the encrypted file
        encrypted_filename = f"{name}_{os.path.basename(file_path)}.enc"
        encrypted_path = self.files_dir / encrypted_filename
        
        # Encrypt and save the file
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            # Convert binary data to base64 string for encryption
            file_data_b64 = base64.b64encode(file_data).decode('utf-8')
            encrypted_data = self.crypto.encrypt_data(file_data_b64)
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Add entry to database
            self.entries[name] = {
                'type': 'file',
                'original_name': os.path.basename(file_path),
                'encrypted_path': str(encrypted_path),
                'size': file_size,
                'notes': notes
            }
            self.save_data()
            logger.debug(f"File entry added successfully: {name}")
        except Exception as e:
            logger.error(f"Failed to add file: {str(e)}")
            # Clean up if encryption failed
            if encrypted_path.exists():
                try:
                    os.remove(encrypted_path)
                except:
                    pass
            raise

    def get_entry(self, name: str) -> dict:
        """Get an entry by name."""
        logger.debug(f"Getting entry: {name}")
        return self.entries.get(name)

    def get_file(self, name: str, output_path: str):
        """Get and decrypt a file."""
        logger.debug(f"Getting file: {name}")
        if not self.crypto.key:
            logger.error("Cannot get file: Master password not set")
            raise ValueError("Master password not set")
            
        entry = self.entries.get(name)
        if not entry or entry['type'] != 'file':
            logger.error("File not found")
            raise ValueError("File not found")
        
        try:
            # Read encrypted file
            with open(entry['encrypted_path'], 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt the data
            decrypted_data_b64 = self.crypto.decrypt_data(encrypted_data)
            
            # Convert from base64 back to binary
            decrypted_data = base64.b64decode(decrypted_data_b64)
            
            # Write to output file
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
                
            logger.debug(f"File retrieved and decrypted successfully: {name}")
        except Exception as e:
            logger.error(f"Failed to get file: {str(e)}")
            raise

    def get_all_entries(self) -> dict:
        """Get all entries."""
        logger.debug("Getting all entries")
        return self.entries

    def delete_entry(self, name: str):
        """Delete an entry and its associated file if it's a file entry."""
        logger.debug(f"Deleting entry: {name}")
        entry = self.entries.get(name)
        if entry:
            if entry['type'] == 'file':
                try:
                    os.remove(entry['encrypted_path'])
                    logger.debug("Associated file deleted")
                except Exception as e:
                    logger.error(f"Failed to delete file: {str(e)}")
            del self.entries[name]
            self.save_data()
            logger.debug("Entry deleted successfully") 