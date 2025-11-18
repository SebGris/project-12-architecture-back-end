"""
Tests unitaires pour AuthService.

Tests couverts:
- authenticate() : authentification utilisateur (succès/échec)
- generate_token() : génération JWT avec payload complet
- validate_token() : validation JWT (valide, expiré, invalide)
- save_token() / load_token() : persistance token sur disque
- delete_token() : suppression token (logout)
- get_current_user() : récupération utilisateur depuis token
- is_authenticated() : vérification authentification active
- _get_or_create_secret_key() : gestion clé secrète
"""

import pytest
import jwt
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from freezegun import freeze_time

from src.models.user import Department, User
from src.services.auth_service import AuthService


@pytest.fixture
def mock_repository(mocker):
    """Create a mock UserRepository."""
    return mocker.Mock()


@pytest.fixture
def auth_service(mock_repository, mocker):
    """Create an AuthService instance with mock repository."""
    # Mock environment variable to ensure consistent secret key
    mocker.patch.dict(
        os.environ,
        {"EPICEVENTS_SECRET_KEY": "test_secret_key_32_chars_long_1234567890"},
    )
    return AuthService(repository=mock_repository)


@pytest.fixture
def mock_user(mocker):
    """Create a mock user for testing."""
    user = mocker.Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@epicevents.com"
    user.first_name = "Test"
    user.last_name = "User"
    user.phone = "0612345678"
    user.department = Department.COMMERCIAL
    user.verify_password = mocker.Mock(
        return_value=True
    )  # stocker le hash pdw
    return user


@pytest.fixture
def cleanup_token_file():
    """Clean up token file after test."""
    yield
    token_file = Path.home() / ".epicevents" / "token"
    if token_file.exists():
        token_file.unlink()


class TestGetOrCreateSecretKey:
    """Test _get_or_create_secret_key method."""

    def test_get_secret_key_from_env(self, mocker, mock_repository):
        """GIVEN EPICEVENTS_SECRET_KEY in env / WHEN service created / THEN uses env key"""
        # Arrange
        expected_key = "my_custom_secret_key_from_env_1234567890"
        mocker.patch.dict(os.environ, {"EPICEVENTS_SECRET_KEY": expected_key})

        # Act
        service = AuthService(repository=mock_repository)

        # Assert
        assert service._secret_key == expected_key

    def test_generate_secret_key_if_not_in_env(self, mocker, mock_repository):
        """GIVEN no EPICEVENTS_SECRET_KEY in env / WHEN service created / THEN generates key"""
        # Arrange - Remove env variable
        mocker.patch.dict(os.environ, {}, clear=True)

        # Act
        service = AuthService(repository=mock_repository)

        # Assert
        assert service._secret_key is not None
        assert (
            len(service._secret_key) == 64
        )  # secrets.token_hex(32) produces 64 chars


class TestAuthenticate:
    """Test authenticate method."""

    def test_authenticate_success(
        self, auth_service, mock_repository, mock_user
    ):
        """GIVEN valid username and password / WHEN authenticate() / THEN returns user"""
        # Arrange
        mock_repository.get_by_username.return_value = mock_user
        mock_user.verify_password.return_value = True

        # Act
        result = auth_service.authenticate("testuser", "CorrectPassword123!")

        # Assert
        mock_repository.get_by_username.assert_called_once_with("testuser")
        mock_user.verify_password.assert_called_once_with(
            "CorrectPassword123!"
        )
        assert result == mock_user

    def test_authenticate_user_not_found(self, auth_service, mock_repository):
        """GIVEN non-existing username / WHEN authenticate() / THEN returns None"""
        # Arrange
        mock_repository.get_by_username.return_value = None

        # Act
        result = auth_service.authenticate("nonexistent", "password")

        # Assert
        mock_repository.get_by_username.assert_called_once_with("nonexistent")
        assert result is None

    def test_authenticate_wrong_password(
        self, auth_service, mock_repository, mock_user
    ):
        """GIVEN wrong password / WHEN authenticate() / THEN returns None"""
        # Arrange
        mock_repository.get_by_username.return_value = mock_user
        mock_user.verify_password.return_value = False

        # Act
        result = auth_service.authenticate("testuser", "WrongPassword")

        # Assert
        mock_user.verify_password.assert_called_once_with("WrongPassword")
        assert result is None


class TestGenerateToken:
    """Test generate_token method."""

    @freeze_time("2025-01-15 10:00:00")
    def test_generate_token_success(self, auth_service, mock_user):
        """GIVEN authenticated user / WHEN generate_token() / THEN returns valid JWT"""
        # Act
        token = auth_service.generate_token(mock_user)

        # Assert
        assert token is not None
        assert isinstance(token, str)

        # Decode and verify payload
        payload = jwt.decode(
            token, auth_service._secret_key, algorithms=["HS256"]
        )
        assert payload["user_id"] == 1
        assert payload["username"] == "testuser"
        assert payload["department"] == "COMMERCIAL"
        assert "exp" in payload
        assert "iat" in payload

    @freeze_time("2025-01-15 10:00:00")
    def test_generate_token_expiration_24h(self, auth_service, mock_user):
        """GIVEN user / WHEN generate_token() / THEN token expires in 24h"""
        # Act
        token = auth_service.generate_token(mock_user)

        # Assert
        payload = jwt.decode(
            token, auth_service._secret_key, algorithms=["HS256"]
        )
        iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        # Verify expiration is 24 hours after issuance
        expected_exp = iat + timedelta(hours=24)
        assert exp == expected_exp


class TestValidateToken:
    """Test validate_token method."""

    @freeze_time("2025-01-15 10:00:00")
    def test_validate_token_success(self, auth_service, mock_user):
        """GIVEN valid token / WHEN validate_token() / THEN returns payload"""
        # Arrange
        token = auth_service.generate_token(mock_user)

        # Act
        payload = auth_service.validate_token(token)

        # Assert
        assert payload is not None
        assert payload["user_id"] == 1
        assert payload["username"] == "testuser"

    @freeze_time("2025-01-15 10:00:00")
    def test_validate_token_expired(self, auth_service, mock_user):
        """GIVEN expired token / WHEN validate_token() / THEN returns None"""
        # Arrange - Generate token at T0
        token = auth_service.generate_token(mock_user)

        # Act - Try to validate 25 hours later (after 24h expiration)
        with freeze_time("2025-01-16 11:00:01"):
            payload = auth_service.validate_token(token)

        # Assert
        assert payload is None

    def test_validate_token_invalid(self, auth_service):
        """GIVEN invalid token / WHEN validate_token() / THEN returns None"""
        # Act
        payload = auth_service.validate_token("invalid.token.here")

        # Assert
        assert payload is None

    def test_validate_token_tampered(self, auth_service, mock_user):
        """GIVEN tampered token / WHEN validate_token() / THEN returns None"""
        # Arrange - Generate valid token
        token = auth_service.generate_token(mock_user)

        # Tamper with token significantly (change payload section)
        # JWT has 3 parts: header.payload.signature
        parts = token.split(".")
        # Change the payload (middle part) by replacing a few characters
        tampered_payload = "X" + parts[1][1:-1] + "Y"
        tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"

        # Act
        payload = auth_service.validate_token(tampered_token)

        # Assert
        assert payload is None


class TestSaveAndLoadToken:
    """Test save_token and load_token methods."""

    def test_save_and_load_token_success(
        self, auth_service, cleanup_token_file
    ):
        """GIVEN token / WHEN save_token() then load_token() / THEN token retrieved"""
        # Arrange
        test_token = "test.jwt.token"

        # Act
        auth_service.save_token(test_token)
        loaded_token = auth_service.load_token()

        # Assert
        assert loaded_token == test_token

    def test_load_token_file_not_exists(
        self, auth_service, cleanup_token_file
    ):
        """GIVEN no token file / WHEN load_token() / THEN returns None"""
        # Ensure file doesn't exist
        token_file = Path.home() / ".epicevents" / "token"
        if token_file.exists():
            token_file.unlink()

        # Act
        result = auth_service.load_token()

        # Assert
        assert result is None

    def test_save_token_creates_directory(
        self, auth_service, cleanup_token_file
    ):
        """GIVEN no .epicevents dir / WHEN save_token() / THEN creates directory"""
        # Arrange - Remove directory if exists
        token_dir = Path.home() / ".epicevents"
        token_file = token_dir / "token"
        if token_file.exists():
            token_file.unlink()
        if token_dir.exists():
            token_dir.rmdir()

        # Act
        auth_service.save_token("test.token")

        # Assert
        assert token_dir.exists()
        assert token_file.exists()


class TestDeleteToken:
    """Test delete_token method."""

    def test_delete_token_success(self, auth_service, cleanup_token_file):
        """GIVEN saved token / WHEN delete_token() / THEN token file deleted"""
        # Arrange
        auth_service.save_token("test.token")
        token_file = Path.home() / ".epicevents" / "token"
        assert token_file.exists()

        # Act
        auth_service.delete_token()

        # Assert
        assert not token_file.exists()

    def test_delete_token_file_not_exists(
        self, auth_service, cleanup_token_file
    ):
        """GIVEN no token file / WHEN delete_token() / THEN no error"""
        # Arrange - Ensure file doesn't exist
        token_file = Path.home() / ".epicevents" / "token"
        if token_file.exists():
            token_file.unlink()

        # Act & Assert - Should not raise error
        auth_service.delete_token()


class TestGetCurrentUser:
    """Test get_current_user method."""

    @freeze_time("2025-01-15 10:00:00")
    def test_get_current_user_success(
        self, auth_service, mock_repository, mock_user
    ):
        """GIVEN valid saved token / WHEN get_current_user() / THEN returns user"""
        # Arrange
        token = auth_service.generate_token(mock_user)
        auth_service.save_token(token)
        mock_repository.get.return_value = mock_user

        # Act
        result = auth_service.get_current_user()

        # Assert
        mock_repository.get.assert_called_once_with(1)
        assert result == mock_user

    def test_get_current_user_no_token(self, auth_service, cleanup_token_file):
        """GIVEN no saved token / WHEN get_current_user() / THEN returns None"""
        # Arrange - Ensure no token
        token_file = Path.home() / ".epicevents" / "token"
        if token_file.exists():
            token_file.unlink()

        # Act
        result = auth_service.get_current_user()

        # Assert
        assert result is None

    @freeze_time("2025-01-15 10:00:00")
    def test_get_current_user_expired_token(
        self, auth_service, mock_user, cleanup_token_file
    ):
        """GIVEN expired token / WHEN get_current_user() / THEN deletes token and returns None"""
        # Arrange - Generate token at T0
        token = auth_service.generate_token(mock_user)
        auth_service.save_token(token)

        # Act - Try to get user 25 hours later
        with freeze_time("2025-01-16 11:00:01"):
            result = auth_service.get_current_user()

        # Assert
        assert result is None
        # Token should be deleted
        token_file = Path.home() / ".epicevents" / "token"
        assert not token_file.exists()

    @freeze_time("2025-01-15 10:00:00")
    def test_get_current_user_invalid_payload(
        self, auth_service, cleanup_token_file
    ):
        """GIVEN token with no user_id / WHEN get_current_user() / THEN returns None"""
        # Arrange - Manually create token without user_id
        payload = {
            "username": "testuser",
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
            "iat": datetime.now(timezone.utc),
        }
        token = jwt.encode(
            payload, auth_service._secret_key, algorithm="HS256"
        )
        auth_service.save_token(token)

        # Act
        result = auth_service.get_current_user()

        # Assert
        assert result is None


class TestIsAuthenticated:
    """Test is_authenticated method."""

    @freeze_time("2025-01-15 10:00:00")
    def test_is_authenticated_true(
        self, auth_service, mock_repository, mock_user, cleanup_token_file
    ):
        """GIVEN valid saved token / WHEN is_authenticated() / THEN returns True"""
        # Arrange
        token = auth_service.generate_token(mock_user)
        auth_service.save_token(token)
        mock_repository.get.return_value = mock_user

        # Act
        result = auth_service.is_authenticated()

        # Assert
        assert result is True

    def test_is_authenticated_false(self, auth_service, cleanup_token_file):
        """GIVEN no token / WHEN is_authenticated() / THEN returns False"""
        # Arrange - Ensure no token
        token_file = Path.home() / ".epicevents" / "token"
        if token_file.exists():
            token_file.unlink()

        # Act
        result = auth_service.is_authenticated()

        # Assert
        assert result is False
