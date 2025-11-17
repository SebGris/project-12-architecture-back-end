"""
Tests unitaires pour UserService.

Tests couverts:
- create_user() : création avec hachage bcrypt
- get_user() : récupération par ID
- verify_password() : vérification mot de passe
"""

import pytest

from src.models.user import Department, User
from src.services.user_service import UserService


@pytest.fixture
def mock_repository(mocker):
    """Create a mock UserRepository."""
    return mocker.Mock()


@pytest.fixture
def user_service(mock_repository):
    """Create a UserService instance with mock repository."""
    return UserService(repository=mock_repository)


class TestCreateUser:
    """Test create_user method."""

    def test_create_user_success(self, user_service, mock_repository):
        """GIVEN valid user data / WHEN create_user() / THEN user created with hashed password"""
        # Arrange
        mock_user = User(
            username="testuser",
            email="test@epicevents.com",
            password_hash="$2b$12$hashedpassword",
            first_name="Jean",
            last_name="Dupont",
            phone="0612345678",
            department=Department.COMMERCIAL,
        )
        mock_repository.add.return_value = mock_user

        # Act
        result = user_service.create_user(
            username="testuser",
            email="test@epicevents.com",
            password="MySecurePass123!",
            first_name="Jean",
            last_name="Dupont",
            phone="0612345678",
            department=Department.COMMERCIAL,
        )

        # Assert
        mock_repository.add.assert_called_once()
        assert result == mock_user
        # Vérifier que add() a été appelé avec un User qui a un password_hash
        call_args = mock_repository.add.call_args[0][0]
        assert isinstance(call_args, User)
        assert call_args.username == "testuser"
        assert call_args.password_hash != ""  # Vérifie que le password est hashé
        assert call_args.password_hash.startswith("$2b$")  # Format bcrypt

    def test_create_user_gestion_department(self, user_service, mock_repository):
        """GIVEN GESTION department / WHEN create_user() / THEN user created with GESTION"""
        mock_user = User(
            username="gestion1",
            email="gestion@epicevents.com",
            password_hash="$2b$12$hash",
            first_name="Marie",
            last_name="Martin",
            phone="0123456789",
            department=Department.GESTION,
        )
        mock_repository.add.return_value = mock_user

        result = user_service.create_user(
            username="gestion1",
            email="gestion@epicevents.com",
            password="Password123!",
            first_name="Marie",
            last_name="Martin",
            phone="0123456789",
            department=Department.GESTION,
        )

        assert result.department == Department.GESTION

    def test_create_user_support_department(self, user_service, mock_repository):
        """GIVEN SUPPORT department / WHEN create_user() / THEN user created with SUPPORT"""
        mock_user = User(
            username="support1",
            email="support@epicevents.com",
            password_hash="$2b$12$hash",
            first_name="Pierre",
            last_name="Durand",
            phone="0987654321",
            department=Department.SUPPORT,
        )
        mock_repository.add.return_value = mock_user

        result = user_service.create_user(
            username="support1",
            email="support@epicevents.com",
            password="SecurePass456!",
            first_name="Pierre",
            last_name="Durand",
            phone="0987654321",
            department=Department.SUPPORT,
        )

        assert result.department == Department.SUPPORT


class TestGetUser:
    """Test get_user method."""

    def test_get_user_found(self, user_service, mock_repository):
        """GIVEN existing user_id / WHEN get_user() / THEN returns user"""
        mock_user = User(
            id=1,
            username="testuser",
            email="test@epicevents.com",
            password_hash="$2b$12$hash",
            first_name="Jean",
            last_name="Dupont",
            phone="0612345678",
            department=Department.COMMERCIAL,
        )
        mock_repository.get.return_value = mock_user

        result = user_service.get_user(user_id=1)

        mock_repository.get.assert_called_once_with(1)
        assert result == mock_user
        assert result.id == 1

    def test_get_user_not_found(self, user_service, mock_repository):
        """GIVEN non-existing user_id / WHEN get_user() / THEN returns None"""
        mock_repository.get.return_value = None

        result = user_service.get_user(user_id=999)

        mock_repository.get.assert_called_once_with(999)
        assert result is None


class TestVerifyPassword:
    """Test verify_password method."""

    def test_verify_password_correct(self, user_service):
        """GIVEN correct password / WHEN verify_password() / THEN returns True"""
        # Créer un vrai User avec un mot de passe hashé
        user = User(
            username="testuser",
            email="test@epicevents.com",
            password_hash="",
            first_name="Jean",
            last_name="Dupont",
            phone="0612345678",
            department=Department.COMMERCIAL,
        )
        user.set_password("CorrectPassword123!")

        result = user_service.verify_password(user=user, password="CorrectPassword123!")

        assert result is True

    def test_verify_password_incorrect(self, user_service):
        """GIVEN incorrect password / WHEN verify_password() / THEN returns False"""
        user = User(
            username="testuser",
            email="test@epicevents.com",
            password_hash="",
            first_name="Jean",
            last_name="Dupont",
            phone="0612345678",
            department=Department.COMMERCIAL,
        )
        user.set_password("CorrectPassword123!")

        result = user_service.verify_password(user=user, password="WrongPassword456!")

        assert result is False

    def test_verify_password_empty(self, user_service):
        """GIVEN empty password / WHEN verify_password() / THEN returns False"""
        user = User(
            username="testuser",
            email="test@epicevents.com",
            password_hash="",
            first_name="Jean",
            last_name="Dupont",
            phone="0612345678",
            department=Department.COMMERCIAL,
        )
        user.set_password("CorrectPassword123!")

        result = user_service.verify_password(user=user, password="")

        assert result is False
