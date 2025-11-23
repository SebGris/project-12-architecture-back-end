# Pattern d'Injection de Dépendances - Epic Events CRM

## Vue d'ensemble

Ce document explique le pattern d'injection de dépendances utilisé dans l'application Epic Events CRM. Le projet utilise **l'instanciation manuelle du Container** dans chaque commande CLI.

## Le Pattern

### Implémentation

```python
# src/cli/commands/user_commands.py

import typer
from src.containers import Container
from src.cli.permissions import require_department
from src.models.user import Department

# Créer l'instance Typer pour ce module
app = typer.Typer()

@app.command("create-user")
@require_department(Department.GESTION)
def create_user(
    username: str = typer.Option(..., prompt="Nom d'utilisateur"),
    # ... autres paramètres
):
    # Manually get services from container
    container = Container()
    user_service = container.user_service()

    # Use the service
    user = user_service.create_user(...)
```

### Flux d'utilisation

```
main.py (point d'entrée)
    ↓
1. Créer une instance du container (pour le wiring des permissions)
    container = Container()

2. Wire les 5 modules de commandes + permissions (pour les décorateurs)
    container.wire(modules=[
        auth_commands,
        user_commands,
        client_commands,
        contract_commands,
        event_commands,
        permissions
    ])

3. Lancer l'application Typer
    commands.app()  # commands.app défini dans commands/__init__.py

Modules de commandes (ex: client_commands.py, user_commands.py)
    ↓
4. Chaque module crée sa propre instance Typer
    app = typer.Typer()

5. Créer une instance du container dans chaque commande
    container = Container()

6. Obtenir les services nécessaires
    client_service = container.client_service()
    user_service = container.user_service()

7. Utiliser les services
    client = client_service.create_client(...)
```

## Pourquoi ce Pattern ?

### Problème

**Typer n'a pas d'injection de dépendances native** comme FastAPI. FastAPI peut injecter des dépendances car il dispose du contexte de requête HTTP, mais les applications CLI n'ont pas ce contexte.

### Approche choisie

Le projet utilise **l'instanciation manuelle** du container dans chaque fonction de commande. C'est simple, explicite et fonctionne bien avec Typer.

**Avantages:**
- ✅ Simple et explicite
- ✅ Pas besoin de wiring complexe pour les commandes
- ✅ Fonctionne directement avec Typer
- ✅ Signatures de commandes propres (pas de paramètres DI)
- ✅ Facile à comprendre pour les débutants

**Inconvénients:**
- ⚠️ Répétition du code `container = Container()`
- ⚠️ Dépendances non visibles dans la signature de fonction

### Référence

Discussion sur le GitHub de Typer : https://github.com/fastapi/typer/issues/80

## Exemples de Code

### 1. Définition du Container

```python
# src/containers.py

from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    """Dependency injection container for Epic Events CRM."""

    # Database session factory
    db_session = providers.Factory(get_db_session)

    # Repositories
    client_repository = providers.Factory(
        SqlAlchemyClientRepository,
        session=db_session,
    )

    # Services
    client_service = providers.Factory(
        ClientService,
        repository=client_repository,
    )
```

### 2. Initialisation dans main.py

```python
# src/cli/main.py

from src.containers import Container
from src.cli import commands, permissions
from src.cli.commands import (
    auth_commands,
    user_commands,
    client_commands,
    contract_commands,
    event_commands
)

def main():
    """Main entry point for the application."""
    # 1. Initialize the dependency injection container
    container = Container()

    # 2. Wire the 5 command modules + permissions
    # This allows permission decorators to access auth_service
    container.wire(modules=[
        auth_commands,      # Module authentification
        user_commands,      # Module utilisateurs
        client_commands,    # Module clients
        contract_commands,  # Module contrats
        event_commands,     # Module événements
        permissions         # Décorateurs de permissions
    ])

    # 3. Launch the Typer application
    try:
        commands.app()  # Defined in commands/__init__.py
    finally:
        # 4. Clean up
        container.unwire()
```

**Note:** Le wiring est configuré pour les **5 modules de commandes** plus le module `permissions` pour permettre aux décorateurs (`@require_auth`, `@require_department`) d'accéder à `auth_service`.

### 3. Utilisation dans les Commandes

```python
# src/cli/commands/client_commands.py

import typer
from src.containers import Container
from src.cli.permissions import require_department
from src.models.user import Department

# Créer l'instance Typer pour ce module
app = typer.Typer()

@app.command("create-client")
@require_department(Department.COMMERCIAL, Department.GESTION)
def create_client(
    first_name: str = typer.Option(..., prompt="Prénom"),
    last_name: str = typer.Option(..., prompt="Nom"),
    # ... autres paramètres Typer
):
    """Create a new client."""
    # Manually get services from container
    container = Container()
    client_service = container.client_service()
    auth_service = container.auth_service()

    # Use services
    client = client_service.create_client(
        first_name=first_name,
        last_name=last_name,
        # ...
    )
```

### 4. Accès à current_user depuis les décorateurs

Les décorateurs de permissions injectent `current_user` dans `kwargs`:

```python
# src/cli/commands/client_commands.py

@app.command("update-client")
@require_department(Department.COMMERCIAL, Department.GESTION)
def update_client(
    client_id: int = typer.Option(...),
    # ... autres paramètres
    **kwargs  # Pour recevoir current_user du décorateur
):
    container = Container()
    client_service = container.client_service()

    # Récupérer l'utilisateur du décorateur
    current_user = kwargs.get('current_user')

    # Vérifier les permissions
    client = client_service.get_client_by_id(client_id)
    if not check_client_ownership(current_user, client):
        print_error("Vous n'avez pas accès à ce client")
        raise typer.Exit(code=1)
```

## Avantages

### 1. **Séparation des Préoccupations**
- `main.py` : Initialisation et configuration de l'application
- `commands.py` : Logique métier et interaction utilisateur
- `containers.py` : Câblage des dépendances

### 2. **Signatures de Commandes Propres**
```python
# Avec instanciation manuelle (propre)
def create_client(first_name: str, last_name: str):
    container = Container()
    service = container.client_service()
    # ...

# Alternative avec injection (verbeux)
def create_client(
    first_name: str,
    last_name: str,
    client_service: ClientService = Provide[Container.client_service]  # ❌ Encombre
):
    # ...
```

### 3. **Testabilité**
Facile de tester en mockant le container :

```python
# In tests
from unittest.mock import Mock, patch

def test_create_client():
    # Mock container and services
    mock_container = Mock()
    mock_service = Mock()
    mock_container.client_service.return_value = mock_service

    with patch('src.cli.commands.Container', return_value=mock_container):
        # Test command
        result = runner.invoke(app, ["create-client", ...])
```

### 4. **Simplicité**
Pas besoin de comprendre le wiring, `@inject`, ou `Provide[...]`. Juste créer le container et obtenir le service.

## Chaîne de Dépendances

La chaîne complète de dépendances pour une opération typique :

```
Commande CLI (create_client)
    ↓ (crée)
Container()
    ↓ (appelle)
container.client_service()
    ↓ (crée & injecte)
ClientService(repository=...)
    ↓ (utilise)
SqlAlchemyClientRepository(session=...)
    ↓ (utilise)
get_db_session()
    ↓ (retourne)
SQLAlchemy Session
```

## Notes Importantes

### 🔄 Nouvelle instance à chaque commande

Chaque commande crée une **nouvelle instance** du container. C'est voulu car :
- ✅ Isolation entre les commandes
- ✅ Pas d'état partagé
- ✅ Sessions de base de données propres

### 🎯 Les Providers Factory

Le container utilise des `Factory` providers qui créent de nouvelles instances à chaque appel :

```python
class Container(containers.DeclarativeContainer):
    # Factory = Nouvelle instance à chaque appel
    db_session = providers.Factory(get_db_session)
    client_service = providers.Factory(ClientService, repository=...)
```

Cela garantit que chaque commande a sa propre session de base de données.

### 🔒 Thread Safety

Ce pattern est **thread-safe** car chaque commande crée son propre container. Il n'y a pas d'état global partagé.

## Pourquoi Pas de Décorateur `@inject` ?

Le framework `dependency-injector` propose un décorateur `@inject` pour l'injection automatique. **Nous ne l'utilisons pas** dans les commandes CLI car :

1. **Signatures encombrées** - Mélange les paramètres CLI et les paramètres DI
2. **Confusion avec Typer** - Typer ne distingue pas les paramètres CLI des paramètres DI
3. **Complexité inutile** - L'instanciation manuelle est plus simple et claire
4. **Pas d'avantage réel** - Pour les CLI, l'injection manuelle est suffisante

### Note sur le Wiring

Le wiring dans `main.py` existe uniquement pour les **décorateurs de permissions** (`@require_auth`, `@require_department`) qui peuvent potentiellement utiliser l'injection. Les commandes elles-mêmes n'utilisent pas l'injection automatique.

## Patterns Similaires

Ce pattern est similaire à :
- **Service Locator** : Le container est un registre de services
- **Factory Pattern** : Le container fabrique les services à la demande
- **Manual DI** : Injection de dépendances manuelle et explicite

## Alternatives non retenues

### Alternative 1 : Container Global avec Setter

```python
# ❌ Non utilisé (ancien pattern)
_container = None

def set_container(container):
    global _container
    _container = container

def create_client(...):
    service = _container.client_service()
```

**Pourquoi rejeté :** État global, plus complexe sans avantage réel.

### Alternative 2 : Injection Automatique avec @inject

```python
# ❌ Non utilisé
@inject
def create_client(
    first_name: str = typer.Option(...),
    client_service: ClientService = Provide[Container.client_service],
):
    pass
```

**Pourquoi rejeté :** Signatures encombrées, confusion avec Typer.

### Alternative 3 : Context de Typer

```python
# ❌ Non utilisé
@app.callback()
def main(ctx: typer.Context):
    ctx.obj = Container()

def create_client(ctx: typer.Context, ...):
    service = ctx.obj.client_service()
```

**Pourquoi rejeté :** Nécessite de passer `ctx` partout.

## Ressources

### Documentation Officielle
- Dependency Injector : https://python-dependency-injector.ets-labs.org/
- Discussion Typer DI : https://github.com/fastapi/typer/issues/80
- Service Locator Pattern : https://martinfowler.com/articles/injection.html

## Résumé

Le pattern d'**instanciation manuelle du Container** est une solution pragmatique pour l'injection de dépendances dans les applications CLI utilisant Typer. Il offre :

- ✅ Code simple et explicite
- ✅ Tests faciles
- ✅ Séparation claire des préoccupations
- ✅ Pas de complexité inutile
- ✅ Thread-safe par design

Cette approche est appropriée pour notre cas d'usage : une application CLI où chaque commande est indépendante et crée ses propres dépendances.
