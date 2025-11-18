"""
Tests unitaires pour UserService.

Tests couverts:
- create_user() : création avec hachage bcrypt
- get_user() : récupération par ID
- verify_password() : vérification mot de passe
"""

import pytest

from src.models.user import Department, User
from src.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from src.services.user_service import UserService


@pytest.fixture
def user_service(db_session):
    """Create a UserService instance with real repository and SQLite DB."""
    repository = SqlAlchemyUserRepository(session=db_session)
    return UserService(repository=repository)


class TestCreateUser:
    """Test create_user method."""

    def test_create_user_success(self, user_service, db_session):
        """GIVEN valid user data / WHEN create_user() / THEN user created with hashed password"""
        result = user_service.create_user(
            username="testuser",
            email="test@epicevents.com",
            password="MySecurePass123!",
            first_name="Jean",
            last_name="Dupont",
            phone="0612345678",
            department=Department.COMMERCIAL,
        )

        # Verify user was created
        assert isinstance(result, User)
        assert result.id is not None
        assert result.username == "testuser"
        assert result.email == "test@epicevents.com"
        assert result.first_name == "Jean"
        assert result.last_name == "Dupont"
        assert result.phone == "0612345678"
        assert result.department == Department.COMMERCIAL
        # Verify password was hashed with bcrypt
        assert result.password_hash != ""
        assert result.password_hash.startswith("$2b$")

        # Verify it's persisted in database
        db_user = db_session.query(User).filter_by(username="testuser").first()
        assert db_user is not None
        assert db_user.id == result.id
        assert db_user.email == "test@epicevents.com"
        # Verify password hash is persisted
        assert db_user.password_hash.startswith("$2b$")

    def test_create_user_gestion_department(self, user_service, db_session):
        """GIVEN GESTION department / WHEN create_user() / THEN user created with GESTION"""
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

        # Verify persistence
        db_user = db_session.query(User).filter_by(username="gestion1").first()
        assert db_user.department == Department.GESTION

    def test_create_user_support_department(self, user_service, db_session):
        """GIVEN SUPPORT department / WHEN create_user() / THEN user created with SUPPORT"""
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

        # Verify persistence
        db_user = db_session.query(User).filter_by(username="support1").first()
        assert db_user.department == Department.SUPPORT


class TestGetUser:
    """Test get_user method."""

    def test_get_user_found(self, user_service, test_users):
        """GIVEN existing user_id / WHEN get_user() / THEN returns user"""
        commercial1 = test_users["commercial1"]

        result = user_service.get_user(user_id=commercial1.id)

        assert result is not None
        assert result.id == commercial1.id
        assert result.username == "commercial1"
        assert result.email == "commercial1@epicevents.com"
        assert result.department == Department.COMMERCIAL

    def test_get_user_not_found(self, user_service):
        """GIVEN non-existing user_id / WHEN get_user() / THEN returns None"""
        result = user_service.get_user(user_id=99999)

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
