"""Unit tests for PasswordHashingService."""

import pytest

from src.services.password_hashing_service import PasswordHashingService


class TestPasswordHashingService:
    """Test suite for PasswordHashingService."""

    @pytest.fixture
    def password_service(self):
        """Fixture providing a PasswordHashingService instance."""
        return PasswordHashingService()

    def test_hash_password_returns_string(self, password_service):
        """Test that hash_password returns a string."""
        password = "test_password_123"
        hashed = password_service.hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_different_each_time(self, password_service):
        """Test that hash_password generates different hashes for the same password.

        This is because bcrypt uses a random salt each time.
        """
        password = "same_password"
        hash1 = password_service.hash_password(password)
        hash2 = password_service.hash_password(password)

        assert hash1 != hash2  # Different salts = different hashes

    def test_verify_password_correct_password(self, password_service):
        """Test that verify_password returns True for correct password."""
        password = "my_secure_password"
        hashed = password_service.hash_password(password)

        assert password_service.verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self, password_service):
        """Test that verify_password returns False for incorrect password."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = password_service.hash_password(password)

        assert password_service.verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password(self, password_service):
        """Test that verify_password handles empty passwords."""
        password = ""
        hashed = password_service.hash_password(password)

        assert password_service.verify_password(password, hashed) is True
        assert password_service.verify_password("not_empty", hashed) is False

    def test_verify_password_special_characters(self, password_service):
        """Test that password hashing works with special characters."""
        password = "P@ssw0rd!#$%^&*()_+-=[]{}|;':,.<>?/~`"
        hashed = password_service.hash_password(password)

        assert password_service.verify_password(password, hashed) is True

    def test_verify_password_unicode_characters(self, password_service):
        """Test that password hashing works with unicode characters."""
        password = "mot_de_passe_éèàçù_🔒"
        hashed = password_service.hash_password(password)

        assert password_service.verify_password(password, hashed) is True

    def test_hash_starts_with_bcrypt_prefix(self, password_service):
        """Test that the hash starts with the bcrypt prefix $2b$."""
        password = "test_password"
        hashed = password_service.hash_password(password)

        assert hashed.startswith("$2b$")

    def test_verify_password_case_sensitive(self, password_service):
        """Test that password verification is case-sensitive."""
        password = "MyPassword"
        hashed = password_service.hash_password(password)

        assert password_service.verify_password("MyPassword", hashed) is True
        assert password_service.verify_password("mypassword", hashed) is False
        assert password_service.verify_password("MYPASSWORD", hashed) is False

    def test_long_password_within_limit(self, password_service):
        """Test that passwords up to 72 bytes are handled correctly.

        Bcrypt has a maximum password length of 72 bytes.
        """
        long_password = "a" * 72  # Maximum allowed
        hashed = password_service.hash_password(long_password)

        assert password_service.verify_password(long_password, hashed) is True

    def test_password_exceeding_limit_raises_error(self, password_service):
        """Test that passwords exceeding 72 bytes raise a ValueError."""
        too_long_password = "a" * 100

        with pytest.raises(ValueError, match="password cannot be longer than 72 bytes"):
            password_service.hash_password(too_long_password)
