"""
Test unitaire pour la création des utilisateurs.

Ce test vérifie que :
- Les utilisateurs peuvent être créés dans la base de données
- Les mots de passe sont correctement hashés avec bcrypt
- Les contraintes UNIQUE fonctionnent (username, email)
- Les champs requis sont présents
"""
import pytest
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base
from src.models.user import User, Department


@pytest.fixture
def db_session():
    """Crée une base de données SQLite en mémoire pour les tests."""
    # Base de données temporaire en mémoire
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


def test_create_user_success(db_session):
    """
    GIVEN des données utilisateur valides
    WHEN un utilisateur est créé
    THEN il est sauvegardé correctement dans la base de données
    """
    # Préparer les données
    password = "TestPassword123!"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Créer l'utilisateur
    user = User(
        username="testuser",
        email="test@epicevents.com",
        password_hash=password_hash,
        first_name="Test",
        last_name="User",
        phone="+33123456789",
        department=Department.COMMERCIAL
    )

    db_session.add(user)
    db_session.commit()

    # Vérifier que l'utilisateur existe
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
    GIVEN un mot de passe en clair
    WHEN il est hashé et stocké
    THEN le hash est valide et différent du mot de passe original
    """
    password = "MyPassword123!"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = User(
        username="testuser",
        email="test@epicevents.com",
        password_hash=password_hash,
        first_name="Test",
        last_name="User",
        phone="+33123456789",
        department=Department.GESTION
    )

    db_session.add(user)
    db_session.commit()

    # Vérifier que le hash est correct
    assert user.password_hash != password  # Le hash est différent du mot de passe
    assert user.password_hash.startswith("$2b$")  # Format bcrypt
    assert len(user.password_hash) == 60  # Longueur standard bcrypt


def test_password_verification(db_session):
    """
    GIVEN un utilisateur avec un mot de passe hashé
    WHEN on vérifie le mot de passe
    THEN le bon mot de passe est accepté et le mauvais est rejeté
    """
    password = "CorrectPassword123!"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = User(
        username="testuser",
        email="test@epicevents.com",
        password_hash=password_hash,
        first_name="Test",
        last_name="User",
        phone="+33123456789",
        department=Department.SUPPORT
    )

    db_session.add(user)
    db_session.commit()

    # Vérifier le bon mot de passe
    is_valid = bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))
    assert is_valid is True

    # Vérifier un mauvais mot de passe
    is_invalid = bcrypt.checkpw(b"WrongPassword!", user.password_hash.encode('utf-8'))
    assert is_invalid is False


def test_create_multiple_users(db_session):
    """
    GIVEN plusieurs utilisateurs de départements différents
    WHEN ils sont créés
    THEN tous sont présents dans la base de données
    """
    users_data = [
        ("admin", "admin@epicevents.com", Department.GESTION),
        ("commercial1", "commercial@epicevents.com", Department.COMMERCIAL),
        ("support1", "support@epicevents.com", Department.SUPPORT),
    ]

    for username, email, department in users_data:
        password_hash = bcrypt.hashpw(b"Password123!", bcrypt.gensalt()).decode('utf-8')

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            first_name="Test",
            last_name="User",
            phone="+33123456789",
            department=department
        )
        db_session.add(user)

    db_session.commit()

    # Vérifier le nombre total
    assert db_session.query(User).count() == 3

    # Vérifier chaque département
    assert db_session.query(User).filter_by(department=Department.GESTION).count() == 1
    assert db_session.query(User).filter_by(department=Department.COMMERCIAL).count() == 1
    assert db_session.query(User).filter_by(department=Department.SUPPORT).count() == 1


def test_username_must_be_unique(db_session):
    """
    GIVEN un utilisateur existant
    WHEN on essaie de créer un autre utilisateur avec le même username
    THEN une erreur est levée
    """
    password_hash = bcrypt.hashpw(b"Password123!", bcrypt.gensalt()).decode('utf-8')

    # Premier utilisateur
    user1 = User(
        username="duplicate",
        email="user1@epicevents.com",
        password_hash=password_hash,
        first_name="User",
        last_name="One",
        phone="+33123456789",
        department=Department.COMMERCIAL
    )
    db_session.add(user1)
    db_session.commit()

    # Deuxième utilisateur avec le même username
    user2 = User(
        username="duplicate",  # Même username
        email="user2@epicevents.com",
        password_hash=password_hash,
        first_name="User",
        last_name="Two",
        phone="+33198765432",
        department=Department.COMMERCIAL
    )
    db_session.add(user2)

    # Doit lever une exception
    with pytest.raises(Exception):
        db_session.commit()


def test_email_must_be_unique(db_session):
    """
    GIVEN un utilisateur existant
    WHEN on essaie de créer un autre utilisateur avec le même email
    THEN une erreur est levée
    """
    password_hash = bcrypt.hashpw(b"Password123!", bcrypt.gensalt()).decode('utf-8')

    # Premier utilisateur
    user1 = User(
        username="user1",
        email="duplicate@epicevents.com",
        password_hash=password_hash,
        first_name="User",
        last_name="One",
        phone="+33123456789",
        department=Department.COMMERCIAL
    )
    db_session.add(user1)
    db_session.commit()

    # Deuxième utilisateur avec le même email
    user2 = User(
        username="user2",
        email="duplicate@epicevents.com",  # Même email
        password_hash=password_hash,
        first_name="User",
        last_name="Two",
        phone="+33198765432",
        department=Department.COMMERCIAL
    )
    db_session.add(user2)

    # Doit lever une exception
    with pytest.raises(Exception):
        db_session.commit()


def test_user_has_timestamps(db_session):
    """
    GIVEN un nouvel utilisateur
    WHEN il est créé
    THEN created_at et updated_at sont automatiquement définis
    """
    password_hash = bcrypt.hashpw(b"Password123!", bcrypt.gensalt()).decode('utf-8')

    user = User(
        username="testuser",
        email="test@epicevents.com",
        password_hash=password_hash,
        first_name="Test",
        last_name="User",
        phone="+33123456789",
        department=Department.COMMERCIAL
    )

    db_session.add(user)
    db_session.commit()

    # Vérifier les timestamps
    assert user.created_at is not None
    assert user.updated_at is not None


def test_user_repr(db_session):
    """
    GIVEN un utilisateur
    WHEN on appelle repr() dessus
    THEN une représentation lisible est retournée
    """
    password_hash = bcrypt.hashpw(b"Password123!", bcrypt.gensalt()).decode('utf-8')

    user = User(
        username="testuser",
        email="test@epicevents.com",
        password_hash=password_hash,
        first_name="Test",
        last_name="User",
        phone="+33123456789",
        department=Department.COMMERCIAL
    )

    db_session.add(user)
    db_session.commit()

    # Vérifier la représentation
    repr_str = repr(user)
    assert "User" in repr_str
    assert "testuser" in repr_str
    assert "COMMERCIAL" in repr_str
