# Guide de Soutenance - Epic Events CRM

**Durée totale** : 25 minutes (10 min présentation + 15 min discussion)

---

## 📋 Structure de la soutenance

### Partie 1 : Présentation des livrables (10 minutes)

1. [Vue d'ensemble du projet](#1-vue-densemble-du-projet-1-minute)
2. [Démonstration - Authentification](#2-démonstration---authentification-3-minutes)
3. [Démonstration - Gestion des utilisateurs](#3-démonstration---gestion-des-utilisateurs-2-minutes)
4. [Démonstration - Lecture et modification des données](#4-démonstration---lecture-et-modification-des-données-3-minutes)
5. [Récapitulatif de sécurité](#5-récapitulatif-de-sécurité-1-minute)

### Partie 2 : Discussion technique (15 minutes)

1. [Schéma de la base de données](#schéma-de-la-base-de-données)
2. [Sécurité - Risques classiques](#sécurité---risques-classiques)
3. [Bonnes pratiques de l'industrie](#bonnes-pratiques-de-lindustrie)

---

# PARTIE 1 : PRÉSENTATION DES LIVRABLES (10 minutes)

## 1. Vue d'ensemble du projet (1 minute)

### Script de présentation

> "Bonjour, je vais vous présenter Epic Events CRM, une application CLI sécurisée de gestion de la relation client pour une entreprise d'événementiel.
>
> L'application respecte toutes les exigences de sécurité du cahier des charges :
> - ✅ **Protection contre les injections SQL** avec SQLAlchemy ORM
> - ✅ **Principe du moindre privilège** avec RBAC (Role-Based Access Control)
> - ✅ **Authentification persistante** avec tokens JWT
> - ✅ **Journalisation avec Sentry** pour le monitoring
>
> L'architecture suit le pattern Clean Architecture avec séparation en couches : modèles, repositories, services, et interface CLI."

### Affichage visuel

Montrer rapidement l'arborescence du projet :

```bash
tree src -L 2
```

**Points clés à mentionner** :
- Architecture en couches
- Séparation des responsabilités
- Injection de dépendances

---

## 2. Démonstration - Authentification (3 minutes)

### 🎯 Objectif
Démontrer que l'authentification JWT fonctionne et protège l'accès aux commandes.

### 📝 Script de démonstration

#### Étape 1 : Tentative d'accès sans authentification (30 sec)

```bash
poetry run epicevents whoami
```

**Dire** :
> "Sans authentification, l'accès est refusé. Le message d'erreur invite l'utilisateur à se connecter."

**Résultat attendu** :
```
[ERREUR] Vous n'êtes pas connecté. Utilisez 'epicevents login' pour vous connecter.
```

#### Étape 2 : Connexion avec un utilisateur GESTION (1 min)

```bash
poetry run epicevents login
# Username: admin
# Password: Admin123!
```

**Dire** :
> "Je me connecte avec un utilisateur du département GESTION. L'application génère un token JWT signé avec HMAC-SHA256, valide pour 24 heures, et le stocke dans ~/.epicevents/token.
>
> Notez le message '[INFO] Sentry initialisé' - toutes les actions sont loggées dans Sentry pour le monitoring de sécurité."

**Résultat attendu** :
```
[INFO] Sentry non configuré (SENTRY_DSN manquant)
+-----------------------------------------------------------------------------+
| ✓ Bienvenue Alice Dubois !                                                 |
| Département : GESTION                                                       |
| Session     : Valide pour 24 heures                                        |
+-----------------------------------------------------------------------------+
```

#### Étape 3 : Vérification de l'utilisateur connecté (30 sec)

```bash
poetry run epicevents whoami
```

**Dire** :
> "La commande whoami affiche maintenant les informations de l'utilisateur authentifié. Le token JWT a été validé."

**Résultat attendu** :
```
+-----------------------------------------------------------------------------+
| ID                : 1                                                       |
| Nom d'utilisateur : admin                                                   |
| Nom complet       : Alice Dubois                                            |
| Email             : admin@epicevents.com                                    |
| Département       : GESTION                                                 |
+-----------------------------------------------------------------------------+
```

#### Étape 4 : Localisation du token JWT (30 sec)

```bash
# Windows
echo "Token stocké dans : %USERPROFILE%\.epicevents\token"
type %USERPROFILE%\.epicevents\token
```

**Dire** :
> "Le token JWT est stocké localement avec des permissions restreintes (600 sur Unix). Voici le token - c'est une chaîne encodée en trois parties séparées par des points : header, payload, et signature."

#### Étape 5 : Déconnexion (30 sec)

```bash
poetry run epicevents logout
```

**Dire** :
> "La déconnexion supprime le token JWT. Sentry enregistre également cette action avec un breadcrumb."

---

## 3. Démonstration - Gestion des utilisateurs (2 minutes)

### 🎯 Objectif
Démontrer le contrôle d'accès basé sur les rôles (RBAC).

### 📝 Script de démonstration

#### Étape 1 : Connexion en tant que GESTION (30 sec)

```bash
poetry run epicevents login
# Username: admin
# Password: Admin123!
```

**Dire** :
> "Seul le département GESTION peut créer des utilisateurs. Je me reconnecte avec admin."

#### Étape 2 : Création d'un utilisateur (1 min)

```bash
poetry run epicevents create-user
# Username: demo_user
# Prénom: Demo
# Nom: User
# Email: demo@example.com
# Téléphone: 0123456789
# Mot de passe: Demo123!
# Département: 1 (COMMERCIAL)
```

**Dire** :
> "La création d'un utilisateur nécessite le département GESTION. Le mot de passe est automatiquement hashé avec bcrypt avant d'être stocké. Jamais en clair dans la base de données."

**Résultat attendu** :
```
+-----------------------------------------------------------------------------+
| ✓ Utilisateur demo_user créé avec succès!                                  |
| ID          : 6                                                             |
| Nom complet : Demo User                                                     |
| Email       : demo@example.com                                              |
| Département : COMMERCIAL                                                    |
+-----------------------------------------------------------------------------+
```

#### Étape 3 : Test du contrôle d'accès (30 sec)

```bash
poetry run epicevents logout
poetry run epicevents login
# Username: commercial1
# Password: Commercial123!

poetry run epicevents create-user
# (Entrer n'importe quelles données)
```

**Dire** :
> "Un utilisateur COMMERCIAL tente de créer un utilisateur. L'accès est refusé - seul GESTION a cette permission."

**Résultat attendu** :
```
[ERREUR] Action non autorisée pour votre département
[ERREUR] Départements autorisés : GESTION
[ERREUR] Votre département : COMMERCIAL
```

---

## 4. Démonstration - Lecture et modification des données (3 minutes)

### 🎯 Objectif
Démontrer les filtres contextuels et la modification sécurisée des données.

### 📝 Script de démonstration

#### Étape 1 : Création d'un client avec auto-assignation (1 min)

```bash
# Déjà connecté en tant que commercial1
poetry run epicevents create-client
# Prénom: Jean
# Nom: Dupont
# Email: jean.dupont@example.com
# Téléphone: 0612345678
# Entreprise: DupontCorp
# ID contact commercial: (laisser vide - ENTRER)
```

**Dire** :
> "Un commercial crée un client. L'ID du contact commercial est automatiquement assigné à l'utilisateur connecté si laissé vide. C'est une fonctionnalité de sécurité qui empêche les commerciaux de s'attribuer les clients des autres."

**Résultat attendu** :
```
| Contact commercial : Auto-assigné à commercial1                            |
+-----------------------------------------------------------------------------+
| ✓ Client Jean Dupont créé avec succès!                                     |
+-----------------------------------------------------------------------------+
```

#### Étape 2 : Filtrage des contrats non signés (1 min)

```bash
poetry run epicevents filter-unsigned-contracts
```

**Dire** :
> "Les filtres contextuels remplacent les méthodes get_all() dangereuses. Au lieu de récupérer tous les contrats, on applique un filtre métier : 'contrats non signés'. Cela respecte le principe du moindre privilège.
>
> Aucune méthode get_all() n'existe dans l'application - tout est filtré."

**Résultat attendu** :
```
+-----------------------------------------------------------------------------+
|                       Contrats non signés                                   |
+-----------------------------------------------------------------------------+
| Aucun contrat non signé trouvé                                              |
+-----------------------------------------------------------------------------+
```

#### Étape 3 : Validation des données utilisateur (1 min)

```bash
poetry run epicevents create-client
# Prénom: Jean
# Nom: Dupont
# Email: invalid-email  (EMAIL INVALIDE)
```

**Dire** :
> "Toutes les données utilisateur sont validées avec des regex et des type checks. Ici, l'email est invalide - l'application le détecte immédiatement."

**Résultat attendu** :
```
[ERREUR] Format d'email invalide
```

**Ensuite, tester avec un email déjà existant** :

```bash
poetry run epicevents create-client
# ... (mêmes données qu'avant avec jean.dupont@example.com)
```

**Dire** :
> "SQLAlchemy détecte les violations d'unicité. L'application affiche un message d'erreur clair sans exposer de détails techniques sensibles."

**Résultat attendu** :
```
[ERREUR] Un client avec l'email 'jean.dupont@example.com' existe déjà dans le système
```

---

## 5. Récapitulatif de sécurité (1 minute)

### Script de conclusion

> "En résumé, l'application Epic Events CRM implémente :
>
> **1. Authentification sécurisée**
> - Tokens JWT signés HMAC-SHA256
> - Stockage local avec permissions restreintes
> - Expiration automatique après 24h
>
> **2. Autorisation granulaire**
> - RBAC avec 3 rôles (COMMERCIAL, GESTION, SUPPORT)
> - Vérification à chaque commande
> - Principe du moindre privilège
>
> **3. Protection des données**
> - ORM SQLAlchemy contre injection SQL
> - Validation complète des inputs
> - Hachage bcrypt des mots de passe
> - Pas de méthodes get_all()
>
> **4. Monitoring**
> - Sentry pour journalisation
> - Logging des tentatives de connexion
> - Breadcrumbs et contexte utilisateur
>
> L'application est prête pour la production."

---

# PARTIE 2 : DISCUSSION TECHNIQUE (15 minutes)

## Schéma de la base de données

### Question attendue
> "Pouvez-vous expliquer la logique du schéma de votre base de données ?"

### 📊 Réponse structurée

#### Diagramme à présenter

```
┌──────────────────────────┐
│         User             │
│ ──────────────────────── │
│ PK  id                   │
│ UQ  username             │
│ UQ  email                │
│     password_hash        │◄─────┐
│     first_name           │      │
│     last_name            │      │
│     phone                │      │
│     department (ENUM)    │      │
│     created_at           │      │
│     updated_at           │      │
└────────────┬─────────────┘      │
             │ 1                  │
             │                    │
             │ *                  │
      ┌──────▼──────────────┐    │
      │     Client          │    │
      │ ─────────────────── │    │
      │ PK  id              │    │
      │ UQ  email           │    │
      │     first_name      │    │
      │     last_name       │    │
      │     phone           │    │
      │     company_name    │    │
      │ FK  sales_contact_id├────┘
      │     created_at      │
      │     updated_at      │
      └──────┬──────────────┘
             │ 1
             │
             │ *
      ┌──────▼──────────────┐
      │     Contract        │
      │ ─────────────────── │
      │ PK  id              │
      │ FK  client_id       │
      │     total_amount    │
      │     remaining_amount│
      │     is_signed       │
      │     created_at      │
      │     updated_at      │
      └──────┬──────────────┘
             │ 1
             │
             │ *
      ┌──────▼──────────────┐       ┌──────────────────────┐
      │     Event           │       │         User         │
      │ ─────────────────── │       │  (SUPPORT contact)   │
      │ PK  id              │     * │                      │
      │     name            ├───────┤                      │
      │ FK  contract_id     │       │                      │
      │ FK  support_contact ├───────►                      │
      │     event_start     │       └──────────────────────┘
      │     event_end       │
      │     location        │
      │     attendees       │
      │     notes           │
      │     created_at      │
      │     updated_at      │
      └─────────────────────┘
```

#### Explication détaillée

**1. Entité User (pivot central)**
> "La table User est centrale car elle sert pour deux rôles distincts :
> - **Sales contact** : Un utilisateur COMMERCIAL assigné à des clients
> - **Support contact** : Un utilisateur SUPPORT assigné à des événements
>
> Le champ `department` (ENUM) définit le rôle : COMMERCIAL, GESTION, ou SUPPORT."

**2. Relations hiérarchiques**
> "Les relations suivent le flux métier :
> - Un **Commercial** (User) gère plusieurs **Clients**
> - Un **Client** a plusieurs **Contrats**
> - Un **Contrat** (signé) génère plusieurs **Événements**
> - Un **Support** (User) est assigné à plusieurs **Événements**
>
> C'est une cascade logique qui reflète le processus commercial."

**3. Contraintes d'intégrité**

| Contrainte | Table | Colonne | Rôle de sécurité |
|------------|-------|---------|------------------|
| PRIMARY KEY | Toutes | id | Identification unique |
| UNIQUE | User | username, email | Empêche les doublons d'utilisateurs |
| UNIQUE | Client | email | Un client = un email unique |
| FOREIGN KEY | Client | sales_contact_id | Garantit l'existence du commercial |
| FOREIGN KEY | Contract | client_id | Garantit l'existence du client |
| FOREIGN KEY | Event | contract_id | Garantit l'existence du contrat |
| FOREIGN KEY | Event | support_contact_id | Garantit l'existence du support |
| NOT NULL | User | password_hash | Impossible de créer un user sans mdp |
| NOT NULL | Contract | total_amount | Montant obligatoire |
| CHECK (implicite) | Contract | remaining_amount >= 0 | Validé par l'application |

**4. Timestamps automatiques**
> "Chaque table a `created_at` et `updated_at` :
> - **Traçabilité** : Savoir quand une donnée a été créée/modifiée
> - **Audit** : Détecter les modifications suspectes
> - **Sécurité** : Logs temporels pour Sentry"

**5. Types de données sécurisés**

| Colonne | Type SQL | Longueur | Justification |
|---------|----------|----------|---------------|
| username | VARCHAR | 50 | Limite les attaques par buffer overflow |
| email | VARCHAR | 255 | Standard RFC 5321 |
| password_hash | VARCHAR | 255 | Bcrypt génère ~60 caractères |
| phone | VARCHAR | 20 | Numéros internationaux |
| total_amount | DECIMAL | 10,2 | Précision monétaire |

---

## Sécurité - Risques classiques

### Question attendue
> "Comment votre implémentation limite-t-elle les risques classiques comme l'injection SQL, les fuites de données, et la validation des données utilisateur ?"

### 🛡️ Réponse structurée

#### 1. Protection contre l'injection SQL

**Risque** :
> "L'injection SQL permet à un attaquant d'exécuter du code SQL arbitraire en manipulant les inputs."

**Exemple d'attaque** :
```python
# ❌ Code vulnérable (que nous N'UTILISONS PAS)
username = input("Username: ")
query = f"SELECT * FROM users WHERE username = '{username}'"
# Un attaquant entre : ' OR '1'='1' --
# Résultat : SELECT * FROM users WHERE username = '' OR '1'='1' --'
# Accès à tous les utilisateurs !
```

**Notre protection** :
> "Nous utilisons SQLAlchemy ORM qui génère automatiquement des requêtes paramétrées :"

```python
# ✅ Code sécurisé (notre implémentation)
user = session.query(User).filter_by(username=username).first()
# SQLAlchemy génère : SELECT * FROM users WHERE username = ?
# Paramètre bindé séparément, impossible d'injecter du SQL
```

**Démonstration de code** : `src/repositories/sqlalchemy_user_repository.py:30-33`

```python
def get_by_username(self, username: str) -> Optional[User]:
    return self.session.query(User).filter_by(username=username).first()
```

**Points clés** :
- ✅ Aucune concaténation de chaînes SQL
- ✅ ORM avec requêtes paramétrées
- ✅ Validation des types avant la requête

---

#### 2. Protection contre les fuites de données

**Risque** :
> "Les fuites de données surviennent quand un utilisateur accède à plus de données qu'il ne devrait."

**Exemple de vulnérabilité** :
```python
# ❌ Méthode dangereuse (que nous avons SUPPRIMÉE)
def get_all_clients():
    return session.query(Client).all()
# Un commercial peut voir TOUS les clients, même ceux des autres !
```

**Notre protection - Principe du moindre privilège** :

**a) Suppression des get_all()**
> "Nous avons supprimé toutes les méthodes `get_all()` et les avons remplacées par des filtres contextuels :"

```python
# ✅ Filtre contextuel (notre implémentation)
def get_clients_by_sales_contact(self, sales_contact_id: int):
    return self.session.query(Client).filter_by(
        sales_contact_id=sales_contact_id
    ).all()
# Un commercial voit uniquement SES clients
```

**b) Vérification d'ownership**

`src/cli/permissions.py:127-146`

```python
def check_client_ownership(user: User, client) -> bool:
    # GESTION a accès à tous les clients
    if user.department == Department.GESTION:
        return True

    # COMMERCIAL ne peut accéder qu'à ses propres clients
    if user.department == Department.COMMERCIAL:
        return client.sales_contact_id == user.id

    return False  # SUPPORT n'a pas accès aux clients
```

**c) Décorateurs de permission**

`src/cli/permissions.py:64-124`

```python
@require_department(Department.COMMERCIAL, Department.GESTION)
def create_client(...):
    # Seuls COMMERCIAL et GESTION peuvent créer des clients
```

**Matrice de contrôle d'accès** :

| Action | GESTION | COMMERCIAL | SUPPORT |
|--------|---------|------------|---------|
| Voir tous les clients | ✅ | ❌ | ❌ |
| Voir ses clients | ✅ | ✅ | ❌ |
| Modifier tous les clients | ✅ | ❌ | ❌ |
| Modifier ses clients | ✅ | ✅ | ❌ |

**Points clés** :
- ✅ Pas de `get_all()` - tout est filtré
- ✅ Vérification d'ownership systématique
- ✅ RBAC avec décorateurs
- ✅ Filtres contextuels uniquement

---

#### 3. Validation des données utilisateur

**Risque** :
> "Des données invalides peuvent causer des erreurs, des bugs, ou être exploitées pour des attaques (XSS, buffer overflow, etc.)."

**Notre protection - Triple validation** :

**a) Validation au niveau CLI (première ligne)**

`src/cli/validators.py`

```python
def validate_email_callback(value: str) -> str:
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_regex, value):
        raise typer.BadParameter("Format d'email invalide")
    return value

def validate_phone_callback(value: str) -> str:
    phone_clean = re.sub(r"[\s\-\(\)]", "", value)
    if len(phone_clean) < 10:
        raise typer.BadParameter("Le numéro doit contenir au moins 10 chiffres")
    return value

def validate_amount_callback(value: str) -> str:
    try:
        amount = Decimal(value)
        if amount < 0:
            raise typer.BadParameter("Le montant ne peut pas être négatif")
        return value
    except InvalidOperation:
        raise typer.BadParameter("Format de montant invalide")
```

**b) Validation au niveau Service (logique métier)**

`src/services/contract_service.py`

```python
from src.cli.validators import validate_contract_amounts

def create_contract(self, ...):
    # Validation métier
    validate_contract_amounts(
        Decimal(total_amount),
        Decimal(remaining_amount)
    )
    # Vérifie que remaining_amount <= total_amount
```

**c) Validation au niveau Base de données (contraintes)**

```python
# Modèle SQLAlchemy
class User(Base):
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    # SQLAlchemy garantit l'unicité et la non-nullité
```

**Liste complète des validations** :

| Donnée | Validation CLI | Validation Service | Contrainte DB |
|--------|----------------|-------------------|---------------|
| Email | Regex RFC 5322 | - | UNIQUE, NOT NULL |
| Username | Regex (4-50 chars) | - | UNIQUE, NOT NULL, VARCHAR(50) |
| Password | Min 8 caractères | Hachage bcrypt | NOT NULL, VARCHAR(255) |
| Phone | Min 10 chiffres | - | NOT NULL, VARCHAR(20) |
| Montants | Decimal >= 0 | remaining <= total | NOT NULL, DECIMAL(10,2) |
| Dates | Format ISO | Parsing datetime | NOT NULL |
| Department | Enum valide | - | ENUM |

**Points clés** :
- ✅ Validation en trois couches (défense en profondeur)
- ✅ Regex pour formats structurés
- ✅ Type checking avec Decimal, datetime
- ✅ Contraintes DB comme dernier rempart
- ✅ Messages d'erreur clairs sans détails techniques

---

#### 4. Protection des mots de passe

**Risque** :
> "Stockage en clair des mots de passe = catastrophe en cas de fuite de la base de données."

**Notre protection - Bcrypt avec salt** :

`src/models/user.py:56-67`

```python
def set_password(self, password: str) -> None:
    """Hash and set password using bcrypt."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()  # Salt unique automatique
    hashed = bcrypt.hashpw(password_bytes, salt)
    self.password_hash = hashed.decode("utf-8")

def verify_password(self, password: str) -> bool:
    """Verify password against hash using bcrypt."""
    password_bytes = password.encode("utf-8")
    hash_bytes = self.password_hash.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hash_bytes)
```

**Pourquoi bcrypt ?**
- ✅ **Salt automatique** : Chaque mot de passe a un salt unique
- ✅ **Lenteur intentionnelle** : Résistant aux attaques par force brute (~100ms/hash)
- ✅ **Work factor ajustable** : Peut augmenter la difficulté avec le temps
- ✅ **Standard de l'industrie** : Recommandé par OWASP

**Exemple de hash bcrypt** :
```
$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5jtRq5CcH6RM6
 │  │  │                        │
 │  │  │                        └─ Hash (31 chars)
 │  │  └─────────────────────────── Salt (22 chars)
 │  └────────────────────────────── Cost factor (2^12 = 4096 rounds)
 └───────────────────────────────── Algorithme (bcrypt)
```

**Points clés** :
- ✅ Jamais de mot de passe en clair dans la DB
- ✅ Salt unique par utilisateur
- ✅ Algorithme de hachage moderne (bcrypt)
- ✅ Impossible de retrouver le mot de passe d'origine

---

#### 5. Sécurité des tokens JWT

**Risque** :
> "Tokens JWT non signés ou mal configurés peuvent être forgés par un attaquant."

**Notre protection** :

`src/services/auth_service.py:97-109`

```python
def generate_token(self, user: User) -> str:
    now = datetime.utcnow()
    expiration = now + timedelta(hours=24)

    payload = {
        "user_id": user.id,
        "username": user.username,
        "department": user.department.value,
        "exp": expiration,  # Expiration automatique
        "iat": now,          # Issued at
    }

    token = jwt.encode(payload, self._secret_key, algorithm="HS256")
    return token
```

**Configuration sécurisée** :
- ✅ **Algorithme HMAC-SHA256** : Signature cryptographique forte
- ✅ **Secret key de 256 bits minimum** : Clé robuste
- ✅ **Expiration 24h** : Limite la fenêtre d'exposition
- ✅ **Stockage local sécurisé** : Permissions 600 (Unix)
- ✅ **Variable d'environnement** : Secret key non hardcodée

**Points clés** :
- ✅ Signature vérifiée à chaque requête
- ✅ Expiration automatique
- ✅ Secret key robuste et externalisée
- ✅ Impossible de forger un token sans la clé

---

## Bonnes pratiques de l'industrie

### Question attendue
> "Comment votre implémentation suit-elle les bonnes pratiques actuelles de l'industrie ?"

### 📚 Réponse structurée

#### 1. Architecture Clean Architecture / Hexagonale

**Principe** :
> "Séparation stricte des responsabilités en couches indépendantes."

**Notre implémentation** :

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI (Interface)                           │
│                  src/cli/commands.py                         │
│              (Typer - User Interface)                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Services (Business Logic)                   │
│  src/services/{auth,user,client,contract,event}_service.py  │
│            (Logique métier pure)                             │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Repositories (Data Access)                      │
│  src/repositories/sqlalchemy_*_repository.py                 │
│        (Interface avec la base de données)                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Models (Domain)                             │
│       src/models/{user,client,contract,event}.py             │
│          (Entités métier)                                    │
└─────────────────────────────────────────────────────────────┘
```

**Avantages** :
- ✅ **Testabilité** : Chaque couche testable indépendamment
- ✅ **Maintenabilité** : Changement DB sans toucher la logique
- ✅ **Réutilisabilité** : Services réutilisables (CLI → API REST)
- ✅ **Séparation des préoccupations** : Chaque couche a un rôle unique

**Référence industrie** : Clean Architecture (Robert C. Martin)

---

#### 2. Dependency Injection

**Principe** :
> "Inversion de contrôle - les dépendances sont injectées, pas instanciées."

**Notre implémentation** :

`src/containers.py`

```python
class Container(containers.DeclarativeContainer):
    # Database
    db_session = providers.Factory(get_db_session)

    # Repositories
    user_repository = providers.Factory(
        SqlAlchemyUserRepository,
        session=db_session,
    )

    # Services
    auth_service = providers.Factory(
        AuthService,
        repository=user_repository,
    )
```

**Utilisation dans les commandes** :

```python
@app.command()
def create_user(...):
    container = Container()
    user_service = container.user_service()
    # Toutes les dépendances sont injectées automatiquement
```

**Avantages** :
- ✅ **Loose coupling** : Composants découplés
- ✅ **Testabilité** : Mock facile des dépendances
- ✅ **Configuration centralisée** : Un seul endroit pour les dépendances
- ✅ **Gestion du cycle de vie** : Factory pattern pour les sessions DB

**Référence industrie** : Dependency Injection (Martin Fowler)

---

#### 3. Repository Pattern

**Principe** :
> "Abstraction de l'accès aux données - la source de données peut changer sans impacter le code."

**Notre implémentation** :

`src/repositories/user_repository.py` (Interface)

```python
class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass
```

`src/repositories/sqlalchemy_user_repository.py` (Implémentation)

```python
class SqlAlchemyUserRepository(UserRepository):
    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        return user

    # Implémentation spécifique à SQLAlchemy
```

**Avantages** :
- ✅ **Abstraction** : Le service ne connaît pas SQLAlchemy
- ✅ **Changement de DB facile** : PostgreSQL → MongoDB sans toucher les services
- ✅ **Test avec mock** : Repository mockable pour les tests unitaires
- ✅ **Single Responsibility** : Repository = accès données uniquement

**Référence industrie** : Repository Pattern (Domain-Driven Design)

---

#### 4. OWASP Top 10 - Conformité

**Référence industrie** : [OWASP Top 10 2021](https://owasp.org/Top10/)

| Risque OWASP | Notre protection | Implémentation |
|--------------|------------------|----------------|
| **A01 - Broken Access Control** | RBAC + Ownership checks | `src/cli/permissions.py` |
| **A02 - Cryptographic Failures** | Bcrypt + JWT HMAC-SHA256 | `src/models/user.py`, `src/services/auth_service.py` |
| **A03 - Injection** | ORM SQLAlchemy paramétré | `src/repositories/sqlalchemy_*.py` |
| **A04 - Insecure Design** | Clean Architecture | Architecture globale |
| **A05 - Security Misconfiguration** | Variables d'environnement | `.env` |
| **A06 - Vulnerable Components** | Dependencies à jour (Poetry) | `pyproject.toml` |
| **A07 - Authentication Failures** | JWT + Password validation | `src/services/auth_service.py` |
| **A08 - Software/Data Integrity** | Foreign keys + Constraints | Modèles SQLAlchemy |
| **A09 - Security Logging** | Sentry + Breadcrumbs | `src/sentry_config.py` |
| **A10 - SSRF** | N/A (CLI, pas de requêtes externes) | - |

---

#### 5. Twelve-Factor App

**Référence industrie** : [12factor.net](https://12factor.net/)

| Facteur | Notre implémentation | Conformité |
|---------|---------------------|------------|
| **I. Codebase** | Git repository unique | ✅ |
| **II. Dependencies** | Poetry + pyproject.toml | ✅ |
| **III. Config** | Variables d'environnement (.env) | ✅ |
| **IV. Backing services** | Database URL configurable | ✅ |
| **V. Build, release, run** | Poetry build + run | ✅ |
| **VI. Processes** | Stateless (token JWT externe) | ✅ |
| **VII. Port binding** | N/A (CLI) | - |
| **VIII. Concurrency** | N/A (single process CLI) | - |
| **IX. Disposability** | Graceful shutdown (finally block) | ✅ |
| **X. Dev/prod parity** | ENVIRONMENT variable | ✅ |
| **XI. Logs** | Sentry pour centralisation | ✅ |
| **XII. Admin processes** | seed_database.py séparé | ✅ |

---

#### 6. Principe SOLID

**Référence industrie** : SOLID Principles (Robert C. Martin)

| Principe | Implémentation | Exemple |
|----------|----------------|---------|
| **S - Single Responsibility** | Une classe = une responsabilité | `AuthService` fait auth uniquement |
| **O - Open/Closed** | Extension sans modification | Repository interface + implémentations |
| **L - Liskov Substitution** | Implémentations interchangeables | Tous les repositories respectent l'interface |
| **I - Interface Segregation** | Interfaces minimales | Repository interfaces ciblées |
| **D - Dependency Inversion** | Injection de dépendances | Container IoC |

**Exemple concret - Single Responsibility** :

```python
# ✅ BON : Chaque classe a UNE responsabilité
class AuthService:
    # Responsabilité : Authentification uniquement
    def authenticate(self, username, password): ...
    def generate_token(self, user): ...
    def validate_token(self, token): ...

class UserService:
    # Responsabilité : Gestion des utilisateurs
    def create_user(self, ...): ...
    def get_user(self, user_id): ...

# ❌ MAUVAIS (que nous N'UTILISONS PAS)
class UserAuthService:
    # Deux responsabilités mélangées
    def authenticate(self, ...): ...
    def create_user(self, ...): ...
```

---

#### 7. Logging et Monitoring (Sentry)

**Référence industrie** : Observability Best Practices

**Notre implémentation** :

`src/sentry_config.py`

```python
# Initialisation Sentry
sentry_sdk.init(
    dsn=sentry_dsn,
    traces_sample_rate=1.0,     # 100% des transactions (ajustable en prod)
    profiles_sample_rate=1.0,   # 100% des profils
    environment=environment,    # dev/staging/production
    send_default_pii=False,     # Pas de PII
)
```

**Événements journalisés** :
- ✅ Tentatives de connexion (succès/échecs)
- ✅ Exceptions non gérées
- ✅ Breadcrumbs (parcours utilisateur)
- ✅ Contexte utilisateur (user_id, department)

**Avantages** :
- ✅ **Détection proactive** : Alertes en temps réel
- ✅ **Debugging facilité** : Stack traces complètes
- ✅ **Analyse de sécurité** : Tentatives d'intrusion détectées
- ✅ **Monitoring de performance** : Traces et profils

---

#### 8. Security by Design

**Principe** :
> "La sécurité est intégrée dès la conception, pas ajoutée après."

**Décisions de conception sécurisées** :

| Décision | Justification | Implémentation |
|----------|---------------|----------------|
| Supprimer `get_all()` | Éviter fuites de données | Filtres contextuels uniquement |
| JWT signé HMAC-SHA256 | Impossible de forger des tokens | `auth_service.py` |
| Bcrypt avec salt | Rainbow tables inefficaces | `user.py:set_password()` |
| Validation triple couche | Défense en profondeur | CLI + Service + DB |
| RBAC dès le départ | Principe du moindre privilège | `permissions.py` |
| Messages d'erreur génériques | Pas de divulgation d'infos | "Username ou password incorrect" |
| Permissions 600 token file | Lecture restreinte au propriétaire | `auth_service.py:save_token()` |

---

## 📋 Checklist avant la soutenance

### Préparation technique

- [ ] Base de données initialisée : `poetry run python seed_database.py`
- [ ] `.env` configuré avec `EPICEVENTS_SECRET_KEY`
- [ ] Application testée : `poetry run epicevents whoami`
- [ ] Tests unitaires passent : `poetry run pytest tests/unit/ -v`

### Documents à avoir sous la main

- [ ] `docs/DEMO_AUTHENTICATION.md` - Scénarios de démonstration
- [ ] `docs/SENTRY_SETUP.md` - Configuration Sentry
- [ ] `docs/SECURITY_SUMMARY.md` - Résumé sécurité
- [ ] `docs/AUTHENTICATION.md` - Architecture auth
- [ ] Diagramme ERD de la base de données (ci-dessus)

### Code à pouvoir montrer rapidement

- [ ] `src/models/` - Modèles avec contraintes
- [ ] `src/repositories/` - Pattern Repository
- [ ] `src/services/` - Logique métier
- [ ] `src/cli/permissions.py` - RBAC
- [ ] `src/cli/validators.py` - Validation inputs
- [ ] `src/services/auth_service.py` - JWT + Bcrypt
- [ ] `src/sentry_config.py` - Logging

### Réponses préparées

- [ ] Pourquoi SQLAlchemy ORM ?
- [ ] Pourquoi bcrypt et pas SHA256 ?
- [ ] Pourquoi JWT et pas sessions serveur ?
- [ ] Comment gérer les tokens expirés ?
- [ ] Que faire en cas de fuite de la clé secrète ?
- [ ] Comment migrer vers PostgreSQL ?
- [ ] Comment ajouter une nouvelle permission ?

---

## 🎯 Conseils pour la soutenance

### Attitude et communication

1. **Confiance** : Vous avez implémenté une application sécurisée et complète
2. **Clarté** : Utilisez des termes techniques mais expliquez-les simplement
3. **Honnêteté** : Si vous ne savez pas, dites "Je ne sais pas, mais voici comment je chercherais la réponse"
4. **Démonstration** : Montrez le code, ne vous contentez pas de décrire

### Gestion du temps

- **Présentation (10 min)** : Préparez un timer, respectez le timing
- **Discussion (15 min)** : Laissez l'évaluateur poser ses questions, ne monopolisez pas

### Points forts à mettre en avant

1. ✅ **Conformité totale** au cahier des charges (100%)
2. ✅ **Sécurité** : OWASP Top 10, JWT, Bcrypt, RBAC
3. ✅ **Architecture** : Clean Architecture, SOLID, DI
4. ✅ **Bonnes pratiques** : Repository Pattern, Validation triple couche
5. ✅ **Production-ready** : Sentry, variables d'env, tests

### Questions difficiles anticipées

**Q: "Pourquoi ne pas utiliser OAuth2 au lieu de JWT simple ?"**
> R: "OAuth2 est excellent pour les applications multi-tenant ou les connexions tierces (Google, Facebook). Ici, c'est une application interne CLI avec authentification basique username/password. JWT suffit largement et est plus simple à maintenir. En production, on pourrait ajouter un refresh token pour améliorer la sécurité."

**Q: "Et si un attaquant vole le fichier token ?"**
> R: "Plusieurs mesures de mitigation :
> 1. Permissions 600 (Unix) - seul le propriétaire peut lire
> 2. Expiration 24h - fenêtre d'exposition limitée
> 3. Logging Sentry - tentatives suspectes détectées
> 4. En production, on pourrait ajouter device fingerprinting ou IP whitelisting"

**Q: "Votre application est-elle résistante aux attaques par force brute ?"**
> R: "Oui, grâce à bcrypt qui est intentionnellement lent (~100ms/hash). Un attaquant ne peut tester que ~10 mots de passe par seconde. Pour améliorer, on pourrait ajouter :
> 1. Rate limiting (max 5 tentatives / 15 minutes)
> 2. CAPTCHA après 3 échecs
> 3. Blocage temporaire du compte"

---

**Bonne chance pour votre soutenance ! 🚀**

**Date de dernière mise à jour** : 2025-11-03
**Version** : 1.0
