# Organisation des Sous-Applications Typer

Ce document explique le code utilisé dans [src/cli/commands/__init__.py](../src/cli/commands/__init__.py) pour organiser l'application CLI en sous-applications modulaires.

## Architecture Modulaire

Depuis le refactoring, les commandes sont organisées en **5 modules séparés** dans le répertoire `src/cli/commands/` :

1. **auth_commands.py** - Authentification (login, logout, whoami)
2. **user_commands.py** - Gestion des utilisateurs
3. **client_commands.py** - Gestion des clients
4. **contract_commands.py** - Gestion des contrats
5. **event_commands.py** - Gestion des événements

## Le Code Expliqué

### Création des sous-applications (dans chaque module)

Chaque module crée sa propre instance Typer :

```python
# Dans auth_commands.py
import typer
app = typer.Typer()

@app.command()
def login(...):
    """Connexion à Epic Events CRM."""
    pass

# Dans user_commands.py
import typer
app = typer.Typer()

@app.command("create-user")
def create_user(...):
    """Créer un nouvel utilisateur."""
    pass

# De même pour client_commands.py, contract_commands.py, event_commands.py
```

### Agrégation dans __init__.py

Le fichier `src/cli/commands/__init__.py` **agrège toutes les sous-applications** :

```python
import typer

from .auth_commands import app as auth_app
from .client_commands import app as client_app
from .contract_commands import app as contract_app
from .event_commands import app as event_app
from .user_commands import app as user_app

# Application principale qui agrège tous les modules
app = typer.Typer()

# Monter les sous-applications
app.add_typer(auth_app)
app.add_typer(client_app)
app.add_typer(contract_app)
app.add_typer(event_app)
app.add_typer(user_app)
```

## Qu'est-ce qu'une Sous-Application Typer ?

### Création des Sous-Applications

Dans la nouvelle architecture, **chaque module crée sa propre sous-application indépendante** :

- **auth_commands.py** : `app = typer.Typer()` pour les commandes d'authentification
- **user_commands.py** : `app = typer.Typer()` pour gérer les utilisateurs
- **client_commands.py** : `app = typer.Typer()` pour gérer les clients
- **contract_commands.py** : `app = typer.Typer()` pour gérer les contrats
- **event_commands.py** : `app = typer.Typer()` pour gérer les événements

**Avantage de cette approche :**
- **Séparation des responsabilités** : Chaque domaine métier dans son propre fichier
- **Maintenabilité** : Plus facile de trouver et modifier une commande spécifique
- **Modularité** : Chaque module peut être testé indépendamment

### Intégration dans l'Application Principale

Le fichier `__init__.py` **monte ces sous-applications** avec `app.add_typer()` :

```python
app.add_typer(auth_app)      # Toutes les commandes d'auth
app.add_typer(client_app)    # Toutes les commandes client
app.add_typer(contract_app)  # Toutes les commandes contract
app.add_typer(event_app)     # Toutes les commandes event
app.add_typer(user_app)      # Toutes les commandes user
```

**Fonctionnement de `add_typer()` :**

- **Sans `name`** : Les commandes conservent leur nom d'origine (ex: `login`, `create-client`)
- L'utilisateur exécute directement : `epicevents login`, `epicevents create-client`
- Pas de préfixe ajouté

## Avantages de cette Architecture

### 1. **Modularité**
Chaque domaine métier a son propre module, ce qui permet de :
- **Séparer les responsabilités** : Un fichier = Un domaine
- **Faciliter la maintenance** : Les modifications sont isolées dans un fichier
- **Réduire la complexité** : Fichiers de ~300-700 lignes au lieu de 2000+ lignes
- **Organiser logiquement** : Structure claire par domaine métier

### 2. **Commandes CLI**
L'utilisateur exécute des commandes directement (sans préfixe) :
```bash
# Authentification
epicevents login
epicevents logout
epicevents whoami

# Utilisateurs
epicevents create-user
epicevents update-user
epicevents delete-user

# Clients
epicevents create-client
epicevents update-client

# Contrats
epicevents create-contract
epicevents sign-contract
epicevents filter-unsigned-contracts

# Événements
epicevents create-event
epicevents update-event
epicevents assign-support
epicevents filter-my-events
```

### 3. **Testabilité**
- Chaque module peut être testé indépendamment
- Tests plus rapides (on ne charge que le module nécessaire)
- Mocking simplifié par module

### 4. **Documentation Automatique**
Typer génère automatiquement une aide structurée :
```bash
epicevents --help
# Affiche toutes les commandes disponibles (19 commandes)

epicevents create-client --help
# Affiche l'aide spécifique pour cette commande
```

## Le Paramètre `rich_markup_mode="rich"`

Ce paramètre active le **markup Rich** dans les docstrings et l'aide de la CLI.

### Qu'est-ce que Rich Markup ?

Rich Markup permet d'utiliser des balises pour formater le texte :

```python
@app.command()
def example():
    """
    Cette commande fait quelque chose de [bold]très important[/bold].

    Elle peut afficher du texte en [green]vert[/green] ou en [red]rouge[/red].
    """
    pass
```

### Balises Disponibles

- `[bold]texte[/bold]` : Texte en gras
- `[italic]texte[/italic]` : Texte en italique
- `[green]texte[/green]` : Texte en vert
- `[red]texte[/red]` : Texte en rouge
- `[blue]texte[/blue]` : Texte en bleu
- Et beaucoup d'autres styles...

### Modes Disponibles

1. `rich_markup_mode="rich"` : Active le markup Rich (ce qui est utilisé ici)
2. `rich_markup_mode="markdown"` : Active le formatage Markdown
3. `rich_markup_mode=None` : Désactive tout formatage

## Exemple Complet d'Utilisation

### Structure des fichiers

```
src/cli/commands/
├── __init__.py              # Agrégation
├── auth_commands.py         # Module auth
└── client_commands.py       # Module client
```

### client_commands.py

```python
import typer
from src.containers import Container

# Créer l'application pour ce module
app = typer.Typer()

@app.command("create-client")
def create_client(
    first_name: str = typer.Option(..., prompt="Prénom"),
    last_name: str = typer.Option(..., prompt="Nom"),
):
    """
    Créer un nouveau client dans le système CRM.
    """
    container = Container()
    client_service = container.client_service()

    client = client_service.create_client(
        first_name=first_name,
        last_name=last_name
    )
    print(f"Client {client.id} créé avec succès")

@app.command("update-client")
def update_client(
    client_id: int = typer.Option(..., prompt="ID du client"),
):
    """
    Mettre à jour un client existant.
    """
    # Implementation...
    pass
```

### __init__.py (Agrégation)

```python
import typer

from .auth_commands import app as auth_app
from .client_commands import app as client_app

# Application principale
app = typer.Typer()

# Monter les sous-applications
app.add_typer(auth_app)
app.add_typer(client_app)
```

### Commandes générées

```bash
epicevents create-client
epicevents update-client
epicevents login
epicevents logout
```

## Liens vers la Documentation Officielle

### Documentation Typer

- **Add Typer (Sous-Applications)** : https://typer.tiangolo.com/tutorial/subcommands/add-typer/
- **SubCommand Name and Help** : https://typer.tiangolo.com/tutorial/subcommands/name-and-help/
- **Nested SubCommands** : https://typer.tiangolo.com/tutorial/subcommands/nested-subcommands/
- **Command Help** : https://typer.tiangolo.com/tutorial/commands/help/
- **One File Per Command** : https://typer.tiangolo.com/tutorial/one-file-per-command/
- **Documentation Principale** : https://typer.tiangolo.com/

### Documentation Rich

- **Console Markup** : https://rich.readthedocs.io/en/stable/markup.html
- **Rich Markup Reference** : https://rich.readthedocs.io/en/stable/reference/markup.html
- **Styles** : https://rich.readthedocs.io/en/latest/style.html

## Résumé

L'architecture Epic Events CRM utilise une **structure modulaire** pour organiser l'application CLI :

1. **5 modules de commandes indépendants** (auth, user, client, contract, event)
2. **Chaque module crée sa propre instance Typer** avec ses commandes
3. **Le fichier `__init__.py` agrège tous les modules** via `app.add_typer()`
4. **Séparation des responsabilités** : Un fichier = Un domaine métier
5. **Maintenabilité optimale** : Fichiers de ~300-700 lignes au lieu de 2000+ lignes

Cette approche est une **bonne pratique** recommandée par la documentation Typer pour les applications CLI complexes et respecte les principes SOLID (Single Responsibility Principle).
