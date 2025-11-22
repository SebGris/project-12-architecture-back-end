# Externalisation de la Configuration - Architecture SOLID

## 📋 Vue d'ensemble

Ce document explique comment la configuration de l'injection de dépendances (DI) a été externalisée pour respecter le principe SOLID de **Dependency Inversion Principle (DIP)** et faciliter la gestion multi-environnements.

## 🎯 Objectifs

1. ✅ **Respecter le Dependency Inversion Principle** : Le container ne dépend plus directement des implémentations concrètes
2. ✅ **Faciliter les tests** : Permet de switcher facilement entre implémentations réelles et fakes/mocks
3. ✅ **Support multi-environnements** : Development, Testing, Production avec des configurations différentes
4. ✅ **Suivre les standards professionnels** : Twelve-Factor App, bonnes pratiques Python

## 📁 Structure des fichiers

```
project-12-architecture-back-end/
├── config/                          # ← NOUVEAU : Fichiers de configuration YAML
│   ├── development.yml              # Configuration pour développement
│   ├── testing.yml                  # Configuration pour tests
│   └── production.yml               # Configuration pour production
├── src/
│   ├── config.py                    # ← NOUVEAU : Mapping des implémentations
│   ├── containers.py                # ← MODIFIÉ : Utilise config.py
│   └── ...
├── .env.example                     # ← MODIFIÉ : Documentation des variables d'environnement
└── docs/
    └── CONFIGURATION_EXTERNALIZATION.md  # ← CE FICHIER
```

## 🔧 Comment ça fonctionne

### 1. Fichier de configuration (`src/config.py`)

Ce fichier centralise le mapping entre les noms de repositories et leurs implémentations concrètes :

```python
# src/config.py
REPOSITORY_IMPLEMENTATIONS = {
    "user": SqlAlchemyUserRepository,
    "client": SqlAlchemyClientRepository,
    "contract": SqlAlchemyContractRepository,
    "event": SqlAlchemyEventRepository,
}
```

**Avantages** :
- ✅ Un seul endroit à modifier pour changer d'implémentation
- ✅ Facile à tester : remplacer par des fakes/mocks
- ✅ Support de différentes bases de données (SQLite, PostgreSQL, MongoDB, etc.)

### 2. Container DI (`src/containers.py`)

Le container utilise maintenant `REPOSITORY_IMPLEMENTATIONS` au lieu d'importer directement les classes :

```python
# AVANT (couplage fort)
from src.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository

user_repository = providers.Factory(
    SqlAlchemyUserRepository,  # ← Implémentation hardcodée
    session=db_session,
)

# APRÈS (couplage faible)
from src.config import REPOSITORY_IMPLEMENTATIONS

user_repository = providers.Factory(
    REPOSITORY_IMPLEMENTATIONS["user"],  # ← Depuis configuration
    session=db_session,
)
```

### 3. Fichiers YAML par environnement (`config/*.yml`)

Chaque environnement a son propre fichier de configuration :

#### `config/development.yml`
```yaml
repositories:
  user: "src.repositories.sqlalchemy_user_repository.SqlAlchemyUserRepository"
  # ...

database:
  url: "sqlite:///data/epicevents.db"

app:
  debug: true
```

#### `config/testing.yml`
```yaml
repositories:
  user: "src.repositories.sqlalchemy_user_repository.SqlAlchemyUserRepository"
  # Ou bien : "tests.fakes.in_memory_user_repository.InMemoryUserRepository"

database:
  url: "sqlite:///:memory:"
```

#### `config/production.yml`
```yaml
repositories:
  user: "src.repositories.sqlalchemy_user_repository.SqlAlchemyUserRepository"

database:
  url: "${DATABASE_URL:sqlite:///data/epicevents.db}"  # Depuis variable d'env
```

## 🚀 Utilisation

### Développement (par défaut)

```bash
# Utilise config/development.yml
poetry run epicevents login
```

### Tests

```bash
# Utilise config/testing.yml
APP_ENV=testing poetry run pytest
```

### Production

```bash
# Utilise config/production.yml
APP_ENV=production epicevents login
```

## 🧪 Tests avec des Fakes

Pour tester sans base de données réelle, vous pouvez créer des repositories "fake" :

### 1. Créer un fake repository

```python
# tests/fakes/in_memory_user_repository.py
from src.repositories.user_repository import UserRepository

class InMemoryUserRepository(UserRepository):
    """Fake repository pour tests - sans BDD."""

    def __init__(self):
        self._users = {}
        self._next_id = 1

    def add(self, user):
        user.id = self._next_id
        self._users[user.id] = user
        self._next_id += 1
        return user

    def get(self, user_id):
        return self._users.get(user_id)
    # ...
```

### 2. Configurer pour les tests

```python
# src/config.py
import os

ENV = os.getenv("APP_ENV", "development")

if ENV == "testing":
    from tests.fakes.in_memory_user_repository import InMemoryUserRepository
    REPOSITORY_IMPLEMENTATIONS["user"] = InMemoryUserRepository
else:
    REPOSITORY_IMPLEMENTATIONS["user"] = SqlAlchemyUserRepository
```

## 📚 Références et Standards

Cette approche suit les standards professionnels de l'industrie :

### 1. **The Twelve-Factor App**
- **Factor III - Configuration** : https://12factor.net/config
- Stocker la config dans l'environnement, pas dans le code

### 2. **Dependency Injector Framework**
- **Configuration Provider** : https://python-dependency-injector.ets-labs.org/providers/configuration.html
- Support natif pour YAML, JSON, variables d'environnement

### 3. **Best Practices Python**
- **ArjanCodes** : https://arjancodes.com/blog/python-dependency-injection-best-practices/
- **DataCamp** : https://www.datacamp.com/tutorial/python-dependency-injection

### 4. **Testing Without Mocks**
- https://blog.boot.dev/clean-code/writing-good-unit-tests-dont-mock-database-connections/
- https://medium.com/@mayintuji/unit-test-with-real-database-in-repository-pattern-9205cd9966e4

## 🔄 Migration depuis l'ancienne version

Si vous avez du code existant qui dépend de l'ancien `containers.py` :

### Pas de changement nécessaire ! ✅

L'interface publique du container n'a pas changé. Votre code continue de fonctionner :

```python
# Toujours valide
container = Container()
auth_service = container.auth_service()
```

### Pour profiter de la nouvelle configuration

Vous pouvez maintenant :

1. **Changer d'environnement** via `APP_ENV`
2. **Utiliser des fakes pour tests** en modifiant `src/config.py`
3. **Supporter plusieurs bases de données** facilement

## 💡 Exemples d'utilisation avancée

### Exemple 1 : Switcher vers MongoDB

```python
# src/config.py
import os

if os.getenv("DATABASE_TYPE") == "mongodb":
    from src.repositories.mongodb_user_repository import MongoDBUserRepository
    REPOSITORY_IMPLEMENTATIONS["user"] = MongoDBUserRepository
else:
    REPOSITORY_IMPLEMENTATIONS["user"] = SqlAlchemyUserRepository
```

### Exemple 2 : Tests ultra-rapides avec fakes

```python
# pytest avec fakes (pas de BDD)
APP_ENV=testing USE_FAKES=true pytest

# pytest avec vraie BDD SQLite in-memory
APP_ENV=testing pytest
```

## 📊 Comparaison avant/après

| Critère | Avant | Après |
|---------|-------|-------|
| **Couplage** | Fort (imports hardcodés) | Faible (via config) |
| **Testabilité** | Difficile (mocks complexes) | Facile (fakes ou config) |
| **Multi-env** | Complexe | Simple (APP_ENV) |
| **DIP (SOLID)** | Partiellement respecté | Totalement respecté |
| **Changement de BDD** | 8+ modifications | 1 modification |

## 🤝 Contribution

Pour ajouter un nouvel environnement :

1. Créer `config/staging.yml`
2. Définir les repositories et paramètres
3. Lancer avec `APP_ENV=staging`

Pour ajouter une nouvelle implémentation :

1. Créer la classe (ex: `MongoDBUserRepository`)
2. Ajouter dans `src/config.py`
3. Tester avec les tests existants

## ❓ FAQ

**Q : Dois-je installer PyYAML ?**
R : Non, c'est optionnel. Le container fonctionne sans YAML. Pour l'utiliser : `pip install pyyaml`

**Q : Puis-je utiliser JSON au lieu de YAML ?**
R : Oui ! `config.from_json('config.json')`

**Q : Comment tester avec des fakes ?**
R : Modifiez `src/config.py` pour retourner vos fakes selon `APP_ENV`

**Q : Est-ce compatible avec l'ancien code ?**
R : Oui, 100% rétrocompatible. Aucune modification nécessaire.

## 📝 Auteur

Cette architecture a été mise en place pour respecter les principes SOLID et les standards professionnels de l'industrie.

Date : 2025-01-22
