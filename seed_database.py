"""
Script de seed pour peupler la base de données Epic Events CRM.
Crée des utilisateurs de test pour chaque département.

Usage:
    poetry run python seed_database.py

Attention: Ce script écrasera les données existantes !
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt

from src.models.user import User, Department


def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt."""
    # Convertir le mot de passe en bytes
    password_bytes = password.encode("utf-8")
    # Générer le salt et hasher
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Retourner le hash en string
    return hashed.decode("utf-8")


def create_users(session):
    """Crée les utilisateurs de test."""

    print("\n" + "=" * 60)
    print("CREATION DES UTILISATEURS DE TEST")
    print("=" * 60)

    users_data = [
        {
            "username": "admin",
            "email": "admin@epicevents.com",
            "password": "Admin123!",  # Mot de passe temporaire
            "first_name": "Alice",
            "last_name": "Dubois",
            "phone": "+33123456789",
            "department": Department.GESTION,
        },
        {
            "username": "commercial1",
            "email": "john.smith@epicevents.com",
            "password": "Commercial123!",
            "first_name": "John",
            "last_name": "Smith",
            "phone": "+33198765432",
            "department": Department.COMMERCIAL,
        },
        {
            "username": "commercial2",
            "email": "marie.martin@epicevents.com",
            "password": "Commercial123!",
            "first_name": "Marie",
            "last_name": "Martin",
            "phone": "+33187654321",
            "department": Department.COMMERCIAL,
        },
        {
            "username": "support1",
            "email": "pierre.durand@epicevents.com",
            "password": "Support123!",
            "first_name": "Pierre",
            "last_name": "Durand",
            "phone": "+33176543210",
            "department": Department.SUPPORT,
        },
        {
            "username": "support2",
            "email": "sophie.bernard@epicevents.com",
            "password": "Support123!",
            "first_name": "Sophie",
            "last_name": "Bernard",
            "phone": "+33165432109",
            "department": Department.SUPPORT,
        },
    ]

    created_users = []

    for user_data in users_data:
        # Hash du mot de passe
        password = user_data.pop("password")
        password_hash = hash_password(password)

        # Création de l'utilisateur
        user = User(**user_data, password_hash=password_hash)

        session.add(user)
        created_users.append(
            (user_data["username"], password, user_data["department"])
        )
        print(
            f"- Utilisateur cree: {user_data['username']} ({user_data['department'].value})"
        )

    session.commit()

    print("\n" + "=" * 60)
    print(f"- {len(created_users)} utilisateurs crees avec succes !")
    print("=" * 60)

    return created_users


def display_credentials(users):
    """Affiche les identifiants de connexion."""

    print("\n" + "=" * 60)
    print("IDENTIFIANTS DE CONNEXION")
    print("=" * 60)
    print("\nIMPORTANT: Notez ces identifiants pour vos tests\n")

    for username, password, department in users:
        print(f"Departement: {department.value}")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print()

    print("=" * 60)
    print("Ces mots de passe sont temporaires.")
    print("En production, utilisez des mots de passe securises.")
    print("=" * 60)


def verify_users(session):
    """Vérifie que les utilisateurs ont été créés."""

    print("\n" + "=" * 60)
    print("VERIFICATION DE LA BASE DE DONNEES")
    print("=" * 60)

    total = session.query(User).count()
    print(f"\nTotal d'utilisateurs: {total}")

    for department in Department:
        count = session.query(User).filter_by(department=department).count()
        print(f"  - {department.value}: {count} utilisateur(s)")

    print("\n" + "=" * 60)


def main():
    """Point d'entrée principal du script."""

    print("\n" + "=" * 60)
    print("SEED DATABASE - Epic Events CRM")
    print("=" * 60)

    # Connexion à la base de données
    engine = create_engine("sqlite:///data/epic_events_crm.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Supprimer les utilisateurs existants (optionnel)
        print("\nSuppression des utilisateurs existants...")
        session.query(User).delete()
        session.commit()
        print("- Utilisateurs existants supprimes")

        # Créer les utilisateurs
        users = create_users(session)

        # Afficher les identifiants
        display_credentials(users)

        # Vérifier
        verify_users(session)

        print("\nSEED TERMINE AVEC SUCCES !")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\nERREUR: {e}")
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()
