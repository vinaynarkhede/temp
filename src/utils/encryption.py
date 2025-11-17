"""
Data encryption at rest for job data security.

Users can provide encryption keys to secure their job data in MinIO.
Only the user can decrypt their results.
"""

import os
import base64
import hashlib
import logging
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Manages encryption/decryption of job data."""

    # AES-256 requires 32-byte keys
    KEY_SIZE = 32
    BLOCK_SIZE = 128  # AES block size in bits
    SALT_SIZE = 16    # 16 bytes for salt
    IV_SIZE = 16      # 16 bytes for IV

    @staticmethod
    def generate_key() -> str:
        """
        Generate a random encryption key.

        Returns:
            Base64-encoded 256-bit encryption key
        """
        key = os.urandom(EncryptionManager.KEY_SIZE)
        key_b64 = base64.b64encode(key).decode('utf-8')
        logger.info("Generated new encryption key")
        return key_b64

    @staticmethod
    def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from user password using PBKDF2.

        Args:
            password: User password
            salt: Salt for key derivation (generates new if None)

        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = os.urandom(EncryptionManager.SALT_SIZE)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=EncryptionManager.KEY_SIZE,
            salt=salt,
            iterations=100000,  # OWASP recommended
            backend=default_backend()
        )

        key = kdf.derive(password.encode('utf-8'))
        logger.info("Derived encryption key from password")
        return key, salt

    @staticmethod
    def encrypt_data(data: bytes, key: str) -> bytes:
        """
        Encrypt data using AES-256-CBC.

        Args:
            data: Plaintext data to encrypt
            key: Base64-encoded encryption key

        Returns:
            Encrypted data with prepended IV and salt
            Format: [IV (16 bytes)][encrypted_data]
        """
        # Decode key from base64
        key_bytes = base64.b64decode(key)

        # Generate random IV
        iv = os.urandom(EncryptionManager.IV_SIZE)

        # Create cipher
        cipher = Cipher(
            algorithms.AES(key_bytes),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # Apply PKCS7 padding
        padder = padding.PKCS7(EncryptionManager.BLOCK_SIZE).padder()
        padded_data = padder.update(data) + padder.finalize()

        # Encrypt
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # Prepend IV to ciphertext (needed for decryption)
        encrypted_data = iv + ciphertext

        logger.info(f"Encrypted {len(data)} bytes to {len(encrypted_data)} bytes")
        return encrypted_data

    @staticmethod
    def decrypt_data(encrypted_data: bytes, key: str) -> bytes:
        """
        Decrypt data encrypted with encrypt_data.

        Args:
            encrypted_data: Encrypted data with prepended IV
            key: Base64-encoded encryption key

        Returns:
            Decrypted plaintext data

        Raises:
            ValueError: If decryption fails (wrong key, corrupted data)
        """
        try:
            # Decode key from base64
            key_bytes = base64.b64decode(key)

            # Extract IV (first 16 bytes)
            iv = encrypted_data[:EncryptionManager.IV_SIZE]
            ciphertext = encrypted_data[EncryptionManager.IV_SIZE:]

            # Create cipher
            cipher = Cipher(
                algorithms.AES(key_bytes),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()

            # Decrypt
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()

            # Remove PKCS7 padding
            unpadder = padding.PKCS7(EncryptionManager.BLOCK_SIZE).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()

            logger.info(f"Decrypted {len(encrypted_data)} bytes to {len(data)} bytes")
            return data

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Decryption failed - incorrect key or corrupted data")

    @staticmethod
    def hash_data(data: bytes) -> str:
        """
        Generate SHA-256 hash of data for integrity verification.

        Args:
            data: Data to hash

        Returns:
            Hex-encoded hash
        """
        hash_obj = hashlib.sha256(data)
        return hash_obj.hexdigest()

    @staticmethod
    def verify_integrity(data: bytes, expected_hash: str) -> bool:
        """
        Verify data integrity using hash.

        Args:
            data: Data to verify
            expected_hash: Expected hash value

        Returns:
            True if hash matches
        """
        actual_hash = EncryptionManager.hash_data(data)
        return actual_hash == expected_hash


class EncryptedStorageClient:
    """
    Storage client with automatic encryption/decryption.

    Wraps MinIO client to transparently encrypt/decrypt data.
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encrypted storage client.

        Args:
            encryption_key: Base64-encoded encryption key
                           If None, generates new key
        """
        self.encryption_key = encryption_key or EncryptionManager.generate_key()
        self.manager = EncryptionManager()
        logger.info("Initialized encrypted storage client")

    def upload_encrypted(
        self,
        data: bytes,
        object_name: str,
        include_hash: bool = True
    ) -> dict:
        """
        Encrypt and upload data.

        Args:
            data: Plaintext data
            object_name: Object name in storage
            include_hash: Include integrity hash in metadata

        Returns:
            Upload metadata (hash, size, etc.)
        """
        # Generate hash before encryption (for integrity)
        data_hash = self.manager.hash_data(data) if include_hash else None

        # Encrypt data
        encrypted_data = self.manager.encrypt_data(data, self.encryption_key)

        # In production, would call MinIO client here
        # For now, return metadata
        metadata = {
            "object_name": object_name,
            "original_size": len(data),
            "encrypted_size": len(encrypted_data),
            "hash": data_hash,
            "encrypted": True
        }

        logger.info(f"Uploaded encrypted data: {metadata}")
        return metadata

    def download_decrypted(
        self,
        encrypted_data: bytes,
        expected_hash: Optional[str] = None
    ) -> bytes:
        """
        Download and decrypt data.

        Args:
            encrypted_data: Encrypted data from storage
            expected_hash: Expected hash for integrity verification

        Returns:
            Decrypted plaintext data

        Raises:
            ValueError: If decryption or integrity check fails
        """
        # Decrypt data
        data = self.manager.decrypt_data(encrypted_data, self.encryption_key)

        # Verify integrity if hash provided
        if expected_hash:
            if not self.manager.verify_integrity(data, expected_hash):
                raise ValueError("Data integrity check failed - possible tampering")

        logger.info("Downloaded and decrypted data successfully")
        return data


# Example usage
if __name__ == "__main__":
    # Generate encryption key
    key = EncryptionManager.generate_key()
    print(f"Encryption key (save securely!): {key}")

    # Encrypt some data
    plaintext = b"Secret job results: Pi = 3.14159..."
    encrypted = EncryptionManager.encrypt_data(plaintext, key)
    print(f"Encrypted {len(plaintext)} bytes to {len(encrypted)} bytes")

    # Decrypt
    decrypted = EncryptionManager.decrypt_data(encrypted, key)
    print(f"Decrypted: {decrypted.decode('utf-8')}")

    # Verify they match
    assert plaintext == decrypted
    print("✅ Encryption/decryption successful!")

    # Generate hash for integrity
    data_hash = EncryptionManager.hash_data(plaintext)
    print(f"Data hash: {data_hash}")
