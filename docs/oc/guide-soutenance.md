# 🎯 GUIDE DE RÉVISION - EPIC EVENTS CRM

**Préparation soutenance OpenClassrooms - Projet 12**

---

## 📋 TABLE DES MATIÈRES

1. [Authentification & Sécurité](#1️⃣-authentification--sécurité)
2. [Protection contre l'injection SQL](#2️⃣-protection-contre-linjection-sql)
3. [Validation des données utilisateur](#3️⃣-validation-des-données-utilisateur)
4. [RBAC - Contrôle d'accès par rôle](#4️⃣-rbac-contrôle-daccès-par-rôle)
5. [Contraintes base de données](#5️⃣-contraintes-base-de-données)
6. [Architecture & Bonnes pratiques](#6️⃣-architecture--bonnes-pratiques)
7. [Checklist pour la soutenance](#-checklist-pour-la-soutenance)
8. [Démonstration en direct](#-démonstration-en-direct)
9. [Phrases clés à utiliser](#-phrases-clés-à-utiliser)

---

## 1️⃣ AUTHENTIFICATION & SÉCURITÉ

### A. Hachage de mot de passe (Protection contre fuites)

**Localisation:** `src/models/user.py` (lignes 58-77)

```python
# ✅ BONNE PRATIQUE : Utilisation de bcrypt pour hasher les mots de passe
def set_password(self, password: str) -> None:
    """Hash et stocke le mot de passe de manière sécurisée"""
    password_service = PasswordHashingService()
    self.password_hash = password_service.hash_password(password)

def verify_password(self, password: str) -> bool:
    """Vérifie le mot de passe sans jamais stocker le plain text"""
    password_service = PasswordHashingService()
    return password_service.verify_password(password, self.password_hash)
```

**Points clés à expliquer :**
- ❌ **Jamais** stocker les mots de passe en clair
- ✅ Utilisation de **bcrypt** (résistant au brute-force, salt automatique)
- ✅ Le hash est **unidirectionnel** (impossible de retrouver le mot de passe original)
- ✅ Chaque mot de passe a un **salt unique** généré automatiquement par bcrypt
- ✅ **Work factor** configurable pour ajuster la résistance au brute-force

**Pourquoi bcrypt ?**
- Conçu spécifiquement pour les mots de passe
- Lent intentionnellement (ralentit les attaques par force brute)
- Salt automatique inclus dans le hash
- Résistant aux attaques rainbow tables

---

### B. JWT pour l'authentification (Tokens sécurisés)

**Localisation:** `src/services/auth_service.py` (lignes 117-145)

```python
def generate_token(self, user: User) -> str:
    """Génère un JWT avec expiration de 24h"""
    now = datetime.now(timezone.utc)
    expiration = now + timedelta(hours=24)

    payload = {
        "user_id": user.id,
        "username": user.username,
        "department": user.department.value,
        "exp": expiration,  # ✅ Expiration automatique
        "iat": now          # ✅ Timestamp de création
    }

    # ✅ Algorithme sécurisé HS256 (pas HS512 qui a des vulnérabilités)
    token = jwt.encode(payload, self._secret_key, algorithm="HS256")
    return token
```

**Points clés à expliquer :**
- ✅ **Expiration** : Token valide 24h seulement (limite la fenêtre d'attaque)
- ✅ **Algorithme sécurisé** : HS256 (HMAC-SHA256)
- ✅ **Secret key** : Stockée dans variable d'environnement `EPICEVENTS_SECRET_KEY`
- ✅ **Stateless** : Pas besoin de stocker les sessions en BDD
- ✅ **Payload minimal** : Seulement les infos nécessaires (pas de données sensibles)

**Structure d'un JWT :**
```
Header.Payload.Signature
eyJhbGc...  .  eyJ1c2V...  .  SflKxwRJ...
(Base64)       (Base64)       (HMAC-SHA256)
```

---

### C. Validation des tokens

**Localisation:** `src/services/auth_service.py` (lignes 147-166)

```python
def validate_token(self, token: str) -> Optional[dict]:
    """Valide un JWT et retourne son payload"""
    try:
        payload = jwt.decode(
            token,
            self._secret_key,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        # ✅ Token expiré : refuser l'accès
        return None
    except jwt.InvalidTokenError:
        # ✅ Token invalide : refuser l'accès
        return None
```

**Points clés :**
- ✅ Gestion des **tokens expirés**
- ✅ Gestion des **tokens invalides/falsifiés**
- ✅ **Pas de confiance aveugle** : toujours valider
- ✅ **Algorithme whitelist** : Seul HS256 est accepté (évite les attaques par confusion d'algo)

**Stockage sécurisé du token :**
```python
# Fichier: ~/.epicevents/token
# Permissions: 0600 (lecture/écriture owner seulement)
TOKEN_FILE = Path.home() / ".epicevents" / "token"
```

---

## 2️⃣ PROTECTION CONTRE L'INJECTION SQL

### Utilisation de l'ORM SQLAlchemy (Requêtes paramétrées)

**Localisation:** `src/repositories/sqlalchemy_user_repository.py` (lignes 44-55)

```python
# ✅ SÉCURISÉ : SQLAlchemy utilise des requêtes paramétrées
def get_by_username(self, username: str) -> Optional[User]:
    """Récupère un utilisateur par son username"""
    # ✅ PAS d'injection SQL possible : username est échappé automatiquement
    return self.session.query(User).filter_by(username=username).first()

# ❌ DANGEREUX (exemple de ce qu'il NE FAUT PAS faire) :
# query = f"SELECT * FROM users WHERE username = '{username}'"
# # Un attaquant pourrait injecter : ' OR '1'='1
```

**Points clés à expliquer :**
- ✅ **ORM SQLAlchemy** : Échappement automatique des paramètres
- ✅ **Requêtes paramétrées** : Séparation entre code SQL et données
- ❌ **Jamais de concaténation** de strings SQL
- ✅ **filter_by()** utilise des placeholders sécurisés

**Exemple d'attaque par injection SQL (CE QU'ON ÉVITE) :**

```python
# ❌ CODE VULNÉRABLE (NE JAMAIS FAIRE)
username = "admin' OR '1'='1"
query = f"SELECT * FROM users WHERE username = '{username}'"
# Résultat SQL: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
# → Retourne TOUS les utilisateurs !

# ✅ AVEC SQLAlchemy (SÉCURISÉ)
session.query(User).filter_by(username=username).first()
# → Paramètre échappé automatiquement, pas d'injection possible
```

**Techniques de protection supplémentaires :**
- ✅ Utilisation exclusive de l'ORM (pas de raw SQL)
- ✅ Si raw SQL nécessaire : `session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})`
- ✅ Validation des inputs en amont (voir section validation)

---

## 3️⃣ VALIDATION DES DONNÉES UTILISATEUR

### A. Validation côté input (Première ligne de défense)

**Localisation:** `src/cli/validators.py` (lignes 46-51)

```python
def validate_email_callback(value: str) -> str:
    """Valide et nettoie l'email"""
    cleaned = value.strip().lower()
    # ✅ Regex stricte pour valider le format email
    if not EMAIL_PATTERN.match(cleaned):
        raise typer.BadParameter(f"Email invalide: {value}")
    return cleaned

# Pattern regex (ligne 9)
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
```

**Patterns de validation (lignes 8-18) :**

```python
# Email : format standard RFC 5322 (simplifié)
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Téléphone : chiffres, espaces, tirets, +, parenthèses, points
PHONE_PATTERN = re.compile(r"^[\d\s\-\+\(\)\.]+$")

# Username : lettres, chiffres, underscore, tiret (4-50 caractères)
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{4,50}$")

# Noms/Prénoms : lettres (avec accents), espaces, tirets, apostrophes
NAME_PATTERN = re.compile(r"^[a-zA-ZÀ-ÿ\s\-']+$")
```

**Points clés :**
- ✅ **Validation avec regex** : Format strict
- ✅ **Nettoyage** : `.strip()`, `.lower()`
- ✅ **Principe de moindre privilège** : Accepter uniquement les formats valides
- ✅ **Messages d'erreur explicites** pour l'utilisateur

---

### B. Validation métier (Business rules)

**Localisation:** `src/cli/validators.py` (lignes 137-157)

```python
def validate_contract_amounts(total_amount, remaining_amount) -> None:
    """Valide les règles métier des montants"""
    if total_amount < 0:
        raise ValueError("Le montant total doit être positif ou zéro")

    if remaining_amount < 0:
        raise ValueError("Le montant restant doit être positif ou zéro")

    # ✅ Contrainte métier : montant restant <= montant total
    if remaining_amount > total_amount:
        raise ValueError(
            f"Le montant restant ({remaining_amount}) ne peut pas dépasser "
            f"le montant total ({total_amount})"
        )
```

**Autres validations métier importantes :**

```python
# Validation des dates d'événement (lignes 276-299)
def validate_event_dates(event_start: datetime, event_end: datetime, attendees: int):
    """Valide les dates et participants"""
    if event_end <= event_start:
        raise ValueError("La fin doit être après le début")

    if attendees < 0:
        raise ValueError("Le nombre de participants doit être positif")

    if event_start < datetime.now():
        raise ValueError("L'événement doit être dans le futur")
```

**Points clés :**
- ✅ **Validation en couches** : Input → Business logic → Base de données
- ✅ **Messages d'erreur explicites**
- ✅ **Contraintes métier** appliquées avant l'insertion en BDD
- ✅ **Cohérence des données** garantie

---

## 4️⃣ RBAC (CONTRÔLE D'ACCÈS PAR RÔLE)

### Décorateur de permissions

**Localisation:** `src/cli/permissions.py` (lignes 16-93)

```python
@require_department(Department.GESTION)
def create_contract(current_user: User, ...):
    """Seuls les GESTION peuvent créer des contrats"""
    # current_user est injecté automatiquement par le décorateur
    pass

# Implémentation du décorateur
def require_department(*allowed_departments: Department):
    """Vérifie l'authentification + département autorisé"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Vérifier l'authentification
            user = auth_service.get_current_user()
            if not user:
                print_error("Vous devez être connecté")
                raise typer.Exit(code=1)

            # 2. Vérifier le département
            if allowed_departments and user.department not in allowed_departments:
                print_error("Action non autorisée pour votre département")
                raise typer.Exit(code=1)

            # 3. Injecter current_user dans la fonction
            kwargs["current_user"] = user
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

**Matrice des permissions (RBAC) :**

| Action | COMMERCIAL | GESTION | SUPPORT |
|--------|------------|---------|---------|
| **Créer CLIENT** | ✅ | ❌ | ❌ |
| **Modifier CLIENT** | ✅ (ses clients) | ✅ | ❌ |
| **Créer CONTRAT** | ❌ | ✅ | ❌ |
| **Signer CONTRAT** | ❌ | ✅ | ❌ |
| **Créer ÉVÉNEMENT** | ✅ (contrat signé) | ❌ | ❌ |
| **Assigner SUPPORT** | ❌ | ✅ | ❌ |
| **Modifier ÉVÉNEMENT** | ❌ | ❌ | ✅ (ses événements) |
| **Lire tout** | ✅ | ✅ | ✅ |

**Points clés :**
- ✅ **Principe du moindre privilège** : Chaque rôle a des permissions spécifiques
- ✅ **Vérification centralisée** : Un seul endroit pour gérer les permissions
- ✅ **Injection de dépendance** : `current_user` injecté automatiquement
- ✅ **Fail-secure** : Par défaut, accès refusé sauf autorisation explicite

**Exemples d'utilisation :**

```python
# Seuls GESTION peuvent créer des contrats
@app.command()
@require_department(Department.GESTION)
def create_contract(current_user: User, ...):
    pass

# GESTION ou COMMERCIAL peuvent lister les clients
@app.command()
@require_department(Department.GESTION, Department.COMMERCIAL)
def list_clients(current_user: User):
    pass

# Tous les utilisateurs authentifiés
@app.command()
@require_department()  # Pas de département spécifié = authentification seule
def list_my_events(current_user: User):
    pass
```

---

## 5️⃣ CONTRAINTES BASE DE DONNÉES

### Contraintes CHECK au niveau SQLAlchemy (Défense en profondeur)

**Localisation:** `src/models/contract.py` (lignes 60-71)

```python
class Contract(Base):
    __tablename__ = "contracts"

    # Contraintes CHECK pour garantir l'intégrité
    __table_args__ = (
        CheckConstraint(
            "total_amount >= 0",
            name="check_total_amount_positive"
        ),
        CheckConstraint(
            "remaining_amount >= 0",
            name="check_remaining_amount_positive"
        ),
        CheckConstraint(
            "remaining_amount <= total_amount",
            name="check_remaining_lte_total"
        ),
    )
```

**Contraintes sur les événements (`src/models/event.py`, lignes 64-69) :**

```python
__table_args__ = (
    CheckConstraint(
        "event_end > event_start",
        name="check_event_dates_valid"
    ),
    CheckConstraint(
        "attendees >= 0",
        name="check_attendees_positive"
    ),
)
```

**Points clés :**
- ✅ **Défense en profondeur** : Validation à TOUS les niveaux
  1. **Input** (Typer validators) → Première ligne de défense
  2. **Business logic** (Service layer) → Règles métier
  3. **Base de données** (CHECK constraints) → Garantie ultime
- ✅ **Intégrité garantie** même si le code applicatif est bypassé
- ✅ **Contraintes nommées** : Facilite le debugging

**Exemple concret :**

```python
# Niveau 1 : Validation input CLI
validate_amount_callback(total_amount)  # Vérifie format numérique

# Niveau 2 : Validation business logic
validate_contract_amounts(total_amount, remaining_amount)  # Règle métier

# Niveau 3 : Contrainte BDD
# Si un attaquant bypass les niveaux 1 et 2, la BDD rejette l'insertion
INSERT INTO contracts VALUES (..., -1000, ...);  -- ❌ ERREUR: check_total_amount_positive
```

---

## 6️⃣ ARCHITECTURE & BONNES PRATIQUES

### Pattern Repository (Séparation des responsabilités)

**Architecture en couches (Clean Architecture) :**

```
┌─────────────────────────┐
│   CLI Commands          │  ← Interface utilisateur (Typer)
│   (auth_commands.py)    │     Gère les inputs/outputs
├─────────────────────────┤
│   Services              │  ← Logique métier
│   (auth_service.py)     │     Règles business, workflows
├─────────────────────────┤
│   Repositories          │  ← Accès aux données (abstraction)
│   (user_repository.py)  │     Interface pour la persistance
├─────────────────────────┤
│   SQLAlchemy Repos      │  ← Implémentation concrète
│   (sqlalchemy_...py)    │     Requêtes ORM
├─────────────────────────┤
│   Models (SQLAlchemy)   │  ← Représentation des tables
│   (user.py, client.py)  │     Schéma de données
├─────────────────────────┤
│   Base de données       │  ← PostgreSQL/SQLite
└─────────────────────────┘
```

**Exemple concret de flux :**

```python
# 1. CLI Command (Interface utilisateur)
@app.command()
@require_department(Department.GESTION)
def create_user(username: str, password: str, ...):
    """Point d'entrée CLI"""
    service = container.user_service()
    user = service.create_user(username, password, ...)
    print(f"Utilisateur créé : {user.username}")

# 2. Service Layer (Logique métier)
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository  # ✅ Injection de dépendance

    def create_user(self, username, password, ...):
        # Validation métier
        if len(password) < 8:
            raise ValueError("Mot de passe trop court")

        # Vérifier unicité
        if self.repository.get_by_username(username):
            raise ValueError("Username déjà pris")

        # Créer l'objet
        user = User(username=username, ...)
        user.set_password(password)  # ✅ Hash automatique

        # Persister via le repository
        return self.repository.add(user)

# 3. Repository (Abstraction)
class UserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass

# 4. SQLAlchemy Repository (Implémentation)
class SqlAlchemyUserRepository(UserRepository):
    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        return user

    def get_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter_by(username=username).first()

# 5. Model (Représentation de la table)
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    # ...
```

**Avantages de cette architecture :**
- ✅ **Séparation des responsabilités** (SRP - SOLID)
- ✅ **Injection de dépendance** : Facilite les tests unitaires
- ✅ **Testabilité** : Chaque couche peut être testée indépendamment
- ✅ **Maintenabilité** : Modifications isolées à une couche
- ✅ **Flexibilité** : Facile de changer de BDD (ex: SQLite → PostgreSQL)

**Exemple de test unitaire (grâce à l'injection de dépendance) :**

```python
def test_create_user():
    # Créer un mock repository
    mock_repo = MockUserRepository()

    # Injecter le mock dans le service
    service = UserService(mock_repo)

    # Tester sans toucher à la vraie BDD
    user = service.create_user("test", "password123", ...)
    assert user.username == "test"
```

---

## 📋 CHECKLIST POUR LA SOUTENANCE

### Questions probables et réponses à préparer

| Question | Réponse concise | Fichier référence |
|----------|-----------------|-------------------|
| **Comment protégez-vous contre l'injection SQL ?** | ✅ ORM SQLAlchemy avec requêtes paramétrées. Jamais de concaténation de strings SQL. Validation stricte des inputs. | `sqlalchemy_user_repository.py` |
| **Comment gérez-vous les mots de passe ?** | ✅ Hachage avec bcrypt (salt + iterations). Jamais stocké en clair. Vérification via `verify_password()`. | `user.py:58-77` |
| **Expliquez votre système d'authentification** | ✅ JWT avec expiration 24h, algorithme HS256, secret key en variable d'environnement. Token stocké dans `~/.epicevents/token` avec permissions 0600. | `auth_service.py` |
| **Comment gérez-vous les permissions ?** | ✅ RBAC avec décorateur `@require_department()`. 3 rôles : COMMERCIAL, GESTION, SUPPORT. Principe du moindre privilège. | `permissions.py` |
| **Validation des données utilisateur ?** | ✅ Triple validation : Input (regex) → Business logic (services) → BDD (CHECK constraints). Défense en profondeur. | `validators.py`, `contract.py:60-71` |
| **Architecture du projet ?** | ✅ Clean Architecture : CLI → Services → Repositories → Models → BDD. Séparation des responsabilités (SOLID). Pattern Repository pour abstraction. | Toute la structure `src/` |
| **Comment évitez-vous les fuites de données ?** | ✅ Bcrypt pour mots de passe, JWT avec expiration, validation stricte, logs Sentry pour monitoring, pas de données sensibles dans les tokens. | `auth_service.py`, `user.py` |
| **Expliquez le pattern Repository** | ✅ Abstraction de la persistance. Interface UserRepository + implémentation SQLAlchemy. Facilite les tests (mock) et permet de changer de BDD sans toucher au code métier. | `repositories/` |
| **Comment testez-vous votre code ?** | ✅ Tests unitaires (services, repositories) + tests d'intégration (workflows complets). Injection de dépendance pour mocker. Coverage > 80%. | `tests/unit/`, `tests/integration/` |
| **Migrations de base de données ?** | ✅ Alembic pour versionner le schéma. Migrations auto-générées depuis les modèles SQLAlchemy. Rollback possible. | `migrations/versions/` |

---

## 🔧 DÉMONSTRATION EN DIRECT

### Scénarios à maîtriser (À préparer)

#### 1. Créer un nouvel utilisateur (GESTION)

```bash
poetry run epicevents create-user \
  --username john_doe \
  --password SecurePass123 \
  --first-name John \
  --last-name Doe \
  --email john@example.com \
  --phone "0123456789" \
  --department 1  # 1=COMMERCIAL, 2=GESTION, 3=SUPPORT
```

**Ce qui se passe en coulisses :**
1. Validation input (regex username, password length)
2. Hash bcrypt du mot de passe
3. Insertion en BDD via repository
4. User créé avec `created_at` automatique

---

#### 2. S'authentifier

```bash
poetry run epicevents login
# Username: john_doe
# Password: SecurePass123
```

**Ce qui se passe :**
1. Récupération user depuis BDD
2. Vérification bcrypt du mot de passe
3. Génération JWT (expiration 24h)
4. Stockage token dans `~/.epicevents/token`

---

#### 3. Créer un client (COMMERCIAL uniquement)

```bash
poetry run epicevents create-client \
  --first-name Alice \
  --last-name Smith \
  --email alice@startup.io \
  --phone "0987654321" \
  --company "StartupCo"
```

**Protection RBAC :**
- ✅ Si connecté en COMMERCIAL : Client créé
- ❌ Si connecté en SUPPORT : Erreur "Action non autorisée"

---

#### 4. Lister les clients

```bash
# Liste tous les clients (tous les départements)
poetry run epicevents list-clients

# Filtrer par commercial (ID)
poetry run epicevents list-clients --sales-contact-id 1
```

---

#### 5. Créer un contrat (GESTION uniquement)

```bash
poetry run epicevents create-contract \
  --client-id 1 \
  --total-amount 50000 \
  --remaining-amount 10000
```

**Validation en 3 niveaux :**
1. Input : `validate_amount_callback()` → Format numérique
2. Business logic : `validate_contract_amounts()` → remaining ≤ total
3. BDD : CHECK constraints → Montants positifs

---

#### 6. Signer un contrat (GESTION uniquement)

```bash
poetry run epicevents sign-contract --contract-id 1
```

---

#### 7. Créer un événement (COMMERCIAL, contrat signé requis)

```bash
poetry run epicevents create-event \
  --contract-id 1 \
  --name "Product Launch 2025" \
  --start "2025-12-01 18:00" \
  --end "2025-12-01 23:00" \
  --location "Grand Hotel Paris" \
  --attendees 150
```

---

#### 8. Assigner un support (GESTION uniquement)

```bash
poetry run epicevents assign-support \
  --event-id 1 \
  --user-id 3  # ID d'un user SUPPORT
```

---

#### 9. Lister mes événements (SUPPORT)

```bash
# Affiche uniquement les événements assignés au support connecté
poetry run epicevents list-my-events
```

---

#### 10. Se déconnecter

```bash
poetry run epicevents logout
```

**Ce qui se passe :**
- Suppression du fichier `~/.epicevents/token`

---

### Commandes utiles pour la démo

```bash
# Afficher l'aide
poetry run epicevents --help

# Afficher l'aide d'une commande spécifique
poetry run epicevents create-user --help

# Vérifier l'état de la base de données (Alembic)
poetry run alembic current

# Voir l'historique des migrations
poetry run alembic history

# Lancer les tests
poetry run pytest

# Coverage des tests
poetry run pytest --cov=src --cov-report=html

# Linter (flake8)
poetry run flake8 src/

# Formateur (black)
poetry run black src/
```

---

## 🎤 PHRASES CLÉS À UTILISER DURANT LA SOUTENANCE

### Sur la sécurité

1. **"Nous appliquons le principe de **défense en profondeur** avec validation à trois niveaux : input, business logic, et base de données."**

2. **"Contre l'injection SQL, nous utilisons **SQLAlchemy ORM** qui génère automatiquement des requêtes paramétrées avec échappement des paramètres."**

3. **"Les mots de passe sont hachés avec **bcrypt** qui inclut un salt aléatoire et des iterations pour résister au brute-force. Le hash est unidirectionnel."**

4. **"L'authentification repose sur des **JWT avec expiration de 24h**, utilisant l'algorithme **HS256** et un secret key stocké en variable d'environnement."**

5. **"La validation des données suit le principe de **whitelisting** : on accepte uniquement les formats valides via regex strictes."**

---

### Sur l'architecture

6. **"Notre architecture suit les principes **SOLID** et le **pattern Repository** pour séparer les responsabilités et faciliter les tests."**

7. **"L'architecture en couches (CLI → Services → Repositories → Models → BDD) permet d'**isoler la logique métier** de la persistance."**

8. **"Nous utilisons l'**injection de dépendance** via le container Dependency Injector, ce qui facilite les tests unitaires avec des mocks."**

9. **"Le pattern Repository nous permet de **changer de base de données** (SQLite → PostgreSQL) sans toucher au code métier."**

---

### Sur les permissions

10. **"Le système RBAC garantit le **principe du moindre privilège** : chaque département n'a accès qu'aux actions nécessaires à son rôle."**

11. **"Le décorateur `@require_department()` centralise la **vérification des permissions** et injecte automatiquement l'utilisateur courant."**

12. **"Par défaut, l'accès est **refusé** (fail-secure) sauf autorisation explicite via le décorateur."**

---

### Sur les bonnes pratiques

13. **"Nous suivons les **OWASP Top 10** : protection contre injection SQL, XSS (pas applicable CLI), authentification cassée, exposition de données sensibles, etc."**

14. **"Les migrations Alembic permettent de **versionner le schéma** et de revenir en arrière (rollback) en cas de problème."**

15. **"Le monitoring avec **Sentry** capture les erreurs et les tentatives de connexion échouées pour détecter les attaques."**

16. **"La couverture de tests est > 80% avec des **tests unitaires** (services, repositories) et des **tests d'intégration** (workflows complets)."**

---

## 🎓 CONCEPTS CLÉS À MAÎTRISER

### OWASP Top 10 (2021) - Comment on les traite

| Vulnérabilité | Notre protection |
|---------------|------------------|
| **A01: Broken Access Control** | ✅ RBAC avec `@require_department()`, vérification à chaque action |
| **A02: Cryptographic Failures** | ✅ Bcrypt pour mots de passe, JWT HS256, secret key en env var |
| **A03: Injection** | ✅ SQLAlchemy ORM (requêtes paramétrées), validation inputs |
| **A04: Insecure Design** | ✅ Architecture en couches, SOLID, pattern Repository |
| **A05: Security Misconfiguration** | ✅ Permissions 0600 sur token, secret key en env var |
| **A07: Identification Failures** | ✅ JWT avec expiration, bcrypt résistant brute-force |
| **A08: Software/Data Integrity** | ✅ CHECK constraints BDD, validation à 3 niveaux |
| **A09: Security Logging Failures** | ✅ Sentry monitoring, logs des tentatives échouées |

*(A06, A10 non applicables car CLI, pas d'API web)*

---

### Principes SOLID appliqués

| Principe | Application dans le projet |
|----------|----------------------------|
| **S - Single Responsibility** | Chaque classe a une seule raison de changer : UserService (logique métier), UserRepository (persistance), User (modèle) |
| **O - Open/Closed** | Extension via héritage (SqlAlchemyUserRepository implémente UserRepository) |
| **L - Liskov Substitution** | Toute implémentation de UserRepository est interchangeable |
| **I - Interface Segregation** | Interfaces spécifiques (UserRepository, ClientRepository) au lieu d'une interface générique |
| **D - Dependency Inversion** | Services dépendent d'abstractions (UserRepository), pas d'implémentations concrètes |

---

### Termes techniques à utiliser

- **Salt** : Données aléatoires ajoutées au mot de passe avant hachage
- **Rainbow table** : Table précalculée de hash pour craquer les mots de passe
- **Brute-force** : Essayer toutes les combinaisons possibles
- **Parameterized query** : Requête SQL avec placeholders (évite injection)
- **JWT payload** : Données encodées dans le token (user_id, exp, iat)
- **HMAC** : Hash-based Message Authentication Code (signature JWT)
- **Stateless** : Pas de session côté serveur, tout dans le token
- **Whitelisting** : Accepter uniquement les valeurs valides (vs blacklisting)
- **Fail-secure** : En cas d'erreur, refuser l'accès par défaut

---

## 📚 RESSOURCES COMPLÉMENTAIRES

### Fichiers importants à revoir

- `src/models/user.py` - Modèle User, hachage bcrypt
- `src/services/auth_service.py` - Authentification JWT
- `src/cli/permissions.py` - RBAC avec décorateur
- `src/cli/validators.py` - Validation inputs/business
- `src/repositories/sqlalchemy_user_repository.py` - Protection injection SQL
- `docs/database-schema.md` - Schéma BDD avec contraintes

### Commandes pour préparer la démo

```bash
# 1. Nettoyer et recréer la BDD
rm epicevents.db
poetry run alembic upgrade head

# 2. Seed les données de test
poetry run python seed_database.py

# 3. Tester l'authentification
poetry run epicevents login
# Username: alice_martin
# Password: password123

# 4. Vérifier les permissions
poetry run epicevents list-clients  # ✅ OK
poetry run epicevents create-contract --client-id 1 --total-amount 1000 --remaining-amount 500
# ❌ Erreur si pas GESTION
```

---

## ✅ CHECKLIST FINALE AVANT LA SOUTENANCE

- [ ] Relire ce guide complet
- [ ] Tester toutes les commandes CLI de la section "Démonstration"
- [ ] Vérifier que la BDD est seedée avec des données de test
- [ ] Préparer des réponses aux questions de la checklist
- [ ] Revoir les 16 phrases clés à utiliser
- [ ] Comprendre le flux complet : Login → Create client → Create contract → Sign → Create event → Assign support
- [ ] Savoir expliquer chaque niveau de validation (input/business/BDD)
- [ ] Connaître la matrice RBAC par cœur
- [ ] Pouvoir dessiner l'architecture en couches
- [ ] Maîtriser les termes techniques (salt, JWT, HMAC, parameterized query)

---

**Bonne chance pour votre soutenance ! 🚀**

*Document créé le 2025-11-23*
*Projet 12 - Epic Events CRM - OpenClassrooms*
