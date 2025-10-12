"""
Script pour tester le hashing et la vérification des mots de passe.

Usage:
    poetry run python test_password_hash.py
"""
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.user import User

def test_password_verification():
    """Test de vérification des mots de passe."""

    # Connexion à la base
    engine = create_engine("sqlite:///epic_events.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    print("\n" + "=" * 60)
    print("TEST DE VERIFICATION DES MOTS DE PASSE")
    print("=" * 60 + "\n")

    # Test pour chaque utilisateur
    test_cases = [
        ("admin", "Admin123!"),
        ("commercial1", "Commercial123!"),
        ("support1", "Support123!"),
    ]

    for username, password in test_cases:
        user = session.query(User).filter_by(username=username).first()

        if user:
            # Vérifier le bon mot de passe
            password_bytes = password.encode('utf-8')
            hash_bytes = user.password_hash.encode('utf-8')
            is_valid = bcrypt.checkpw(password_bytes, hash_bytes)
            status = "OK" if is_valid else "ERREUR"
            print(f"[{status}] {username}: Mot de passe correct -> {is_valid}")

            # Vérifier un mauvais mot de passe
            wrong_password_bytes = "WrongPassword123!".encode('utf-8')
            is_invalid = bcrypt.checkpw(wrong_password_bytes, hash_bytes)
            status = "OK" if not is_invalid else "ERREUR"
            print(f"[{status}] {username}: Mauvais mot de passe -> {is_invalid} (devrait etre False)")
        else:
            print(f"[ERREUR] Utilisateur '{username}' introuvable")

        print()

    session.close()

    print("=" * 60)
    print("Test termine")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    test_password_verification()
