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

    @pytest.mark.parametrize(
        "username,expected_found",
        [("commercial1", True), ("nonexistent", False)],
        ids=["existing", "nonexistent"],
    )
    def test_get_by_username(self, user_repository, test_users, username, expected_found):
        """Test get_by_username with existing and nonexistent usernames."""
        result = user_repository.get_by_username(username)

        if expected_found:
            assert result is not None
            assert result.username == username
        else:
            assert result is None


class TestUserRepositoryGetByEmail:
    """Test get_by_email method."""

    @pytest.mark.parametrize(
        "email,expected_found",
        [("admin@epicevents.com", True), ("nonexistent@example.com", False)],
        ids=["existing", "nonexistent"],
    )
    def test_get_by_email(self, user_repository, test_users, email, expected_found):
        """Test get_by_email with existing and nonexistent emails."""
        result = user_repository.get_by_email(email)

        if expected_found:
            assert result is not None
            assert result.email == email
        else:
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

    @pytest.mark.parametrize(
        "get_id,expected",
        [("existing", True), ("nonexistent", False)],
        ids=["existing", "nonexistent"],
    )
    def test_exists(self, user_repository, test_users, get_id, expected):
        """Test exists returns correct boolean for existing/nonexistent users."""
        user_id = test_users["admin"].id if get_id == "existing" else 99999
        result = user_repository.exists(user_id)
        assert result is expected


class TestUserRepositoryUsernameExists:
    """Test username_exists method."""

    @pytest.mark.parametrize(
        "username,exclude_id,expected",
        [
            ("admin", None, True),
            ("nonexistent_user", None, False),
            ("admin", "admin", False),  # exclude_id scenario
        ],
        ids=["exists", "not_exists", "excluded"],
    )
    def test_username_exists(
        self, user_repository, test_users, username, exclude_id, expected
    ):
        """Test username_exists with various scenarios."""
        exclude = test_users["admin"].id if exclude_id == "admin" else None
        result = user_repository.username_exists(username, exclude_id=exclude)
        assert result is expected


class TestUserRepositoryEmailExists:
    """Test email_exists method."""

    @pytest.mark.parametrize(
        "email,exclude_id,expected",
        [
            ("admin@epicevents.com", None, True),
            ("nonexistent@email.com", None, False),
            ("admin@epicevents.com", "admin", False),  # exclude_id scenario
        ],
        ids=["exists", "not_exists", "excluded"],
    )
    def test_email_exists(
        self, user_repository, test_users, email, exclude_id, expected
    ):
        """Test email_exists with various scenarios."""
        exclude = test_users["admin"].id if exclude_id == "admin" else None
        result = user_repository.email_exists(email, exclude_id=exclude)
        assert result is expected
