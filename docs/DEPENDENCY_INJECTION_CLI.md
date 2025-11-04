# Injection de dépendances dans la CLI - Guide complet

Ce document explique comment l'injection de dépendances est implémentée dans l'application CLI Epic Events CRM en utilisant la bibliothèque `dependency_injector`.

## 📚 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Comment ça fonctionne](#comment-ça-fonctionne)
- [Exemple détaillé](#exemple-détaillé)
- [Avantages de cette approche](#avantages-de-cette-approche)
- [Bonnes pratiques](#bonnes-pratiques)
- [Ressources](#ressources)

## 🎯 Vue d'ensemble

L'injection de dépendances (DI) est un pattern de conception qui permet de découpler les composants d'une application. Dans notre application CLI Epic Events, nous utilisons **l'instanciation manuelle du Container** pour obtenir les services nécessaires.

### L'approche utilisée

```python
@app.command()
def create_client(
    first_name: str = typer.Option(...),
    last_name: str = typer.Option(...),
):
    # ✅ Création manuelle du container et obtention des services
    container = Container()
    client_service = container.client_service()

    # Utilisation du service
    client = client_service.create_client(...)
```

Cette approche est **simple, explicite et fonctionne parfaitement avec Typer**.

## 🏗️ Architecture

Notre architecture CLI suit une séparation claire des responsabilités :

```
src/cli/
├── main.py          # Point d'entrée - Configure le wiring pour les permissions
└── commands.py      # Commandes CLI - Crée le container manuellement

src/
├── containers.py    # Définit le conteneur de dépendances
├── services/        # Logique métier
├── repositories/    # Accès aux données
└── models/          # Entités du domaine
```

### Pourquoi séparer `main.py` et `commands.py` ?

**Raisons architecturales :**
1. **Séparation des responsabilités** : `main.py` orchestre, `commands.py` contient la logique
2. **Maintenabilité** : Plus facile de gérer plusieurs commandes dans un module dédié
3. **Testabilité** : On peut importer et tester `commands.app` indépendamment
4. **Configuration** : Le wiring pour les permissions est configuré une seule fois dans `main.py`

## ⚙️ Comment ça fonctionne

### 1. Définition du conteneur (`src/containers.py`)

Le conteneur définit **comment construire** chaque dépendance :

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    # Session de base de données
    db_session = providers.Factory(get_db_session)

    # Repository
    client_repository = providers.Factory(
        SqlAlchemyClientRepository,
        session=db_session,
    )

    # Service
    client_service = providers.Factory(
        ClientService,
        repository=client_repository,
    )
```

**Types de providers :**
- `Factory` : Crée une nouvelle instance à chaque appel
- `Singleton` : Crée une seule instance réutilisée partout
- `Configuration` : Gère la configuration de l'application

### 2. Configuration dans main.py (`src/cli/main.py`)

Le point d'entrée configure le wiring pour les décorateurs de permissions :

```python
from src.containers import Container
from src.cli import commands, permissions

def main():
    # 1. Créer le conteneur
    container = Container()

    # 2. Activer le wiring pour les permissions
    # Cela permet aux décorateurs @require_auth et @require_department
    # d'accéder à auth_service si nécessaire
    container.wire(modules=[commands, permissions])

    # 3. Lancer l'application
    try:
        commands.app()
    finally:
        # 4. Nettoyer le wiring à la fin
        container.unwire()
```

**Note importante :** Le wiring est utilisé uniquement pour les décorateurs de permissions. Les commandes elles-mêmes n'utilisent pas l'injection automatique.

### 3. Utilisation dans les commandes (`src/cli/commands.py`)

Les commandes créent manuellement le container et obtiennent les services :

```python
from src.containers import Container
from src.cli.permissions import require_department
from src.models.user import Department

@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def create_client(
    # Paramètres CLI normaux
    first_name: str = typer.Option(..., prompt="Prénom"),
    last_name: str = typer.Option(..., prompt="Nom"),
    email: str = typer.Option(..., prompt="Email"),
):
    """Créer un nouveau client dans le système CRM."""
    # Création manuelle du container
    container = Container()

    # Obtenir les services nécessaires
    client_service = container.client_service()

    # Utiliser le service
    client = client_service.create_client(
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
```

**Points importants :**
- Chaque commande crée son propre `Container()`
- On obtient les services via `container.service_name()`
- Pas de décorateur `@inject` nécessaire
- Signatures de fonctions propres (uniquement les paramètres CLI)

## 📖 Exemple détaillé

Prenons l'exemple de la commande `create_client` avec vérification de permissions :

### Étape 1 : L'utilisateur lance la commande

```bash
$ poetry run epicevents create-client
```

### Étape 2 : Le décorateur vérifie les permissions

Le décorateur `@require_department` :
1. Crée un container pour obtenir `auth_service`
2. Vérifie que l'utilisateur est connecté
3. Vérifie que l'utilisateur appartient au département COMMERCIAL ou GESTION
4. Injecte `current_user` dans `kwargs`

### Étape 3 : Typer collecte les paramètres CLI

```python
# Typer affiche les prompts et collecte les valeurs
Prénom: John
Nom: Doe
Email: john@example.com
...
```

### Étape 4 : La fonction s'exécute

```python
def create_client(
    first_name="John",
    last_name="Doe",
    email="john@example.com",
):
    # 1. Créer le container
    container = Container()

    # 2. Obtenir le service
    client_service = container.client_service()

    # 3. Utiliser le service
    client = client_service.create_client(...)
```

### Étape 5 : La chaîne de dépendances

```
Container()
    ↓
container.client_service()
    ↓ (Factory crée)
ClientService(repository=...)
    ↓ (Factory crée)
SqlAlchemyClientRepository(session=...)
    ↓ (Factory crée)
get_db_session()
    ↓
SQLAlchemy Session
```

## ✅ Avantages de cette approche

### 1. Code simple et explicite

```python
# ✅ Approche actuelle - Simple et claire
def create_client(...):
    container = Container()
    service = container.client_service()
    # ...

# ❌ Alternative avec @inject - Plus complexe
@inject
def create_client(
    ...,
    client_service=Provide[Container.client_service],
):
    # ...
```

### 2. Signatures de fonctions propres

Les signatures ne contiennent que les paramètres CLI visibles par l'utilisateur :

```python
# ✅ Propre - Uniquement les paramètres CLI
def create_client(
    first_name: str = typer.Option(...),
    last_name: str = typer.Option(...),
):
    pass

# ❌ Encombré - Mélange CLI et DI
def create_client(
    first_name: str = typer.Option(...),
    client_service: ClientService = Provide[...],  # Confus !
):
    pass
```

### 3. Isolation entre commandes

Chaque commande crée son propre container avec ses propres instances de services et de session de base de données :

```python
@app.command()
def create_client(...):
    container = Container()  # ← Nouveau container
    # Session de DB isolée pour cette commande

@app.command()
def update_client(...):
    container = Container()  # ← Nouveau container indépendant
    # Autre session de DB, pas de conflit
```

### 4. Testabilité

Facile de mocker le container dans les tests :

```python
from unittest.mock import Mock, patch

def test_create_client():
    # Mock le container
    mock_container = Mock()
    mock_service = Mock()
    mock_container.client_service.return_value = mock_service

    # Patcher Container pour retourner le mock
    with patch('src.cli.commands.Container', return_value=mock_container):
        result = runner.invoke(app, ["create-client", ...])

        # Vérifier que le service a été appelé
        mock_service.create_client.assert_called_once()
```

### 5. Pas de configuration complexe

Pas besoin de :
- Configurer le wiring pour les commandes
- Comprendre `@inject` et `Provide[...]`
- Gérer les conflits entre Typer et dependency_injector

## 🎯 Bonnes pratiques

### 1. Créer le container en début de fonction

```python
# ✅ Bon - Container créé au début
def my_command(...):
    container = Container()
    service1 = container.service1()
    service2 = container.service2()
    # Utiliser les services

# ❌ Mauvais - Multiples containers
def my_command(...):
    service1 = Container().service1()  # Container 1
    service2 = Container().service2()  # Container 2 (inutile)
```

### 2. Utiliser des Factory pour les sessions DB

```python
class Container(containers.DeclarativeContainer):
    # ✅ Factory = Nouvelle session à chaque appel
    db_session = providers.Factory(get_db_session)

    # ❌ Singleton = Même session réutilisée (dangereux !)
    # db_session = providers.Singleton(get_db_session)
```

### 3. Accéder à current_user avec **kwargs

Les décorateurs de permissions injectent `current_user` dans `kwargs` :

```python
@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def update_client(
    client_id: int = typer.Option(...),
    **kwargs  # ← Pour recevoir current_user
):
    container = Container()
    client_service = container.client_service()

    # Récupérer l'utilisateur du décorateur
    current_user = kwargs.get('current_user')

    # Utiliser current_user pour les vérifications
    client = client_service.get_client_by_id(client_id)
    if not check_client_ownership(current_user, client):
        print_error("Accès refusé")
        raise typer.Exit(code=1)
```

### 4. Ne pas stocker le container globalement

```python
# ❌ Mauvais - Variable globale
_container = None

def set_container(container):
    global _container
    _container = container

# ✅ Bon - Container local
def my_command(...):
    container = Container()
```

## 🔄 Comparaison avec d'autres approches

### Approche 1 : Variable globale

```python
# ❌ Problèmes :
# - État global
# - Couplage fort
# - Tests difficiles

_container = None

def set_container(container):
    global _container
    _container = container

def create_client(...):
    service = _container.client_service()
```

### Approche 2 : Injection automatique avec @inject

```python
# ❌ Problèmes :
# - Signatures encombrées
# - Confusion avec Typer
# - Configuration complexe

@inject
def create_client(
    first_name: str = typer.Option(...),
    client_service: ClientService = Provide[Container.client_service],
):
    pass
```

### Approche 3 : Instanciation manuelle (actuelle)

```python
# ✅✅ Avantages :
# - Simple et explicite
# - Signatures propres
# - Facile à tester
# - Pas de configuration

def create_client(
    first_name: str = typer.Option(...),
):
    container = Container()
    service = container.client_service()
    # ...
```

## 📝 Exemple complet

Voici un exemple complet d'une commande avec permissions et vérifications :

```python
from src.containers import Container
from src.cli.permissions import require_department, check_client_ownership
from src.models.user import Department

@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def update_client(
    client_id: int = typer.Option(..., prompt="ID du client"),
    first_name: str = typer.Option(None, prompt="Nouveau prénom (laisser vide pour ne pas changer)"),
    last_name: str = typer.Option(None, prompt="Nouveau nom (laisser vide pour ne pas changer)"),
    **kwargs  # Pour recevoir current_user du décorateur
):
    """
    Mettre à jour les informations d'un client existant.

    Seuls les commerciaux peuvent modifier leurs propres clients.
    L'équipe GESTION peut modifier tous les clients.
    """
    # 1. Créer le container et obtenir les services
    container = Container()
    client_service = container.client_service()

    # 2. Récupérer l'utilisateur courant (injecté par le décorateur)
    current_user = kwargs.get('current_user')

    # 3. Récupérer le client
    try:
        client = client_service.get_client_by_id(client_id)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(code=1)

    # 4. Vérifier les permissions
    if not check_client_ownership(current_user, client):
        print_error("Vous n'avez pas accès à ce client")
        raise typer.Exit(code=1)

    # 5. Mettre à jour le client
    try:
        updated_client = client_service.update_client(
            client_id=client_id,
            first_name=first_name if first_name else None,
            last_name=last_name if last_name else None,
        )
        print_success(f"Client {updated_client.id} mis à jour avec succès")
    except Exception as e:
        print_error(f"Erreur: {str(e)}")
        raise typer.Exit(code=1)
```

## 📚 Ressources

### Documentation officielle

- **[Dependency Injector - Documentation officielle](https://python-dependency-injector.ets-labs.org/)**
  - Guide complet du framework

- **[Providers Documentation](https://python-dependency-injector.ets-labs.org/providers/index.html)**
  - Détails sur Factory, Singleton, etc.

- **[Typer - Documentation officielle](https://typer.tiangolo.com/)**
  - Framework CLI utilisé dans ce projet

### Articles et tutoriels

- **[Dependency Injection in Python - Real Python](https://realpython.com/python-dependency-injection/)**
  - Introduction aux concepts de DI en Python

- **[Service Locator Pattern](https://martinfowler.com/articles/injection.html)**
  - Article de Martin Fowler sur l'injection de dépendances

## 🐛 Dépannage

### Erreur : "Provider is not defined"

```python
# ❌ Erreur
container = Container()
service = container.wrong_name()

# ✅ Solution : Vérifier que le provider existe dans containers.py
service = container.client_service()
```

### Erreur : Session de base de données fermée

```python
# ❌ Problème : Réutilisation du même container
container = Container()

def command1():
    service = container.client_service()  # Session fermée après usage

def command2():
    service = container.client_service()  # Réutilise la même session fermée

# ✅ Solution : Nouveau container dans chaque commande
def command1():
    container = Container()
    service = container.client_service()

def command2():
    container = Container()
    service = container.client_service()
```

### current_user est None

```python
# ❌ Problème : Oubli de **kwargs
@require_department(Department.GESTION)
def my_command(param: str = typer.Option(...)):
    current_user = kwargs.get('current_user')  # NameError !

# ✅ Solution : Ajouter **kwargs
@require_department(Department.GESTION)
def my_command(param: str = typer.Option(...), **kwargs):
    current_user = kwargs.get('current_user')  # ✓
```

## 📝 Résumé

L'instanciation manuelle du Container offre :

1. ✅ **Simplicité** - Code facile à comprendre et maintenir
2. ✅ **Signatures propres** - Pas de paramètres DI dans les fonctions CLI
3. ✅ **Isolation** - Chaque commande a ses propres dépendances
4. ✅ **Testabilité** - Facile de mocker le container
5. ✅ **Pas de magie** - Le flux est explicite et prévisible

Cette approche est recommandée pour les applications CLI avec Typer qui n'ont pas besoin d'injection automatique complexe !
