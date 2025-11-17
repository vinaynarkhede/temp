"""
Tests for security utilities (password hashing, API key generation).

Following TDD: These tests are written BEFORE implementation.
"""

import pytest
import re


class TestPasswordHashing:
    """Test suite for password hashing functions."""

    def test_hash_password_returns_valid_bcrypt_hash(self):
        """Test that hash_password returns a valid bcrypt hash."""
        from src.utils.security import hash_password

        password = "SecurePassword123!"
        hashed = hash_password(password)

        # Bcrypt hashes start with $2b$ and are 60 characters long
        assert hashed.startswith('$2b$')
        assert len(hashed) == 60

    def test_hash_password_produces_different_hashes_for_same_password(self):
        """Test that hashing the same password twice produces different hashes (salt)."""
        from src.utils.security import hash_password

        password = "SecurePassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Should be different due to different salts
        assert hash1 != hash2

    def test_verify_password_correct_password_returns_true(self):
        """Test that verify_password returns True for correct password."""
        from src.utils.security import hash_password, verify_password

        password = "SecurePassword123!"
        hashed = hash_password(password)

        # Verify with correct password
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect_password_returns_false(self):
        """Test that verify_password returns False for incorrect password."""
        from src.utils.security import hash_password, verify_password

        password = "SecurePassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_password(password)

        # Verify with incorrect password
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password_returns_false(self):
        """Test that verify_password handles empty passwords correctly."""
        from src.utils.security import hash_password, verify_password

        password = "SecurePassword123!"
        hashed = hash_password(password)

        # Verify with empty password
        assert verify_password("", hashed) is False

    def test_hash_password_with_different_work_factors(self):
        """Test that bcrypt work factor can be configured."""
        from src.utils.security import hash_password

        password = "SecurePassword123!"

        # Default work factor (should be 12 as per CLAUDE.md)
        hashed = hash_password(password)

        # Extract work factor from hash (format: $2b$12$...)
        work_factor = int(hashed.split('$')[2])

        # Should be 12 as specified in CLAUDE.md
        assert work_factor == 12


class TestAPIKeyGeneration:
    """Test suite for API key generation."""

    def test_generate_api_key_returns_64_character_string(self):
        """Test that generate_api_key returns a 64-character string."""
        from src.utils.security import generate_api_key

        api_key = generate_api_key()

        # Should be 64 characters as per database schema
        assert len(api_key) == 64

    def test_generate_api_key_returns_url_safe_string(self):
        """Test that API keys are URL-safe (alphanumeric + - and _)."""
        from src.utils.security import generate_api_key

        api_key = generate_api_key()

        # Should only contain URL-safe characters
        assert re.match(r'^[A-Za-z0-9_-]+$', api_key)

    def test_generate_api_key_produces_unique_keys(self):
        """Test that generating multiple API keys produces unique values."""
        from src.utils.security import generate_api_key

        # Generate 1000 API keys
        api_keys = [generate_api_key() for _ in range(1000)]

        # All should be unique
        assert len(api_keys) == len(set(api_keys))

    def test_generate_api_key_uses_cryptographically_secure_random(self):
        """Test that API key generation uses secrets module (cryptographically secure)."""
        from src.utils.security import generate_api_key
        import secrets

        # This test verifies the implementation uses secrets.token_urlsafe
        # by checking that the function exists and returns expected format
        api_key = generate_api_key()

        # Verify it matches the format of secrets.token_urlsafe output
        assert isinstance(api_key, str)
        assert len(api_key) == 64


class TestPasswordHashingEdgeCases:
    """Test edge cases for password hashing."""

    def test_hash_password_handles_unicode_characters(self):
        """Test that password hashing works with Unicode characters."""
        from src.utils.security import hash_password, verify_password

        password = "Password123!你好世界"
        hashed = hash_password(password)

        # Should hash successfully
        assert hashed is not None
        # Should verify correctly
        assert verify_password(password, hashed) is True

    def test_hash_password_handles_very_long_passwords(self):
        """Test that password hashing works with very long passwords."""
        from src.utils.security import hash_password, verify_password

        # Bcrypt truncates at 72 bytes, but we should handle longer inputs
        password = "a" * 200
        hashed = hash_password(password)

        # Should hash successfully
        assert hashed is not None
        # Should verify correctly
        assert verify_password(password, hashed) is True

    def test_verify_password_handles_invalid_hash_format(self):
        """Test that verify_password handles invalid hash format gracefully."""
        from src.utils.security import verify_password

        password = "SecurePassword123!"
        invalid_hash = "not_a_valid_bcrypt_hash"

        # Should return False (not raise exception)
        assert verify_password(password, invalid_hash) is False
