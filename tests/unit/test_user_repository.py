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
        new_user = User(
            username="newuser",
            email="newuser@epicevents.com",
            first_name="New",
            last_name="User",
            phone="0123456789",
            department=Department.COMMERCIAL,
        )
        new_user.set_password("SecurePass123!")

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
