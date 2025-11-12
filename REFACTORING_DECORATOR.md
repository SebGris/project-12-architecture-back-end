# Refactoring du décorateur `require_department`

## Contexte

Le décorateur `require_department` présentait deux problèmes majeurs d'incompatibilité avec Typer :

1. **Le `auth_service` n'était pas disponible dans les kwargs** - Le décorateur s'attendait à recevoir `auth_service` via les kwargs, mais celui-ci n'était jamais injecté.
2. **Les `**kwargs` sont incompatibles avec Typer** - Typer utilise l'introspection des signatures de fonction pour générer l'interface CLI, et `**kwargs` crée de l'ambiguïté.

## Solutions implémentées

### 1. Instanciation directe de `auth_service` dans le décorateur

**Avant :**
```python
def wrapper(*args, **kwargs):
    # Get auth_service from kwargs (injected by dependency_injector)
    auth_service = kwargs.get("auth_service")  # ❌ Jamais disponible
```

**Après :**
```python
def wrapper(*args, **kwargs):
    # Instantiate auth_service directly from container
    from src.containers import Container
    container = Container()
    auth_service = container.auth_service()  # ✅ Autonome
```

**Avantages :**
- Le décorateur est autonome et n'a pas de dépendances externes
- Plus besoin d'injecter `auth_service` via kwargs
- Simplifie l'architecture

### 2. Suppression de tous les `**kwargs` des commandes

**Avant :**
```python
@app.command()
@require_department(Department.GESTION)
def create_user(
    username: str = typer.Option(...),
    # ... autres paramètres
    **kwargs,  # ❌ Incompatible avec Typer
):
    pass
```

**Après :**
```python
@app.command()
@require_department(Department.GESTION)
def create_user(
    username: str = typer.Option(...),
    # ... autres paramètres
):  # ✅ Signature explicite
    pass
```

**Avantages :**
- Compatible avec l'introspection de Typer
- Signatures de fonctions claires et explicites
- Évite les erreurs "unexpected keyword argument"

### 3. Injection intelligente de `current_user`

Le décorateur utilise maintenant `inspect.signature()` pour injecter `current_user` uniquement si la fonction l'attend :

```python
# Inject current_user only if the function expects it
sig = inspect.signature(func)
if "current_user" in sig.parameters:
    kwargs["current_user"] = user

return func(*args, **kwargs)
```

**Avantages :**
- Flexible : les fonctions peuvent choisir d'utiliser `current_user` ou non
- Pas de breaking changes : les fonctions qui récupèrent `current_user` via `auth_service.get_current_user()` continuent de fonctionner
- Évite les erreurs "unexpected keyword argument"

## Fichiers modifiés

### 1. `src/cli/permissions.py`

```python
"""Permission decorators and checks for Epic Events CRM CLI.

This module provides decorators to enforce permissions based on user roles/departments.
"""

from functools import wraps
from typing import Callable
import inspect  # ✅ Ajouté

import typer

from src.cli.console import print_error, print_separator
from src.models.user import Department, User


def require_department(
    *allowed_departments: Department,
):
    """Decorator to require authentication and optionally specific department(s).

    This decorator checks if the user is authenticated before executing the command.
    If departments are specified, it also checks if the user belongs to one of them.
    If no departments are specified, it only requires authentication (behaves like require_auth).

    The decorator instantiates auth_service internally and injects current_user
    as an explicit parameter to the decorated function.

    Args:
        *allowed_departments: Variable number of Department enums (optional)

    Returns:
        A decorator function

    Examples:
        # Require only authentication (no department restriction)
        @app.command()
        @require_department()
        def my_command(current_user: User):
            # current_user is automatically injected
            pass

        # Require specific department(s)
        @app.command()
        @require_department(Department.GESTION, Department.COMMERCIAL)
        def restricted_command(current_user: User):
            # current_user is automatically injected
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Instantiate auth_service directly from container
            from src.containers import Container
            container = Container()
            auth_service = container.auth_service()

            # Check if user is authenticated
            user = auth_service.get_current_user()

            if not user:
                print_separator()
                print_error(
                    "Vous devez être connecté pour effectuer cette action"
                )
                print_error("Utilisez 'epicevents login' pour vous connecter")
                print_separator()
                raise typer.Exit(code=1)

            # Check if user has the required department (only if departments are specified)
            if (
                allowed_departments
                and user.department not in allowed_departments
            ):
                dept_names = ", ".join([d.value for d in allowed_departments])
                print_separator()
                print_error("Action non autorisée pour votre département")
                print_error(f"Départements autorisés : {dept_names}")
                print_error(f"Votre département : {user.department.value}")
                print_separator()
                raise typer.Exit(code=1)

            # Inject current_user only if the function expects it
            sig = inspect.signature(func)
            if "current_user" in sig.parameters:
                kwargs["current_user"] = user

            return func(*args, **kwargs)

        return wrapper

    return decorator
```

### 2. `src/cli/commands.py`

**Changements principaux :**

1. **Import :** Suppression de l'import `User` (non utilisé)
   ```python
   # Avant
   from src.models.user import Department, User

   # Après
   from src.models.user import Department
   ```

2. **Suppression de tous les `**kwargs` :**
   - ✅ `create_client()` - ligne 238
   - ✅ `create_user()` - ligne 396
   - ✅ `create_contract()` - ligne 504
   - ✅ `create_event()` - ligne 644
   - ✅ `assign_support()` - ligne 809
   - ✅ `filter_unsigned_contracts()` - ligne 902
   - ✅ `filter_unpaid_contracts()` - ligne 952
   - ✅ `filter_unassigned_events()` - ligne 1006
   - ✅ `filter_my_events()` - ligne 1069
   - ✅ `update_client()` - ligne 1175
   - ✅ `update_contract()` - ligne 1299
   - ✅ `update_event_attendees()` - ligne 1434

## Tests effectués

### ✅ Tests réussis

1. **`poetry run epicevents whoami`**
   ```
   ID: 1
   Nom d'utilisateur: admin
   Nom complet: Alice Dubois
   Email: admin@epicevents.com
   Téléphone: +33123456789
   Département: GESTION
   ```

2. **`poetry run epicevents filter-unsigned-contracts`**
   ```
   ID: 2
   Client: Jean Dupont (Dupont SA)
   Contact commercial: John Smith (ID: 2)
   Montant total: 8000.00 €
   Montant restant à payer: 8000.00 €
   Date de création: 2025-11-04

   [SUCCES] Total: 3 contrat(s) non signé(s)
   ```

3. **Compilation Python**
   ```bash
   python -m py_compile src/cli/commands.py src/cli/permissions.py
   # ✅ Aucune erreur
   ```

## Résumé des bénéfices

| Aspect | Avant | Après |
|--------|-------|-------|
| **Compatible Typer** | ❌ Erreurs avec `**kwargs` | ✅ Signatures explicites |
| **Dépendances** | ❌ `auth_service` attendu dans kwargs | ✅ Instancié dans le décorateur |
| **Flexibilité** | ❌ `current_user` forcé partout | ✅ Injection conditionnelle |
| **Maintenabilité** | ❌ Code obscur avec kwargs | ✅ Intentions explicites |
| **Breaking changes** | N/A | ✅ Aucun (rétrocompatible) |

## Conclusion

La refactorisation résout les deux problèmes identifiés :

1. ✅ **auth_service** : Instancié directement dans le décorateur
2. ✅ **kwargs** : Supprimés de toutes les commandes

Le code est maintenant **propre, maintenable et pleinement compatible avec Typer** ! 🎉
