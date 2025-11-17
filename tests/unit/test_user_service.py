"""
Tests unitaires pour UserService.

Tests couverts:
- create_user() : création avec hashing bcrypt
- get_user_by_username() : récupération par username
- get_user_by_email() : récupération par email
- get_all_users() : liste complète
"""

import pytest
from src.models.user import Department
from src.services.user_service import UserService


@pytest.fixture
def mock_user_repository(mocker):
    """Create a mock user repository."""
    return mocker.Mock()


@pytest.fixture
def user_service(mock_user_repository):
    """Create a UserService instance with mocked repository."""
    return UserService(mock_user_repository)


@pytest.fixture
def sample_user(mocker):
    """Create a sample user for testing."""
    user = mocker.Mock()
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.first_name = "Test"
    user.last_name = "User"
    user.phone = "0123456789"
    user.department = Department.COMMERCIAL
    return user


class TestCreateUser:
    """Test create_user method."""

    def test_create_user_success(self, user_service, mock_user_repository, sample_user):
        """
        GIVEN valid user data
        WHEN create_user is called
        THEN user should be created with hashed password
        """
        # Configure mock
        mock_user_repository.create.return_value = sample_user

        # Call service
        result = user_service.create_user(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            first_name="Test",
            last_name="User",
            phone="0123456789",
            department=Department.COMMERCIAL,
        )

        # Verify repository was called
        mock_user_repository.create.assert_called_once()
        call_kwargs = mock_user_repository.create.call_args[1]

        # Verify password was hashed (not stored in plain text)
        assert "password" not in call_kwargs
        assert "password_hash" in call_kwargs
        assert call_kwargs["password_hash"] != "SecurePass123!"
        assert call_kwargs["password_hash"].startswith("$2b$")  # bcrypt hash

        # Verify other fields
        assert call_kwargs["username"] == "testuser"
        assert call_kwargs["email"] == "test@example.com"
        assert call_kwargs["department"] == Department.COMMERCIAL

        # Verify result
        assert result == sample_user


class TestGetUserByUsername:
    """Test get_user_by_username method."""

    def test_get_user_by_username_found(
        self, user_service, mock_user_repository, sample_user
    ):
        """
        GIVEN a username that exists
        WHEN get_user_by_username is called
        THEN the user should be returned
        """
        # Configure mock
        mock_user_repository.get_by_username.return_value = sample_user

        # Call service
        result = user_service.get_user_by_username("testuser")

        # Verify
        mock_user_repository.get_by_username.assert_called_once_with("testuser")
        assert result == sample_user

    def test_get_user_by_username_not_found(
        self, user_service, mock_user_repository
    ):
        """
        GIVEN a username that does not exist
        WHEN get_user_by_username is called
        THEN None should be returned
        """
        # Configure mock
        mock_user_repository.get_by_username.return_value = None

        # Call service
        result = user_service.get_user_by_username("nonexistent")

        # Verify
        mock_user_repository.get_by_username.assert_called_once_with("nonexistent")
        assert result is None


class TestGetUserByEmail:
    """Test get_user_by_email method."""

    def test_get_user_by_email_found(
        self, user_service, mock_user_repository, sample_user
    ):
        """
        GIVEN an email that exists
        WHEN get_user_by_email is called
        THEN the user should be returned
        """
        # Configure mock
        mock_user_repository.get_by_email.return_value = sample_user

        # Call service
        result = user_service.get_user_by_email("test@example.com")

        # Verify
        mock_user_repository.get_by_email.assert_called_once_with("test@example.com")
        assert result == sample_user

    def test_get_user_by_email_not_found(
        self, user_service, mock_user_repository
    ):
        """
        GIVEN an email that does not exist
        WHEN get_user_by_email is called
        THEN None should be returned
        """
        # Configure mock
        mock_user_repository.get_by_email.return_value = None

        # Call service
        result = user_service.get_user_by_email("nonexistent@example.com")

        # Verify
        mock_user_repository.get_by_email.assert_called_once_with(
            "nonexistent@example.com"
        )
        assert result is None


class TestGetAllUsers:
    """Test get_all_users method."""

    def test_get_all_users(self, user_service, mock_user_repository, sample_user):
        """
        GIVEN multiple users in the system
        WHEN get_all_users is called
        THEN all users should be returned
        """
        # Configure mock
        users = [sample_user, sample_user]
        mock_user_repository.get_all.return_value = users

        # Call service
        result = user_service.get_all_users()

        # Verify
        mock_user_repository.get_all.assert_called_once()
        assert result == users
        assert len(result) == 2

    def test_get_all_users_empty(self, user_service, mock_user_repository):
        """
        GIVEN no users in the system
        WHEN get_all_users is called
        THEN an empty list should be returned
        """
        # Configure mock
        mock_user_repository.get_all.return_value = []

        # Call service
        result = user_service.get_all_users()

        # Verify
        mock_user_repository.get_all.assert_called_once()
        assert result == []
