# Pattern d'Injection de Dépendances - Epic Events CRM

## Vue d'ensemble

Ce document explique le pattern d'injection de dépendances utilisé dans l'application Epic Events CRM, spécifiquement le **Pattern de Container Global avec Setter** pour les applications CLI.

## Le Pattern

### Implémentation

```python
# src/cli/commands.py

# Global container - will be set by main.py
_container = None

def set_container(container):
    """Set the dependency injection container."""
    global _container
    _container = container
```

### Flux d'utilisation

```
main.py (point d'entrée)
    ↓
1. Créer une instance du container
    container = Container()

2. Définir le container dans le module commands
    commands.set_container(container)

3. Lancer l'application Typer
    commands.app()

commands.py (commandes CLI)
    ↓
4. Accéder aux services depuis le container global
    client_service = _container.client_service()
    user_service = _container.user_service()
```

## Pourquoi ce Pattern ?

### Problème

**Typer n'a pas d'injection de dépendances native** comme FastAPI. FastAPI peut injecter des dépendances car il dispose du contexte de requête HTTP, mais les applications CLI n'ont pas ce contexte.

### Alternatives considérées

| Approche | Avantages | Inconvénients | Verdict |
|----------|-----------|---------------|---------|
| Passer le container en paramètre | Explicite | Verbeux, encombre les signatures de commandes | ❌ Rejeté |
| Utiliser `typer.Context` | Fonctionnalité intégrée à Typer | Complexe pour de nombreuses commandes | ❌ Rejeté |
| **Container global** | Simple, signatures de commandes propres | État global | ✅ **Choisi** |

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

### 2. Initialisation du Container

```python
# src/cli/main.py

def main():
    """Main entry point for the application."""
    # 1. Initialize the dependency injection container
    container = Container()

    # 2. Set the container in the commands module
    commands.set_container(container)

    # 3. Launch the Typer application
    commands.app()
```

### 3. Utilisation des Dépendances dans les Commandes

```python
# src/cli/commands.py

@app.command()
def create_client(...):
    """Create a new client."""
    # Get services from global container
    client_service = _container.client_service()
    user_service = _container.user_service()

    # Use services
    client = client_service.create_client(
        first_name=first_name,
        last_name=last_name,
        # ...
    )
```

## Avantages

### 1. **Séparation des Préoccupations**
- `main.py` : Initialisation et configuration de l'application
- `commands.py` : Logique métier et interaction utilisateur
- `containers.py` : Câblage des dépendances

### 2. **Signatures de Commandes Propres**
```python
# Avec container global (propre)
def create_client(first_name: str, last_name: str):
    service = _container.client_service()
    # ...

# Sans (verbeux)
def create_client(
    first_name: str,
    last_name: str,
    container: Container = typer.Option(...)  # ❌ Encombre la signature
):
    # ...
```

### 3. **Testabilité**
Facile d'injecter un container mock pour les tests :

```python
# In tests
from src.cli import commands

def test_create_client():
    # Create mock container
    mock_container = MockContainer()

    # Inject it
    commands.set_container(mock_container)

    # Test command
    # ...
```

### 4. **Accès Cohérent**
Toutes les commandes accèdent aux dépendances de la même manière, rendant le code cohérent et maintenable.

## Chaîne de Dépendances

La chaîne complète de dépendances pour une opération typique :

```
Commande CLI (create_client)
    ↓ (appelle)
_container.client_service()
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

### ⚠️ Anti-Pattern Service Locator ?

Certains développeurs considèrent les containers globaux comme un "anti-pattern Service Locator". Cependant, c'est acceptable pour les applications CLI quand :

✅ Le container est initialisé **une seule fois** au démarrage
✅ Le container n'est **jamais modifié** pendant l'exécution
✅ Les dépendances sont **clairement définies** dans le container
✅ L'application est **mono-thread** (typique pour les CLI)

### 🔒 Sécurité des Threads

Ce pattern n'est **pas thread-safe** par défaut. Pour les applications multi-thread, considérez :
- Utiliser le stockage local des threads (thread-local storage)
- Passer le container explicitement
- Utiliser un framework DI différent

Pour Epic Events CRM (CLI mono-thread), ce n'est pas une préoccupation.

## Patterns Similaires

Ce pattern est similaire à :
- **Flask** : `app = Flask(__name__)`
- **Django** : `settings.py` comme configuration globale
- **Pattern Singleton** : Une instance de container par application

## Pourquoi Pas de Décorateur `@inject` ?

Le framework `dependency-injector` propose un décorateur `@inject` pour l'injection automatique. **Nous ne l'utilisons pas** car il n'est pas adapté aux applications CLI Typer.

### Architecture Actuelle

```
┌─────────────────────────────────────────┐
│ Couche CLI (commands.py)                │
│ ❌ PAS de @inject                        │
│ ✅ Accès manuel au container            │
│                                          │
│ client_service = _container.client_service()
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ Couche Service (client_service.py)      │
│ ✅ Injection par constructeur (vrai DI) │
│                                          │
│ def __init__(self, repository: ClientRepository)
└─────────────────────────────────────────┘
```

### Approche Actuelle (sans `@inject`)

```python
# commands.py
@app.command()
def create_client(...):
    # Accès manuel au container
    client_service = _container.client_service()
    user_service = _container.user_service()

    # Utiliser les services
    client = client_service.create_client(...)
```

**Avantages:**
- ✅ Simple et explicite
- ✅ Pas besoin de wiring complexe
- ✅ Fonctionne directement avec Typer
- ✅ Signatures de commandes propres

### Approche Alternative (avec `@inject`)

```python
# main.py
def main():
    container = Container()
    container.wire(modules=["src.cli.commands"])  # Wiring nécessaire
    commands.app()

# commands.py
from dependency_injector.wiring import inject, Provide
from typing import Annotated

@app.command()
@inject  # Décorateur requis
def create_client(
    # Paramètres Typer (de l'utilisateur)
    first_name: str = typer.Option(...),
    last_name: str = typer.Option(...),

    # Paramètres DI (du container)
    client_service: Annotated[ClientService, Provide[Container.client_service]] = None,
    user_service: Annotated[UserService, Provide[Container.user_service]] = None,
):
    # Services injectés automatiquement
    client = client_service.create_client(...)
```

**Inconvénients pour Typer:**
- ❌ Signatures de commandes encombrées
- ❌ Confusion entre paramètres CLI et DI
- ❌ Configuration complexe (wiring requis)
- ❌ Typer ne distingue pas les paramètres CLI des paramètres DI

### Problème Principal avec Typer

Typer parse les paramètres de fonction pour créer des options CLI. Avec `@inject`, il y a confusion:

```python
@app.command()
@inject
def create_client(
    first_name: str = typer.Option(...),        # ← Paramètre CLI
    service: ClientService = Provide[...],      # ← Paramètre DI
):
    pass
```

**Typer ne sait pas distinguer** les deux types de paramètres!

### Quand Utiliser `@inject` ?

Le décorateur `@inject` est **parfait** pour:
- ✅ Applications web (Flask, Django, FastAPI)
- ✅ Fonctions utilitaires
- ✅ Workers/tasks (Celery)
- ✅ Scripts sans CLI interactif

**Documentation:** https://python-dependency-injector.ets-labs.org/wiring.html

### Notre Choix

L'accès manuel au container est **plus adapté** pour Typer car:
1. Séparation claire : Typer gère les paramètres CLI, le container gère les services
2. Simplicité : Pas de wiring complexe
3. Lisibilité : Signatures de commandes épurées
4. Compatibilité : Pas de conflits entre Typer et dependency-injector

**Note importante:** Les classes métier (`ClientService`, `UserService`) utilisent quand même la vraie injection de dépendances via leurs constructeurs!

## Ressources

### Documentation Officielle
- Dependency Injector : https://python-dependency-injector.ets-labs.org/
- Wiring et @inject : https://python-dependency-injector.ets-labs.org/wiring.html
- Discussion Typer DI : https://github.com/fastapi/typer/issues/80
- Service Locator Anti-Pattern : https://blog.ploeh.dk/2010/02/03/ServiceLocatorisanAnti-Pattern/

### Bibliothèques Alternatives
- `typer-di` : DI style FastAPI pour Typer
- `python-inject` : DI style autowiring
- `injector` : Un autre framework DI populaire

## Résumé

Le **Pattern de Container Global avec Setter** est une solution pragmatique pour l'injection de dépendances dans les applications CLI utilisant Typer. Il offre :

- ✅ Code propre et lisible
- ✅ Tests faciles
- ✅ Séparation claire des préoccupations
- ✅ Accès cohérent aux dépendances

Bien qu'il utilise un état global, il est approprié pour notre cas d'usage : une application CLI mono-thread avec des dépendances configurées une seule fois au démarrage.
