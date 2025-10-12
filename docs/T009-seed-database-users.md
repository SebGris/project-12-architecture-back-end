# T009: Seed Database - Création des utilisateurs de test

## Description
Créer un script de seed pour peupler la base de données avec des utilisateurs de test, permettant de tester l'authentification et les fonctionnalités de l'application.

## Contexte
Cette tâche intervient après la création des tables (T008). La base de données existe mais est vide. Nous devons créer des comptes utilisateurs de test pour chaque département (GESTION, COMMERCIAL, SUPPORT) afin de pouvoir développer et tester les fonctionnalités de l'application.

## Objectif
- Créer un script `seed_database.py` réutilisable
- Implémenter le hashing sécurisé des mots de passe avec bcrypt
- Ajouter au minimum 5 utilisateurs de test (1 admin, 2 commerciaux, 2 support)
- Vérifier que les utilisateurs sont correctement créés
- Documenter les identifiants pour les tests

---

## Prérequis

### Dépendances nécessaires

Le projet utilise déjà **passlib[bcrypt]** (voir `pyproject.toml`) pour le hashing des mots de passe.

Vérifiez que c'est installé :
```bash
poetry show | findstr passlib
```

Si ce n'est pas installé :
```bash
poetry add "passlib[bcrypt]"
```

---

## Étape 1 : Créer le script de seed

### Créer le fichier `seed_database.py` à la racine du projet

```python
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

# Import des modèles
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
    engine = create_engine("sqlite:///epic_events.db")
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
```

---

## Étape 2 : Exécuter le script de seed

### Commande à exécuter

```bash
poetry run python seed_database.py
```

### Sortie attendue

```
============================================================
SEED DATABASE - Epic Events CRM
============================================================

⚠️  Suppression des utilisateurs existants...
✓ Utilisateurs existants supprimés

============================================================
CRÉATION DES UTILISATEURS DE TEST
============================================================
✓ Utilisateur créé: admin (GESTION)
✓ Utilisateur créé: commercial1 (COMMERCIAL)
✓ Utilisateur créé: commercial2 (COMMERCIAL)
✓ Utilisateur créé: support1 (SUPPORT)
✓ Utilisateur créé: support2 (SUPPORT)

============================================================
✓ 5 utilisateurs créés avec succès !
============================================================

============================================================
IDENTIFIANTS DE CONNEXION
============================================================

⚠️  IMPORTANT: Notez ces identifiants pour vos tests

Département: GESTION
  Username: admin
  Password: Admin123!

Département: COMMERCIAL
  Username: commercial1
  Password: Commercial123!

Département: COMMERCIAL
  Username: commercial2
  Password: Commercial123!

Département: SUPPORT
  Username: support1
  Password: Support123!

Département: SUPPORT
  Username: support2
  Password: Support123!

============================================================
⚠️  Ces mots de passe sont temporaires.
⚠️  En production, utilisez des mots de passe sécurisés.
============================================================

============================================================
VÉRIFICATION DE LA BASE DE DONNÉES
============================================================

Total d'utilisateurs: 5
  - GESTION: 1 utilisateur(s)
  - COMMERCIAL: 2 utilisateur(s)
  - SUPPORT: 2 utilisateur(s)

============================================================

✅ SEED TERMINÉ AVEC SUCCÈS !
============================================================
```

---

## Étape 3 : Vérifier dans la base de données

### Option A : Utiliser le script `check_db.py`

Ajoutez cette fonction au script existant `check_db.py` :

```python
# Ajouter à la fin de check_db.py
from sqlalchemy.orm import sessionmaker

# ... après la partie inspection des tables ...

# Afficher les utilisateurs créés
Session = sessionmaker(bind=engine)
session = Session()

print("\n" + "=" * 50)
print("UTILISATEURS DANS LA BASE DE DONNÉES")
print("=" * 50)

from src.models.user import User

users = session.query(User).all()
for user in users:
    print(f"  - {user.username:<15} | {user.email:<30} | {user.department.value}")

session.close()
```

Exécutez :
```bash
poetry run python check_db.py
```

### Option B : Utiliser DB Browser for SQLite

1. Ouvrez DB Browser for SQLite
2. Ouvrez `epic_events.db`
3. Onglet **"Browse Data"** → Sélectionnez la table **"users"**
4. Vous devriez voir les 5 utilisateurs

**Colonnes visibles** :
- `id`: 1, 2, 3, 4, 5
- `username`: admin, commercial1, commercial2, support1, support2
- `email`: Les emails correspondants
- `password_hash`: Les hash bcrypt (commencent par `$2b$12$...`)
- `department`: GESTION, COMMERCIAL, SUPPORT

### Option C : Requête SQL directe

Dans DB Browser, onglet **"Execute SQL"** :

```sql
SELECT
    id,
    username,
    email,
    department,
    first_name || ' ' || last_name as full_name,
    phone,
    created_at
FROM users
ORDER BY department, username;
```

---

## Étape 4 : Tester le hashing des mots de passe

Pour vérifier que le hashing fonctionne correctement, créez un script de test `test_password_hash.py` :

```python
"""
Script pour tester le hashing et la vérification des mots de passe.
"""
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.user import User

# Configuration bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_password_verification():
    """Test de vérification des mots de passe."""

    # Connexion à la base
    engine = create_engine("sqlite:///epic_events.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    print("\n" + "=" * 60)
    print("TEST DE VÉRIFICATION DES MOTS DE PASSE")
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
            is_valid = pwd_context.verify(password, user.password_hash)
            print(f"✓ {username}: Mot de passe correct → {is_valid}")

            # Vérifier un mauvais mot de passe
            is_invalid = pwd_context.verify("WrongPassword123!", user.password_hash)
            print(f"  {username}: Mauvais mot de passe → {is_invalid} (devrait être False)")
        else:
            print(f"❌ Utilisateur '{username}' introuvable")

        print()

    session.close()

    print("=" * 60)
    print("✅ Test terminé")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    test_password_verification()
```

Exécutez :
```bash
poetry run python test_password_hash.py
```

**Sortie attendue** :
```
============================================================
TEST DE VÉRIFICATION DES MOTS DE PASSE
============================================================

✓ admin: Mot de passe correct → True
  admin: Mauvais mot de passe → False (devrait être False)

✓ commercial1: Mot de passe correct → True
  commercial1: Mauvais mot de passe → False (devrait être False)

✓ support1: Mot de passe correct → True
  support1: Mauvais mot de passe → False (devrait être False)

============================================================
✅ Test terminé
============================================================
```

---

## Comprendre bcrypt et le hashing

### Pourquoi bcrypt ?

**🔒 Sécurité** :
- Résistant aux attaques par force brute (intentionnellement lent)
- Salage automatique intégré (chaque hash est unique)
- Algorithme éprouvé et recommandé par l'industrie

**Exemple de hash bcrypt** :
```
$2b$12$K3aBWzJQZDYV8qVX.aHJYeJ9QX8vDhZ5RqZ3x1BzYh2pX4Jq5NzKa
 │  │   │                                                     │
 │  │   │                                                     └─ Hash (31 caractères)
 │  │   └─────────────────────────────────────── Salt (22 caractères)
 │  └─ Work factor (nombre d'itérations = 2^12 = 4096)
 └─ Algorithme (2b = bcrypt)
```

**Propriétés importantes** :
- ✅ Même mot de passe → Hash différent à chaque fois (grâce au salt aléatoire)
- ✅ Impossible de déchiffrer le hash pour retrouver le mot de passe
- ✅ Vérification : `bcrypt.verify(password, hash)` → True/False

### Configuration de passlib

```python
from passlib.context import CryptContext

# Configuration recommandée
pwd_context = CryptContext(
    schemes=["bcrypt"],        # Algorithme utilisé
    deprecated="auto",         # Détecter les hash obsolètes
    bcrypt__default_rounds=12  # Work factor (optionnel, 12 par défaut)
)

# Hasher un mot de passe
hash = pwd_context.hash("MonMotDePasse123!")

# Vérifier un mot de passe
is_valid = pwd_context.verify("MonMotDePasse123!", hash)  # True
is_invalid = pwd_context.verify("MauvaisMDP", hash)       # False
```

---

## Identifiants de test créés

Pour référence rapide, voici les identifiants créés par le script :

| Username | Password | Email | Département | Permissions |
|----------|----------|-------|-------------|-------------|
| `admin` | `Admin123!` | admin@epicevents.com | GESTION | Toutes permissions |
| `commercial1` | `Commercial123!` | john.smith@epicevents.com | COMMERCIAL | Clients, Contrats |
| `commercial2` | `Commercial123!` | marie.martin@epicevents.com | COMMERCIAL | Clients, Contrats |
| `support1` | `Support123!` | pierre.durand@epicevents.com | SUPPORT | Événements |
| `support2` | `Support123!` | sophie.bernard@epicevents.com | SUPPORT | Événements |

**⚠️ Remarques importantes** :
- Ces mots de passe sont **temporaires** et pour **tests uniquement**
- En production, utilisez des mots de passe complexes et uniques
- Les utilisateurs devraient changer leur mot de passe au premier login

---

## Améliorer le modèle User (Optionnel)

Pour implémenter `set_password()` et `verify_password()` directement dans le modèle User :

### Mettre à jour `src/models/user.py`

```python
from passlib.context import CryptContext

# Configuration bcrypt (en haut du fichier, après les imports)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """User model representing employees of Epic Events."""

    __tablename__ = "users"

    # ... (colonnes existantes) ...

    def set_password(self, password: str) -> None:
        """Hash et définit le mot de passe."""
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Vérifie le mot de passe contre le hash."""
        return pwd_context.verify(password, self.password_hash)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', department={self.department})>"
```

### Script de seed simplifié avec les méthodes du modèle

```python
# Dans seed_database.py, remplacer la création d'utilisateur par :

for user_data in users_data:
    password = user_data.pop("password")

    # Création de l'utilisateur
    user = User(**user_data)
    user.set_password(password)  # ← Utilise la méthode du modèle

    session.add(user)
    # ...
```

---

## Résolution des problèmes courants

### Problème 1 : ImportError sur passlib

**Symptôme** :
```
ImportError: cannot import name 'CryptContext' from 'passlib.context'
```

**Solution** :
```bash
poetry add "passlib[bcrypt]"
poetry install
```

### Problème 2 : "bcrypt not installed"

**Symptôme** :
```
ValueError: bcrypt: bcrypt does not appear to be installed
```

**Solution** :
Le package `bcrypt` n'est pas installé. Assurez-vous d'installer `passlib[bcrypt]` avec les crochets :
```bash
poetry add "passlib[bcrypt]"
```

### Problème 3 : IntegrityError UNIQUE constraint

**Symptôme** :
```
sqlalchemy.exc.IntegrityError: UNIQUE constraint failed: users.username
```

**Cause** : Vous essayez de créer un utilisateur avec un username déjà existant.

**Solution** :
- Le script supprime automatiquement les utilisateurs existants
- Si vous ne voulez pas supprimer, commentez la ligne `session.query(User).delete()`
- Ou changez les usernames dans `users_data`

### Problème 4 : Les mots de passe ne fonctionnent pas

**Cause** : Le hash n'a peut-être pas été généré correctement.

**Vérification** :
```python
# Dans DB Browser, Execute SQL :
SELECT username, LENGTH(password_hash) as hash_length
FROM users;
```

**Attendu** : `hash_length` devrait être ~60 caractères (hash bcrypt).

Si ce n'est pas le cas, le mot de passe n'a pas été hashé correctement.

---

## Prochaines étapes

Une fois les utilisateurs créés, vous pourrez :

1. **Implémenter l'AuthService** (T010)
   - Login avec username/password
   - Génération de token JWT
   - Logout

2. **Créer des clients de test** (T011)
   - Lier les clients aux commerciaux
   - Données de démonstration

3. **Créer l'interface CLI** (T012)
   - Commande `epic-crm login`
   - Commande `epic-crm user list`

4. **Implémenter les permissions RBAC** (T013)
   - Vérifier le département de l'utilisateur
   - Autoriser/refuser les actions

---

## Fichiers créés

- ✅ `seed_database.py` : Script principal de seed
- ✅ `test_password_hash.py` : Test de vérification des mots de passe
- ✅ Mise à jour de `src/models/user.py` (optionnel)

---

## Critères de complétion

✅ Le script `seed_database.py` existe et s'exécute sans erreur
✅ 5 utilisateurs sont créés (1 GESTION, 2 COMMERCIAL, 2 SUPPORT)
✅ Les mots de passe sont hashés avec bcrypt
✅ La vérification des mots de passe fonctionne (test_password_hash.py)
✅ Les utilisateurs sont visibles dans DB Browser
✅ Les identifiants sont documentés pour les tests

---

## Pour le mentor OpenClassrooms

### Justification technique

**Pourquoi bcrypt ?**
- Standard de l'industrie pour le hashing de mots de passe
- Résistant aux attaques par force brute (intentionnellement lent)
- Salage automatique (chaque hash est unique, même pour le même mot de passe)
- Recommandé par OWASP et utilisé par Django, Flask, etc.

**Pourquoi un script de seed ?**
- Permet de recréer rapidement un environnement de test
- Essentiel pour les démonstrations et les présentations
- Facilite le développement (pas besoin de créer manuellement les utilisateurs)
- Bonne pratique en développement logiciel (fixtures)

**Sécurité** :
- Les mots de passe ne sont jamais stockés en clair
- Seuls les hash bcrypt sont dans la base de données
- Impossible de retrouver le mot de passe à partir du hash
- Work factor de 12 = 4096 itérations (équilibre sécurité/performance)

**Architecture** :
- Séparation des responsabilités : le modèle User ne contient pas de logique métier complexe
- Le script de seed est séparé du code applicatif
- Utilisation de SQLAlchemy ORM (pas de SQL brut)

---

## Statut
⏳ **À compléter** - En attente de création du script et exécution

## Date de création
2025-10-12
