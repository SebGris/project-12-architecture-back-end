# Flux de création d'un client - Cheminement du code

Ce document explique le cheminement complet du code lors de l'exécution de la commande `epicevents create-client`.

## Vue d'ensemble

```
Commande CLI → main.py → Container → commands.py → Services → Repositories → Base de données
```

## Étape par étape

### 1. Point d'entrée : `poetry run epicevents create-client`

**Fichier** : [pyproject.toml](../pyproject.toml#L24)
```toml
[tool.poetry.scripts]
epicevents = "src.cli.main:main"
```

Poetry exécute la fonction `main()` du module `src.cli.main`.

---

### 2. Initialisation de l'application

**Fichier** : [src/cli/main.py](../src/cli/main.py#L10-L19)

```python
def main():
    """Point d'entrée principal de l'application."""
    # 1. Initialiser le container d'injection de dépendances
    container = Container()

    # 2. Définir le container dans le module commands
    commands.set_container(container)

    # 3. Lancer l'application Typer
    commands.app()
```

**Ce qui se passe** :
1. Création du `Container` qui configure toutes les dépendances
2. Injection du container dans le module `commands` via `set_container()`
3. Lancement de l'application Typer qui attend les commandes de l'utilisateur

---

### 3. Configuration des dépendances

**Fichier** : [src/containers.py](../src/containers.py)

```python
class Container(containers.DeclarativeContainer):
    # Database session factory
    db_session = providers.Factory(get_db_session)

    # Repositories
    client_repository = providers.Factory(
        SqlAlchemyClientRepository,
        session=db_session,
    )

    user_repository = providers.Factory(
        SqlAlchemyUserRepository,
        session=db_session,
    )

    # Services
    client_service = providers.Factory(
        ClientService,
        repository=client_repository,
    )

    user_service = providers.Factory(
        UserService,
        repository=user_repository,
    )
```

**Ce qui se passe** :
- Le container définit comment créer chaque composant
- `Factory` signifie qu'une nouvelle instance est créée à chaque appel
- Les dépendances sont injectées automatiquement (ex: `client_service` reçoit `client_repository`)

---

### 4. Réception de la commande

**Fichier** : [src/cli/commands.py](../src/cli/commands.py#L115-L139)

```python
@app.command()
def create_client(
    first_name: str = typer.Option(..., prompt="Prénom", callback=validate_first_name_callback),
    last_name: str = typer.Option(..., prompt="Nom", callback=validate_last_name_callback),
    email: str = typer.Option(..., prompt="Email", callback=validate_email_callback),
    phone: str = typer.Option(..., prompt="Téléphone", callback=validate_phone_callback),
    company_name: str = typer.Option(..., prompt="Nom de l'entreprise", callback=validate_company_name_callback),
    sales_contact_id: int = typer.Option(..., prompt="ID du contact commercial", callback=validate_sales_contact_id_callback),
):
```

**Ce qui se passe** :
1. Typer affiche les prompts interactifs pour chaque paramètre
2. Chaque valeur saisie passe par un callback de validation (ex: `validate_email_callback`)
3. Si la validation échoue, une erreur `typer.BadParameter` est levée
4. Une fois toutes les données collectées et validées, la fonction continue

---

### 5. Récupération des services

**Fichier** : [src/cli/commands.py](../src/cli/commands.py#L143-L145)

```python
# Get services from container
client_service = _container.client_service()
user_service = _container.user_service()
```

**Ce qui se passe** :
1. `_container.client_service()` appelle le provider du container
2. Le container crée automatiquement :
   - Une session de base de données via `get_db_session()`
   - Un `SqlAlchemyClientRepository` avec cette session
   - Un `ClientService` avec ce repository
3. Même chose pour `user_service`

**Graphe de création** :
```
_container.client_service()
    └─> providers.Factory(ClientService)
        └─> repository=client_repository()
            └─> providers.Factory(SqlAlchemyClientRepository)
                └─> session=db_session()
                    └─> providers.Factory(get_db_session)
                        └─> return _SessionLocal()
```

---

### 6. Validation métier : Vérification du contact commercial

**Fichier** : [src/cli/commands.py](../src/cli/commands.py#L148-L161)

```python
# Business validation: check if sales contact exists
user = user_service.get_user(sales_contact_id)

if not user:
    typer.echo(f"[ERREUR] Utilisateur avec l'ID {sales_contact_id} n'existe pas")
    raise typer.Exit(code=1)

if user.department != Department.COMMERCIAL:
    typer.echo(f"[ERREUR] L'utilisateur {sales_contact_id} n'est pas du département COMMERCIAL")
    raise typer.Exit(code=1)
```

**Ce qui se passe** :
1. Appel de `user_service.get_user()` → Chemin : **Service → Repository → Base de données**
2. Vérification que l'utilisateur existe
3. Vérification que l'utilisateur est bien du département COMMERCIAL

**Détail du chemin d'exécution** :

```
user_service.get_user(sales_contact_id)
    ↓
[src/services/user_service.py:10-19]
def get_user(self, user_id: int) -> User:
    return self.repository.get(user_id)
    ↓
[src/repositories/sqlalchemy_user_repository.py:26-35]
def get(self, user_id: int) -> User:
    return self.session.query(User).filter_by(id=user_id).first()
    ↓
[Base de données] SELECT * FROM users WHERE id = ?
    ↓
Retourne un objet User ou None
```

---

### 7. Création du client via le service

**Fichier** : [src/cli/commands.py](../src/cli/commands.py#L164-L171)

```python
client = client_service.create_client(
    first_name=first_name,
    last_name=last_name,
    email=email,
    phone=phone,
    company_name=company_name,
    sales_contact_id=sales_contact_id,
)
```

**Détail du chemin d'exécution** :

```
client_service.create_client(...)
    ↓
[src/services/client_service.py:13-44]
def create_client(self, first_name, last_name, ...):
    # 1. Créer l'objet Client
    client = Client(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        company_name=company_name,
        sales_contact_id=sales_contact_id,
    )

    # 2. Persister via le repository
    self.repository.add(client)

    # 3. Retourner le client créé
    return client
    ↓
[src/repositories/sqlalchemy_client_repository.py:15-17]
def add(self, client: Client) -> None:
    self.session.add(client)      # Ajoute à la session SQLAlchemy
    self.session.commit()          # Commit la transaction en base
    ↓
[Base de données] INSERT INTO clients (first_name, last_name, ...) VALUES (?, ?, ...)
    ↓
Le client est créé en base avec un ID auto-généré
```

---

### 8. Affichage du résultat

**Fichier** : [src/cli/commands.py](../src/cli/commands.py#L174-L179)

```python
typer.echo(f"\n[SUCCÈS] Client {client.first_name} {client.last_name} créé avec succès!")
typer.echo(f"  ID: {client.id}")
typer.echo(f"  Email: {client.email}")
typer.echo(f"  Entreprise: {client.company_name}")
```

**Ce qui se passe** :
- Affichage du message de succès avec les informations du client
- L'ID est maintenant disponible car SQLAlchemy l'a récupéré après l'INSERT

---

### 9. Gestion des erreurs

**Fichier** : [src/cli/commands.py](../src/cli/commands.py#L181-L197)

```python
except IntegrityError:
    typer.echo("[ERREUR] Erreur d'intégrité: Données en double ou contrainte violée")
    raise typer.Exit(code=1)

except OperationalError:
    typer.echo("[ERREUR] Erreur de connexion à la base de données")
    raise typer.Exit(code=1)

except KeyboardInterrupt:
    typer.echo("\n[ANNULÉ] Opération annulée")
    raise typer.Exit(code=1)

except Exception as e:
    typer.echo(f"[ERREUR] Erreur inattendue: {e}")
    raise typer.Exit(code=1)
```

**Types d'erreurs gérées** :
- **IntegrityError** : Email en double, clé étrangère invalide, etc.
- **OperationalError** : Problème de connexion à la base de données
- **KeyboardInterrupt** : L'utilisateur annule avec Ctrl+C
- **Exception** : Toute autre erreur inattendue

---

## Schéma complet du flux

```
┌──────────────────────────────────────────────────────────────┐
│ 1. CLI: poetry run epicevents create-client                  │
└────────────────────┬─────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────────┐
│ 2. main.py                                                    │
│    - Crée le Container                                        │
│    - Injecte dans commands                                    │
│    - Lance l'app Typer                                        │
└────────────────────┬─────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────────┐
│ 3. Container (containers.py)                                  │
│    Configure les dépendances:                                 │
│    db_session → repositories → services                       │
└────────────────────┬─────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────────┐
│ 4. commands.py: create_client()                               │
│    - Prompts interactifs (Typer)                              │
│    - Validation des entrées (callbacks)                       │
└────────────────────┬─────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────────┐
│ 5. Récupération des services depuis le container             │
│    client_service = _container.client_service()               │
│    user_service = _container.user_service()                   │
└────────────────────┬─────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────────┐
│ 6. Validation métier                                          │
│    user_service.get_user(sales_contact_id)                    │
│      → UserService.get_user()                                 │
│        → UserRepository.get()                                 │
│          → SELECT FROM users WHERE id = ?                     │
│    Vérifie: existe? + département COMMERCIAL?                 │
└────────────────────┬─────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────────┐
│ 7. Création du client                                         │
│    client_service.create_client(...)                          │
│      → ClientService.create_client()                          │
│        1. Crée l'objet Client                                 │
│        2. repository.add(client)                              │
│          → INSERT INTO clients                                │
│        3. Return client (avec ID)                             │
└────────────────────┬─────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────────┐
│ 8. Affichage du résultat                                      │
│    [SUCCÈS] Client créé avec succès!                          │
│    ID: 1                                                      │
│    Email: ...                                                 │
└──────────────────────────────────────────────────────────────┘
```

## Points clés de l'architecture

### Séparation des responsabilités

| Couche | Responsabilité | Exemple |
|--------|----------------|---------|
| **CLI** (commands.py) | Interface utilisateur, validation des entrées | Prompts, callbacks de validation |
| **Services** (client_service.py) | Logique métier | Création d'un client, validation des règles |
| **Repositories** (sqlalchemy_client_repository.py) | Accès aux données | Requêtes SQL via SQLAlchemy |
| **Models** (client.py) | Structure des données | Définition de la table et des colonnes |
| **Container** (containers.py) | Injection de dépendances | Configuration des dépendances |

### Avantages de cette architecture

1. **Testabilité** : Chaque couche peut être testée indépendamment
2. **Maintenabilité** : Changement localisé (ex: changer de DB n'affecte que les repositories)
3. **Réutilisabilité** : Les services peuvent être utilisés depuis d'autres interfaces (API, GUI, etc.)
4. **Découplage** : Les commandes CLI ne connaissent pas les détails de la base de données
5. **Injection de dépendances** : Facilite le mocking et les tests

### Cycle de vie des objets

```
Container (Singleton pour l'app)
    ↓
db_session (Factory - nouvelle instance par commande)
    ↓
Repositories (Factory - nouveaux par commande)
    ↓
Services (Factory - nouveaux par commande)
```

Chaque commande reçoit ses propres instances de services et repositories avec une nouvelle session DB, évitant les problèmes de partage d'état entre commandes.

## Fichiers impliqués

| Fichier | Rôle |
|---------|------|
| [pyproject.toml](../pyproject.toml) | Point d'entrée de l'application |
| [src/cli/main.py](../src/cli/main.py) | Initialisation et lancement |
| [src/containers.py](../src/containers.py) | Configuration des dépendances |
| [src/cli/commands.py](../src/cli/commands.py) | Commandes CLI et validation |
| [src/services/client_service.py](../src/services/client_service.py) | Logique métier clients |
| [src/services/user_service.py](../src/services/user_service.py) | Logique métier utilisateurs |
| [src/repositories/sqlalchemy_client_repository.py](../src/repositories/sqlalchemy_client_repository.py) | Accès données clients |
| [src/repositories/sqlalchemy_user_repository.py](../src/repositories/sqlalchemy_user_repository.py) | Accès données utilisateurs |
| [src/models/client.py](../src/models/client.py) | Modèle Client |
| [src/models/user.py](../src/models/user.py) | Modèle User |
| [src/database.py](../src/database.py) | Configuration de la base de données |

## Exemple d'exécution complète

```bash
$ poetry run epicevents create-client

Prénom: Jean
Nom: Dupont
Email: jean.dupont@example.com
Téléphone: 0612345678
Nom de l'entreprise: Acme Corp
ID du contact commercial: 1

=== Création d'un nouveau client ===

[SUCCÈS] Client Jean Dupont créé avec succès!
  ID: 42
  Email: jean.dupont@example.com
  Entreprise: Acme Corp
```

**Ce qui s'est passé en coulisses** :
1. ✅ Validation de chaque input (email, téléphone, etc.)
2. ✅ Vérification que l'utilisateur ID=1 existe
3. ✅ Vérification que l'utilisateur ID=1 est COMMERCIAL
4. ✅ Création de l'objet Client en mémoire
5. ✅ INSERT en base de données
6. ✅ Récupération de l'ID auto-généré (42)
7. ✅ Affichage du résultat
