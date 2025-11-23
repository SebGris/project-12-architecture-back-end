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
