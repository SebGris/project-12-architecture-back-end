"""
Integration tests for SqlAlchemyUserRepository.

These tests use a real SQLAlchemy session with an in-memory SQLite database
to verify the repository implementation works correctly with the database.
"""

import pytest

from src.models.user import Department, User
from src.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)
from src.services.password_hashing_service import PasswordHashingService


@pytest.fixture
def user_repository(db_session):
    """Create a UserRepository with the test database session."""
    return SqlAlchemyUserRepository(session=db_session)


class TestUserRepositoryGet:
    """Test get method."""

    def test_get_existing_user(self, user_repository, test_users):
        """GIVEN existing user / WHEN get(user_id) / THEN returns user"""
        admin = test_users["admin"]

        result = user_repository.get(admin.id)

        assert result is not None
        assert result.id == admin.id
        assert result.username == "admin"
        assert result.department == Department.GESTION

    def test_get_nonexistent_user(self, user_repository):
        """GIVEN nonexistent user_id / WHEN get() / THEN returns None"""
        result = user_repository.get(99999)

        assert result is None


class TestUserRepositoryGetByUsername:
    """Test get_by_username method."""

    def test_get_by_username_existing(self, user_repository, test_users):
        """GIVEN existing username / WHEN get_by_username() / THEN returns user"""
        result = user_repository.get_by_username("commercial1")

        assert result is not None
        assert result.username == "commercial1"
        assert result.department == Department.COMMERCIAL

    def test_get_by_username_nonexistent(self, user_repository):
        """GIVEN nonexistent username / WHEN get_by_username() / THEN returns None"""
        result = user_repository.get_by_username("nonexistent")

        assert result is None


class TestUserRepositoryGetByEmail:
    """Test get_by_email method."""

    def test_get_by_email_existing(self, user_repository, test_users):
        """GIVEN existing email / WHEN get_by_email() / THEN returns user"""
        result = user_repository.get_by_email("admin@epicevents.com")

        assert result is not None
        assert result.email == "admin@epicevents.com"
        assert result.username == "admin"

    def test_get_by_email_nonexistent(self, user_repository):
        """GIVEN nonexistent email / WHEN get_by_email() / THEN returns None"""
        result = user_repository.get_by_email("nonexistent@example.com")

        assert result is None


class TestUserRepositoryAdd:
    """Test add method."""

    def test_add_new_user(self, user_repository, db_session):
        """GIVEN new user / WHEN add() / THEN user saved with ID"""
        password_service = PasswordHashingService()
        new_user = User(
            username="newuser",
            email="newuser@epicevents.com",
            first_name="New",
            last_name="User",
            phone="0123456789",
            department=Department.COMMERCIAL,
            password_hash=password_service.hash_password("SecurePass123!"),
        )

        result = user_repository.add(new_user)

        assert result.id is not None
        assert result.username == "newuser"

        # Verify it's in database
        db_user = db_session.query(User).filter_by(username="newuser").first()
        assert db_user is not None
        assert db_user.id == result.id


class TestUserRepositoryUpdate:
    """Test update method."""

    def test_update_user(self, user_repository, test_users, db_session):
        """GIVEN existing user with changes / WHEN update() / THEN changes persisted"""
        user = test_users["commercial1"]
        user.phone = "0999999999"
        user.email = "newemail@epicevents.com"

        result = user_repository.update(user)

        assert result.phone == "0999999999"
        assert result.email == "newemail@epicevents.com"

        # Verify changes persisted
        db_session.expire_all()
        db_user = db_session.query(User).filter_by(id=user.id).first()
        assert db_user.phone == "0999999999"
        assert db_user.email == "newemail@epicevents.com"


class TestUserRepositoryExists:
    """Test exists method."""

    def test_exists_returns_true_for_existing_user(self, user_repository, test_users):
        """GIVEN existing user / WHEN exists() / THEN returns True"""
        admin = test_users["admin"]

        result = user_repository.exists(admin.id)

        assert result is True

    def test_exists_returns_false_for_nonexistent_user(self, user_repository):
        """GIVEN nonexistent user_id / WHEN exists() / THEN returns False"""
        result = user_repository.exists(99999)

        assert result is False


class TestUserRepositoryUsernameExists:
    """Test username_exists method."""

    def test_username_exists_returns_true(self, user_repository, test_users):
        """GIVEN existing username / WHEN username_exists() / THEN returns True"""
        result = user_repository.username_exists("admin")

        assert result is True

    def test_username_exists_returns_false(self, user_repository):
        """GIVEN nonexistent username / WHEN username_exists() / THEN returns False"""
        result = user_repository.username_exists("nonexistent_user")

        assert result is False

    def test_username_exists_excludes_id(self, user_repository, test_users):
        """GIVEN existing username with exclude_id / WHEN username_exists() / THEN returns False"""
        admin = test_users["admin"]

        # Username exists but we exclude admin's ID (for update scenario)
        result = user_repository.username_exists("admin", exclude_id=admin.id)

        assert result is False


class TestUserRepositoryEmailExists:
    """Test email_exists method."""

    def test_email_exists_returns_true(self, user_repository, test_users):
        """GIVEN existing email / WHEN email_exists() / THEN returns True"""
        result = user_repository.email_exists("admin@epicevents.com")

        assert result is True

    def test_email_exists_returns_false(self, user_repository):
        """GIVEN nonexistent email / WHEN email_exists() / THEN returns False"""
        result = user_repository.email_exists("nonexistent@email.com")

        assert result is False

    def test_email_exists_excludes_id(self, user_repository, test_users):
        """GIVEN existing email with exclude_id / WHEN email_exists() / THEN returns False"""
        admin = test_users["admin"]

        # Email exists but we exclude admin's ID (for update scenario)
        result = user_repository.email_exists(
            "admin@epicevents.com", exclude_id=admin.id
        )

        assert result is False
