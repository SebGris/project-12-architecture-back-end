"""Unit tests for UserService.

Tests covered:
- create_user(): User creation with bcrypt password hashing
- get_user(): User retrieval by ID
- list_users(): All users listing
- update_user(): User information updates
- delete_user(): User deletion

Implementation notes:
- Uses real SQLite in-memory database
- Zero mocks - uses real SqlAlchemyUserRepository
- Tests business logic layer with real database objects
"""

import pytest

from src.models.user import Department, User
from src.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)
from src.services.user_service import UserService
from src.services.password_hashing_service import PasswordHashingService


@pytest.fixture
def password_service():
    """Create a PasswordHashingService instance."""
    return PasswordHashingService()


@pytest.fixture
def user_service(db_session, password_service):
    """Create a UserService instance with real repository and SQLite DB."""
    repository = SqlAlchemyUserRepository(session=db_session)
    return UserService(repository=repository, password_service=password_service)


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

    @pytest.mark.parametrize(
        "username,email,department",
        [
            ("gestion1", "gestion@epicevents.com", Department.GESTION),
            ("support1", "support@epicevents.com", Department.SUPPORT),
        ],
        ids=["gestion", "support"],
    )
    def test_create_user_departments(
        self, user_service, db_session, username, email, department
    ):
        """Test create_user with different departments."""
        result = user_service.create_user(
            username=username,
            email=email,
            password="Password123!",
            first_name="Test",
            last_name="User",
            phone="0123456789",
            department=department,
        )

        assert result.department == department

        # Verify persistence
        db_user = db_session.query(User).filter_by(username=username).first()
        assert db_user.department == department


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


class TestUpdateUser:
    """Test update_user method."""

    def test_update_user_all_fields(
        self, user_service, test_users, db_session
    ):
        """GIVEN user_id and all fields / WHEN update_user() / THEN user updated"""
        commercial1 = test_users["commercial1"]

        result = user_service.update_user(
            user_id=commercial1.id,
            username="commercial_updated",
            email="updated@epicevents.com",
            first_name="Updated",
            last_name="Name",
            phone="+33 9 99 99 99 99",
            department=Department.GESTION,
        )

        # Verify updates
        assert result is not None
        assert result.username == "commercial_updated"
        assert result.email == "updated@epicevents.com"
        assert result.first_name == "Updated"
        assert result.last_name == "Name"
        assert result.phone == "+33 9 99 99 99 99"
        assert result.department == Department.GESTION

        # Verify persistence
        db_session.expire_all()
        db_user = db_session.query(User).filter_by(id=commercial1.id).first()
        assert db_user.username == "commercial_updated"
        assert db_user.department == Department.GESTION

    def test_update_user_partial_fields(self, user_service, test_users):
        """GIVEN user_id and some fields / WHEN update_user() / THEN only those fields updated"""
        support1 = test_users["support1"]
        original_username = support1.username

        result = user_service.update_user(
            user_id=support1.id,
            email="newemail@epicevents.com",
            phone="+33 2 22 22 22 22",
        )

        # Verify partial update
        assert result.email == "newemail@epicevents.com"
        assert result.phone == "+33 2 22 22 22 22"
        # Username should be unchanged
        assert result.username == original_username

    def test_update_user_not_found(self, user_service):
        """GIVEN non-existing user_id / WHEN update_user() / THEN returns None"""
        result = user_service.update_user(user_id=99999, username="newname")

        assert result is None

    def test_update_user_only_department(
        self, user_service, test_users, db_session
    ):
        """GIVEN user_id and department / WHEN update_user() / THEN only department updated"""
        commercial2 = test_users["commercial2"]

        result = user_service.update_user(
            user_id=commercial2.id, department=Department.SUPPORT
        )

        assert result.department == Department.SUPPORT

        # Verify persistence
        db_session.expire_all()
        db_user = db_session.query(User).filter_by(id=commercial2.id).first()
        assert db_user.department == Department.SUPPORT


class TestDeleteUser:
    """Test delete_user method."""

    def test_delete_user_success(self, user_service, test_users, db_session):
        """GIVEN existing user_id / WHEN delete_user() / THEN returns True and user deleted"""
        support2 = test_users["support2"]
        user_id = support2.id

        result = user_service.delete_user(user_id=user_id)

        # Verify deletion returned True
        assert result is True

        # Verify user is deleted from database
        db_user = db_session.query(User).filter_by(id=user_id).first()
        assert db_user is None

    def test_delete_user_not_found(self, user_service):
        """GIVEN non-existing user_id / WHEN delete_user() / THEN returns False"""
        result = user_service.delete_user(user_id=99999)

        assert result is False


class TestVerifyPassword:
    """Test verify_password method."""

    def test_verify_password_correct(self, user_service):
        """GIVEN user with hashed password / WHEN verify_password() with correct password / THEN returns True"""
        user = user_service.create_user(
            username="passtest",
            email="passtest@epicevents.com",
            password="MyPassword123!",
            first_name="Test",
            last_name="User",
            phone="0600000000",
            department=Department.COMMERCIAL,
        )

        result = user_service.verify_password(user, "MyPassword123!")

        assert result is True

    def test_verify_password_incorrect(self, user_service):
        """GIVEN user with hashed password / WHEN verify_password() with wrong password / THEN returns False"""
        user = user_service.create_user(
            username="passtest2",
            email="passtest2@epicevents.com",
            password="MyPassword123!",
            first_name="Test",
            last_name="User",
            phone="0600000001",
            department=Department.COMMERCIAL,
        )

        result = user_service.verify_password(user, "WrongPassword!")

        assert result is False


class TestSetPassword:
    """Test set_password method."""

    def test_set_password_updates_hash(self, user_service):
        """GIVEN user / WHEN set_password() / THEN password_hash is updated"""
        user = user_service.create_user(
            username="setpasstest",
            email="setpasstest@epicevents.com",
            password="OldPassword123!",
            first_name="Test",
            last_name="User",
            phone="0600000002",
            department=Department.SUPPORT,
        )
        old_hash = user.password_hash

        user_service.set_password(user, "NewPassword456!")

        # Hash should be different
        assert user.password_hash != old_hash
        # New password should verify
        assert user_service.verify_password(user, "NewPassword456!")
        # Old password should not verify
        assert not user_service.verify_password(user, "OldPassword123!")


class TestUserServiceExists:
    """Test exists method."""

    @pytest.mark.parametrize(
        "get_id,expected",
        [("existing", True), ("nonexistent", False)],
        ids=["existing", "nonexistent"],
    )
    def test_exists(self, user_service, test_users, get_id, expected):
        """Test exists returns correct boolean for existing/nonexistent users."""
        user_id = test_users["admin"].id if get_id == "existing" else 99999
        result = user_service.exists(user_id)
        assert result is expected


class TestUsernameExists:
    """Test username_exists method."""

    @pytest.mark.parametrize(
        "username,exclude_id,expected",
        [
            ("admin", None, True),
            ("nonexistent_user", None, False),
            ("admin", "admin", False),
        ],
        ids=["exists", "not_exists", "excluded"],
    )
    def test_username_exists(
        self, user_service, test_users, username, exclude_id, expected
    ):
        """Test username_exists with various scenarios."""
        exclude = test_users["admin"].id if exclude_id == "admin" else None
        result = user_service.username_exists(username, exclude_id=exclude)
        assert result is expected


class TestEmailExists:
    """Test email_exists method."""

    @pytest.mark.parametrize(
        "email,exclude_id,expected",
        [
            ("admin@epicevents.com", None, True),
            ("nonexistent@email.com", None, False),
            ("admin@epicevents.com", "admin", False),
        ],
        ids=["exists", "not_exists", "excluded"],
    )
    def test_email_exists(self, user_service, test_users, email, exclude_id, expected):
        """Test email_exists with various scenarios."""
        exclude = test_users["admin"].id if exclude_id == "admin" else None
        result = user_service.email_exists(email, exclude_id=exclude)
        assert result is expected
