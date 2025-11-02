"""
Unit test for user creation.

This test verifies that:
- Users can be created in the database
- Passwords are correctly hashed with bcrypt via User.set_password()
- UNIQUE constraints work (username, email)
- Required fields are present
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models.user import Department, User


@pytest.fixture
def db_session():
    """Creates an in-memory SQLite database for tests."""
    # Temporary in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    # Complete resource cleanup
    session.close()
    engine.dispose()


def test_create_user_success(db_session):
    """
    GIVEN valid user data
    WHEN a user is created
    THEN it is correctly saved in the database
    """
    # Create the user
    user = User(
        username="testuser",
        email="test@epicevents.com",
        password_hash="",  # Temporary, will be set by set_password
        first_name="Test",
        last_name="User",
        phone="+33123456789",
        department=Department.COMMERCIAL
    )
    user.set_password("TestPassword123!")

    db_session.add(user)
    db_session.commit()

    # Verify that the user exists
    saved_user = db_session.query(User).filter_by(username="testuser").first()

    assert saved_user is not None
    assert saved_user.username == "testuser"
    assert saved_user.email == "test@epicevents.com"
    assert saved_user.first_name == "Test"
    assert saved_user.last_name == "User"
    assert saved_user.phone == "+33123456789"
    assert saved_user.department == Department.COMMERCIAL
    assert saved_user.id is not None


def test_password_is_hashed(db_session):
    """
    GIVEN a plain text password
    WHEN it is hashed and stored
    THEN the hash is valid and different from the original password
    """
    password = "MyPassword123!"

    user = User(
        username="testuser",
        email="test@epicevents.com",
        password_hash="",  # Temporary, will be set by set_password
        first_name="Test",
        last_name="User",
        phone="+33123456789",
        department=Department.GESTION
    )
    user.set_password(password)

    db_session.add(user)
    db_session.commit()

    # Verify that the hash is correct
    assert user.password_hash != password  # The hash is different from the password
    assert user.password_hash.startswith("$2b$")  # bcrypt format
    assert len(user.password_hash) == 60  # Standard bcrypt length


def test_password_verification(db_session):
    """
    GIVEN a user with a hashed password
    WHEN the password is verified
    THEN the correct password is accepted and the wrong one is rejected
    """
    password = "CorrectPassword123!"

    user = User(
        username="testuser",
        email="test@epicevents.com",
        password_hash="",  # Temporary, will be set by set_password
        first_name="Test",
        last_name="User",
        phone="+33123456789",
        department=Department.SUPPORT
    )
    user.set_password(password)

    db_session.add(user)
    db_session.commit()

    # Verify the correct password
    assert user.verify_password(password) is True

    # Verify a wrong password
    assert user.verify_password("WrongPassword!") is False


def test_create_multiple_users(db_session):
    """
    GIVEN multiple users from different departments
    WHEN they are created
    THEN all are present in the database
    """
    users_data = [
        ("admin", "admin@epicevents.com", Department.GESTION),
        ("commercial1", "commercial@epicevents.com", Department.COMMERCIAL),
        ("support1", "support@epicevents.com", Department.SUPPORT),
    ]

    for username, email, department in users_data:
        user = User(
            username=username,
            email=email,
            password_hash="",  # Temporary, will be set by set_password
            first_name="Test",
            last_name="User",
            phone="+33123456789",
            department=department
        )
        user.set_password("Password123!")
        db_session.add(user)

    db_session.commit()

    # Verify total count
    assert db_session.query(User).count() == 3

    # Verify each department
    assert db_session.query(User).filter_by(department=Department.GESTION).count() == 1
    assert db_session.query(User).filter_by(department=Department.COMMERCIAL).count() == 1
    assert db_session.query(User).filter_by(department=Department.SUPPORT).count() == 1


def test_username_must_be_unique(db_session):
    """
    GIVEN an existing user
    WHEN trying to create another user with the same username
    THEN an error is raised
    """
    # First user
    user1 = User(
        username="duplicate",
        email="user1@epicevents.com",
        password_hash="",  # Temporary, will be set by set_password
        first_name="User",
        last_name="One",
        phone="+33123456789",
        department=Department.COMMERCIAL
    )
    user1.set_password("Password123!")
    db_session.add(user1)
    db_session.commit()

    # Second user with the same username
    user2 = User(
        username="duplicate",  # Same username
        email="user2@epicevents.com",
        password_hash="",  # Temporary, will be set by set_password
        first_name="User",
        last_name="Two",
        phone="+33198765432",
        department=Department.COMMERCIAL
    )
    user2.set_password("Password123!")
    db_session.add(user2)

    # Should raise an exception
    with pytest.raises(Exception):
        db_session.commit()


def test_email_must_be_unique(db_session):
    """
    GIVEN an existing user
    WHEN trying to create another user with the same email
    THEN an error is raised
    """
    # First user
    user1 = User(
        username="user1",
        email="duplicate@epicevents.com",
        password_hash="",  # Temporary, will be set by set_password
        first_name="User",
        last_name="One",
        phone="+33123456789",
        department=Department.COMMERCIAL
    )
    user1.set_password("Password123!")
    db_session.add(user1)
    db_session.commit()

    # Second user with the same email
    user2 = User(
        username="user2",
        email="duplicate@epicevents.com",  # Same email
        password_hash="",  # Temporary, will be set by set_password
        first_name="User",
        last_name="Two",
        phone="+33198765432",
        department=Department.COMMERCIAL
    )
    user2.set_password("Password123!")
    db_session.add(user2)

    # Should raise an exception
    with pytest.raises(Exception):
        db_session.commit()


def test_user_has_timestamps(db_session):
    """
    GIVEN a new user
    WHEN it is created
    THEN created_at and updated_at are automatically set
    """
    user = User(
        username="testuser",
        email="test@epicevents.com",
        password_hash="",  # Temporary, will be set by set_password
        first_name="Test",
        last_name="User",
        phone="+33123456789",
        department=Department.COMMERCIAL
    )
    user.set_password("Password123!")

    db_session.add(user)
    db_session.commit()

    # Verify timestamps
    assert user.created_at is not None
    assert user.updated_at is not None


def test_user_repr(db_session):
    """
    GIVEN a user
    WHEN repr() is called on it
    THEN a readable representation is returned
    """
    user = User(
        username="testuser",
        email="test@epicevents.com",
        password_hash="",  # Temporary, will be set by set_password
        first_name="Test",
        last_name="User",
        phone="+33123456789",
        department=Department.COMMERCIAL
    )
    user.set_password("Password123!")

    db_session.add(user)
    db_session.commit()

    # Verify the representation
    repr_str = repr(user)
    assert "User" in repr_str
    assert "testuser" in repr_str
    assert "COMMERCIAL" in repr_str
