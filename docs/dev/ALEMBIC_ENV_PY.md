# Fichier env.py d'Alembic

## Vue d'ensemble

Le fichier [env.py](../migrations/env.py) est un fichier de configuration d'**Alembic**, l'outil de gestion des migrations de base de données utilisé avec SQLAlchemy.

Il configure et orchestre l'exécution des migrations de votre base de données en définissant **comment** et **dans quel contexte** les migrations doivent être appliquées.

---

## Structure du fichier

### 1. Imports des modèles (lignes 6-10)

```python
from src.database import Base
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event
from src.models.user import User
```

**Pourquoi ces imports sont-ils nécessaires ?**

Alembic doit connaître tous vos modèles pour pouvoir :
- Détecter automatiquement les changements de schéma (autogenerate)
- Créer les migrations appropriées
- Comparer l'état actuel de la base de données avec vos modèles SQLAlchemy

**Important :** Chaque fois que vous créez un nouveau modèle, vous devez l'importer ici pour qu'Alembic puisse le détecter.

---

### 2. Configuration de base (lignes 12-19)

```python
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)
```

- `config` : Objet de configuration Alembic qui lit `alembic.ini`
- `fileConfig()` : Configure les loggers Python à partir du fichier de configuration

---

### 3. Métadonnées cibles (ligne 28)

```python
target_metadata = Base.metadata
```

**Rôle crucial :** C'est la référence qu'Alembic utilise pour :
- Comparer avec la structure actuelle de la base de données
- Détecter les différences (colonnes ajoutées, modifiées, supprimées)
- Générer automatiquement les migrations

---

### 4. Mode Offline - `run_migrations_offline()` (lignes 36-57)

```python
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()
```

**Caractéristiques :**
- Génère du SQL **sans connexion active** à la base de données
- N'exécute pas les migrations, génère uniquement le code SQL
- Utile pour générer des scripts SQL à exécuter manuellement ou à réviser

**Cas d'usage :**
```bash
# Générer le SQL des migrations sans les appliquer
alembic upgrade head --sql > migration.sql
```

---

### 5. Mode Online - `run_migrations_online()` (lignes 60-79)

```python
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
```

**Caractéristiques :**
- Se connecte à la base de données et **applique les migrations directement**
- Mode par défaut utilisé par Alembic
- Crée une connexion SQLAlchemy active
- Utilise `NullPool` pour éviter les problèmes de pool de connexions

**Cas d'usage :**
```bash
# Appliquer toutes les migrations en attente
alembic upgrade head

# Revenir à une version spécifique
alembic downgrade -1
```

---

### 6. Détection automatique du mode (lignes 82-85)

```python
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

Alembic détermine automatiquement le mode à utiliser en fonction :
- Du flag `--sql` dans la ligne de commande → mode offline
- De l'absence de flag → mode online (défaut)

---

## Workflows pratiques

### Créer une nouvelle migration automatique

```bash
alembic revision --autogenerate -m "add email_verified column to users"
```

**Ce qui se passe :**
1. Alembic charge `target_metadata` (vos modèles)
2. Se connecte à la base de données
3. Compare les deux structures
4. Génère automatiquement un fichier de migration avec les différences

### Appliquer les migrations

```bash
# Appliquer toutes les migrations
alembic upgrade head

# Appliquer la prochaine migration seulement
alembic upgrade +1

# Voir l'historique
alembic history

# Voir l'état actuel
alembic current
```

### Générer du SQL pour révision

```bash
# Générer le SQL sans l'exécuter
alembic upgrade head --sql > migration.sql

# Réviser le fichier avant de l'exécuter manuellement
cat migration.sql
```

### Revenir en arrière (rollback)

```bash
# Revenir d'une version
alembic downgrade -1

# Revenir à une révision spécifique
alembic downgrade abc123

# Tout annuler (ATTENTION!)
alembic downgrade base
```

---

## Bonnes pratiques

### 1. Toujours importer tous les modèles

Quand vous créez un nouveau modèle, ajoutez-le immédiatement dans `env.py` :

```python
from src.models.user import User
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event
from src.models.notification import Notification  # ← Nouveau modèle
```

### 2. Vérifier les migrations générées

Les migrations auto-générées ne sont pas toujours parfaites :
- Vérifiez toujours le fichier de migration créé
- Testez sur une base de données de développement
- Ajoutez des données de test pour valider

### 3. Ordre des migrations

Alembic suit un ordre linéaire basé sur :
- Le champ `revision` (ID unique de la migration)
- Le champ `down_revision` (migration parente)

```python
# Exemple de fichier de migration
revision = 'abc123'
down_revision = 'xyz789'  # Migration précédente
```

### 4. Migrations personnalisées

Parfois, vous devez créer des migrations manuellement :

```bash
# Créer une migration vide
alembic revision -m "populate initial data"
```

Puis éditez le fichier généré :

```python
def upgrade() -> None:
    # Ajouter des données initiales
    op.execute("""
        INSERT INTO users (username, email, department)
        VALUES ('admin', 'admin@epicevents.com', 'GESTION')
    """)

def downgrade() -> None:
    # Supprimer les données
    op.execute("DELETE FROM users WHERE username = 'admin'")
```

---

## Dépannage

### Erreur : "Target database is not up to date"

```bash
# Vérifier l'état actuel
alembic current

# Voir l'historique
alembic history

# Appliquer les migrations manquantes
alembic upgrade head
```

### Erreur : "Can't locate revision identified by 'abc123'"

La table `alembic_version` est désynchronisée :

```bash
# Marquer manuellement comme appliquée (ATTENTION!)
alembic stamp head
```

### Les changements ne sont pas détectés

Vérifiez que :
1. Le modèle est importé dans `env.py`
2. Le modèle hérite bien de `Base`
3. La base de données est à jour : `alembic current`

---

## Résumé

Le fichier `env.py` est le **pont entre vos modèles SQLAlchemy et Alembic**.

Sans lui, Alembic ne saurait pas :
- ✅ Quels modèles surveiller
- ✅ Comment se connecter à la base de données
- ✅ Comment exécuter les migrations
- ✅ Comment générer les changements automatiquement

C'est un fichier **de configuration**, que vous modifiez rarement (principalement pour ajouter de nouveaux imports de modèles).

---

## Ressources complémentaires

- [Documentation officielle Alembic](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Migrations](https://docs.sqlalchemy.org/en/20/core/metadata.html)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
