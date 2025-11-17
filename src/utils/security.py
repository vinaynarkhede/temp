"""
Security utilities for the Distributed Compute Marketplace.

This module provides:
- Password hashing using bcrypt
- Password verification
- API key generation using cryptographically secure random
"""

import secrets
import logging
from typing import Optional

import bcrypt

# Setup logging
logger = logging.getLogger(__name__)

# Bcrypt work factor (cost parameter)
# Higher = more secure but slower
# 12 is recommended as per CLAUDE.md
BCRYPT_WORK_FACTOR = 12


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Uses bcrypt with work factor 12 (as specified in CLAUDE.md).
    Each hash includes a unique salt, so the same password
    produces different hashes.

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hash string (60 characters, starts with $2b$)

    Example:
        >>> hashed = hash_password("SecurePassword123!")
        >>> print(hashed)
        $2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy
        >>> verify_password("SecurePassword123!", hashed)
        True
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')

    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=BCRYPT_WORK_FACTOR)
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Convert bytes back to string for storage
    hashed_str = hashed.decode('utf-8')

    logger.debug(f"Password hashed with work factor {BCRYPT_WORK_FACTOR}")

    return hashed_str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hash to verify against

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("SecurePassword123!")
        >>> verify_password("SecurePassword123!", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    try:
        # Convert strings to bytes
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')

        # Verify password
        result = bcrypt.checkpw(password_bytes, hashed_bytes)

        if result:
            logger.debug("Password verification successful")
        else:
            logger.debug("Password verification failed")

        return result

    except (ValueError, AttributeError) as e:
        # Invalid hash format or other error
        logger.warning(f"Password verification error: {e}")
        return False


def generate_api_key() -> str:
    """
    Generate a cryptographically secure API key.

    Uses Python's secrets module to generate a URL-safe random string.
    The key is 64 characters long (as per database schema).

    Returns:
        64-character URL-safe random string

    Example:
        >>> api_key = generate_api_key()
        >>> len(api_key)
        64
        >>> api_key2 = generate_api_key()
        >>> api_key != api_key2
        True

    Note:
        Uses secrets.token_urlsafe which is cryptographically secure.
        Each call produces a unique key with extremely high probability.
    """
    # Generate 48 random bytes
    # token_urlsafe returns base64-encoded string, so 48 bytes ≈ 64 chars
    # (48 bytes * 4/3 for base64 encoding = 64 characters)
    api_key = secrets.token_urlsafe(48)

    logger.debug("Generated new API key")

    return api_key
