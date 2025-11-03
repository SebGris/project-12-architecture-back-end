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

L'injection de dépendances (DI) est un pattern de conception qui permet de découpler les composants d'une application. Au lieu de créer des dépendances directement dans le code, elles sont **injectées automatiquement** par un conteneur.

### Avant l'injection de dépendances

```python
def create_client(...):
    # ❌ Création manuelle des dépendances
    session = get_db_session()
    repository = SqlAlchemyClientRepository(session)
    service = ClientService(repository)

    # Utilisation du service
    client = service.create_client(...)
```

### Après l'injection de dépendances

```python
@inject
def create_client(
    ...,
    client_service=Provide[Container.client_service],  # ✅ Injection automatique
):
    # Le service est déjà prêt à l'emploi !
    client = client_service.create_client(...)
```

## 🏗️ Architecture

Notre architecture CLI suit une séparation claire des responsabilités :

```
src/cli/
├── main.py          # Point d'entrée - Configure le wiring
└── commands.py      # Commandes CLI - Reçoit les dépendances injectées

src/
├── containers.py    # Définit le conteneur de dépendances
├── services/        # Logique métier
├── repositories/    # Accès aux données
└── models/          # Entités du domaine
```

### Pourquoi séparer `main.py` et `commands.py` ?

**Raisons techniques :**
1. **Le wiring nécessite un module à scanner** : `container.wire(modules=[commands])` doit scanner un module existant
2. **Ordre d'exécution** : Le wiring doit s'exécuter AVANT que les commandes soient appelées
3. **Limitation Python** : On ne peut pas scanner un module pendant qu'il s'exécute

**Raisons architecturales :**
4. **Séparation des responsabilités** : `main.py` orchestre, `commands.py` contient la logique
5. **Maintenabilité** : Plus facile de gérer plusieurs commandes dans un module dédié
6. **Testabilité** : On peut importer et tester `commands.app` indépendamment

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

### 2. Configuration du wiring (`src/cli/main.py`)

Le point d'entrée configure le wiring pour activer l'injection automatique :

```python
from src.containers import Container
from src.cli import commands

def main():
    # 1. Créer le conteneur
    container = Container()

    # 2. Activer le wiring
    # Cela scanne le module 'commands' pour trouver les @inject
    container.wire(modules=[commands])

    # 3. Lancer l'application
    try:
        commands.app()
    finally:
        # 4. Nettoyer le wiring à la fin
        container.unwire()
```

**Ce que fait `container.wire()` :**
1. Scanne le module `commands` pour trouver les fonctions avec `@inject`
2. Identifie les paramètres avec `Provide[Container.xxx]`
3. Configure l'injection automatique pour ces paramètres
4. Quand la fonction est appelée, les dépendances sont injectées automatiquement

### 3. Déclaration des dépendances (`src/cli/commands.py`)

Les commandes déclarent leurs dépendances via le décorateur `@inject` :

```python
from dependency_injector.wiring import inject, Provide
from src.containers import Container

@app.command()
@inject
def create_client(
    # Paramètres CLI normaux
    first_name: str = typer.Option(...),
    last_name: str = typer.Option(...),

    # Dépendances injectées automatiquement
    client_service=Provide[Container.client_service],
    user_service=Provide[Container.user_service],
):
    # Les services sont déjà instanciés et prêts !
    client = client_service.create_client(...)
```

**Points importants :**
- `@inject` : Décorateur qui active l'injection pour cette fonction
- `Provide[Container.xxx]` : Indique quelle dépendance injecter
- Ces paramètres **ne sont pas des options CLI** - ils sont invisibles pour l'utilisateur
- Le wiring les remplit automatiquement avant l'exécution de la fonction

## 📖 Exemple détaillé

Prenons l'exemple de la commande `create_client` :

### Étape 1 : L'utilisateur lance la commande

```bash
$ poetry run epicevents create-client
```

### Étape 2 : Typer collecte les paramètres CLI

```python
# Typer affiche les prompts et collecte les valeurs
Prénom: John
Nom: Doe
Email: john@example.com
...
```

### Étape 3 : Le wiring injecte les dépendances

Avant d'appeler `create_client()`, le wiring :

1. Résout `client_service=Provide[Container.client_service]`
   - Appelle `container.client_service()`
   - Qui crée un `ClientService` avec ses dépendances

2. Résout `user_service=Provide[Container.user_service]`
   - Appelle `container.user_service()`
   - Qui crée un `UserService` avec ses dépendances

### Étape 4 : La fonction s'exécute

```python
def create_client(
    first_name="John",
    last_name="Doe",
    email="john@example.com",
    ...,
    client_service=<ClientService instance>,  # ✅ Injecté !
    user_service=<UserService instance>,      # ✅ Injecté !
):
    # Le code s'exécute avec tout ce dont il a besoin
    client = client_service.create_client(...)
```

## ✅ Avantages de cette approche

### 1. Code plus propre

**Avant :**
```python
# Global container
_container = None

def set_container(container):
    global _container
    _container = container

def create_client(...):
    service = _container.client_service()  # ❌ Variable globale
```

**Après :**
```python
@inject
def create_client(
    ...,
    client_service=Provide[Container.client_service],  # ✅ Explicite
):
    pass
```

### 2. Testabilité améliorée

```python
def test_create_client():
    # Mock des services
    mock_client_service = Mock()
    mock_user_service = Mock()

    # Override des providers pour les tests
    with container.client_service.override(mock_client_service):
        with container.user_service.override(mock_user_service):
            # Test de la commande avec des mocks
            result = runner.invoke(app, ["create-client", ...])
```

### 3. Dépendances explicites

Chaque fonction déclare clairement ses dépendances dans sa signature :

```python
@inject
def create_contract(
    ...,
    contract_service=Provide[Container.contract_service],  # ← Visible !
    client_service=Provide[Container.client_service],      # ← Visible !
):
    pass
```

On voit immédiatement :
- Quels services sont utilisés
- Quelles sont les dépendances externes
- Ce qu'il faut mocker dans les tests

### 4. Pas de variable globale

Plus besoin de `_container` global ou de `set_container()` !

### 5. Configuration centralisée

Toute la logique de création des dépendances est dans `containers.py` :
- Facile à maintenir
- Un seul endroit à modifier
- Cohérence garantie

## 🎯 Bonnes pratiques

### 1. Toujours utiliser `@inject` avec `Provide`

```python
# ✅ Bon
@inject
def my_command(
    service=Provide[Container.service],
):
    pass

# ❌ Mauvais - L'injection ne fonctionnera pas
def my_command(
    service=Provide[Container.service],  # Manque @inject
):
    pass
```

### 2. Mettre les dépendances en dernier

```python
# ✅ Bon - Paramètres CLI d'abord, dépendances à la fin
@inject
def create_client(
    first_name: str = typer.Option(...),
    last_name: str = typer.Option(...),
    client_service=Provide[Container.client_service],
):
    pass

# ❌ Mauvais - Mélanger les types de paramètres
@inject
def create_client(
    client_service=Provide[Container.client_service],
    first_name: str = typer.Option(...),
):
    pass
```

### 3. Toujours nettoyer avec `unwire()`

```python
def main():
    container = Container()
    container.wire(modules=[commands])

    try:
        commands.app()
    finally:
        container.unwire()  # ✅ Important pour éviter les fuites mémoire
```

### 4. Utiliser des Factory pour les sessions de base de données

```python
class Container(containers.DeclarativeContainer):
    # ✅ Factory = Nouvelle session à chaque appel
    db_session = providers.Factory(get_db_session)

    # ❌ Singleton = Réutilise la même session (dangereux !)
    # db_session = providers.Singleton(get_db_session)
```

### 5. Garder `main.py` et `commands.py` séparés

```python
# ✅ Bon - Modules séparés
# main.py
container.wire(modules=[commands])

# ❌ Mauvais - Tout dans main.py
container.wire(modules=[__name__])  # Ne fonctionnera pas !
```

## 📚 Ressources

### Documentation officielle

- **[Dependency Injector - Documentation officielle](https://python-dependency-injector.ets-labs.org/)**
  - Guide complet du framework

- **[CLI Application Tutorial](https://python-dependency-injector.ets-labs.org/tutorials/cli.html)**
  - Tutoriel officiel pour les applications CLI
  - Exemple complet de "Movie Lister"

- **[Wiring Feature](https://python-dependency-injector.ets-labs.org/wiring.html)**
  - Documentation détaillée sur le wiring
  - Exemples avancés avec `@inject` et `Provide`

### Articles et tutoriels

- **[Dependency Injection in Python - Snyk Blog](https://snyk.io/blog/dependency-injection-python/)**
  - Introduction aux concepts de DI en Python

- **[Python Dependency Injector - Medium](https://medium.com/@rmogylatov/dependency-injector-python-dependency-injection-framework-eeb9f5c6db8b)**
  - Article de l'auteur du framework

### Typer

- **[Typer - Documentation officielle](https://typer.tiangolo.com/)**
  - Framework CLI utilisé dans ce projet

- **[Using the Context - Typer](https://typer.tiangolo.com/tutorial/commands/context/)**
  - Alternative avec `ctx.obj` (approche différente)

## 🔄 Comparaison avec d'autres approches

### Approche 1 : Variable globale (ancienne version)

```python
# ❌ Problèmes :
# - Variable globale
# - Couplage fort
# - Difficile à tester

_container = None

def set_container(container):
    global _container
    _container = container

def create_client(...):
    service = _container.client_service()
```

### Approche 2 : Context de Typer

```python
# ✅ Fonctionne, mais moins élégant
@app.callback()
def main(ctx: typer.Context):
    ctx.obj = Container()

@app.command()
def create_client(ctx: typer.Context, ...):
    service = ctx.obj.client_service()
```

### Approche 3 : Dependency Injector avec wiring (actuelle)

```python
# ✅✅ Meilleure approche :
# - Pas de global
# - Injection automatique
# - Dépendances explicites
# - Facile à tester

@inject
def create_client(
    ...,
    service=Provide[Container.client_service],
):
    pass
```

## 🐛 Dépannage

### Erreur : "Provider is not defined"

```python
# ❌ Erreur
service=Provide[Container.wrong_name]

# ✅ Solution : Vérifier que le provider existe dans containers.py
service=Provide[Container.client_service]
```

### Erreur : "Injection is not working"

```python
# ❌ Oublié le décorateur @inject
def my_command(service=Provide[Container.service]):
    pass

# ✅ Ajouter @inject
@inject
def my_command(service=Provide[Container.service]):
    pass
```

### Erreur : "Container is not wired"

```python
# ❌ Oublié container.wire()
def main():
    container = Container()
    commands.app()

# ✅ Ajouter le wiring
def main():
    container = Container()
    container.wire(modules=[commands])
    commands.app()
```

## 📝 Résumé

L'injection de dépendances avec `dependency_injector` offre :

1. ✅ **Code plus propre** - Pas de variables globales
2. ✅ **Testabilité** - Facile de mocker les dépendances
3. ✅ **Maintenabilité** - Configuration centralisée
4. ✅ **Explicite** - Les dépendances sont visibles dans la signature
5. ✅ **Professionnel** - Pattern standard de l'industrie

Cette approche est recommandée pour tous les projets Python nécessitant une gestion propre des dépendances !
