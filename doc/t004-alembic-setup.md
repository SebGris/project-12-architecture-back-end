# T004 : Initialiser Alembic pour les migrations de base de données

## Description
Configurer Alembic pour gérer les migrations de la base de données SQLite et créer la migration initiale.

## Prérequis
- ✅ T002 : Poetry installé avec toutes les dépendances (notamment Alembic)
- ✅ Environnement virtuel créé avec `poetry install`

## Étapes d'installation

### 1. Initialiser Alembic

```bash
poetry run alembic init migrations
```

Cette commande crée :
- Dossier `migrations/` avec les fichiers de configuration
- Fichier `alembic.ini` à la racine du projet
- Script `migrations/env.py` pour configurer l'environnement de migration

### 2. Configurer la connexion à la base de données

Éditer le fichier `alembic.ini` :

```ini
# Localiser la ligne sqlalchemy.url et la modifier (driver://user:pass@localhost/dbname) :
sqlalchemy.url = sqlite:///epic_events.db
```

**Alternative dynamique (recommandé)** : Charger l'URL depuis `.env`

Modifier `migrations/env.py` pour charger l'URL depuis les variables d'environnement :

```python
# Au début du fichier migrations/env.py
from dotenv import load_dotenv
import os

load_dotenv()

# Dans la section config
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL', 'sqlite:///epic_events.db'))
```

### 3. Configurer les métadonnées des modèles

Éditer `migrations/env.py` pour pointer vers vos modèles SQLAlchemy :

```python
# Ajouter les imports des modèles
from src.models.user import User
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event
from src.models import Base  # Assurez-vous que Base est importé

# Localiser la ligne target_metadata et la modifier :
target_metadata = Base.metadata
```

### 4. Tester la configuration

```bash
# Vérifier que la configuration fonctionne (sans créer de migration)
poetry run alembic current

# Devrait afficher : (head), <current database revision>
```

### 5. Créer une migration initiale (après avoir créé les modèles)

**Note** : Cette étape sera effectuée plus tard, après T021-T024 (création des modèles).

```bash
# Générer automatiquement la migration basée sur les modèles
poetry run alembic revision --autogenerate -m "Create initial tables"

# Examiner le fichier de migration généré dans migrations/versions/

# Appliquer la migration
poetry run alembic upgrade head
```

## Fichiers modifiés

- `alembic.ini` : Configuration de l'URL de la base de données
- `migrations/env.py` : Import des modèles et configuration de target_metadata

## Structure créée

```
project-12-architecture-back-end/
├── alembic.ini                          # Configuration Alembic
├── migrations/
│   ├── env.py                          # Configuration de l'environnement
│   ├── script.py.mako                  # Template pour les migrations
│   ├── README                          # Documentation Alembic
│   └── versions/                       # Dossier pour les fichiers de migration
│       └── (vide pour l'instant)
└── epic_events.db                      # Créé après alembic upgrade head
```

## Commandes Alembic utiles

```bash
# Voir l'état actuel de la base de données
poetry run alembic current

# Créer une nouvelle migration automatiquement
poetry run alembic revision --autogenerate -m "Description de la migration"

# Appliquer toutes les migrations en attente
poetry run alembic upgrade head

# Revenir à la migration précédente
poetry run alembic downgrade -1

# Voir l'historique des migrations
poetry run alembic history

# Revenir à une migration spécifique
poetry run alembic downgrade <revision_id>
```

## Critères de complétion

- ✅ Commande `alembic init migrations` exécutée avec succès
- ✅ Fichier `alembic.ini` configuré avec l'URL SQLite
- ✅ Fichier `migrations/env.py` configuré pour importer les modèles (sera testé après T021-T024)
- ✅ Commande `poetry run alembic current` s'exécute sans erreur
- ⏳ Attente de T025 pour créer et appliquer la première migration

## Dépendances

- **Dépend de** : T002 (Installation des dépendances Poetry)
- **Requis pour** : T025 (Création de la migration initiale avec tous les modèles)

## Troubleshooting

### Erreur : "Can't locate revision identified by '...'"
- La base de données n'est pas synchronisée avec les migrations
- Solution : `poetry run alembic stamp head` pour marquer la version actuelle

### Erreur : "target database is not up to date"
- Des migrations n'ont pas été appliquées
- Solution : `poetry run alembic upgrade head`

### Erreur : "No module named 'src.models'"
- Le chemin Python n'inclut pas le projet
- Solution : Ajouter `sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))` dans `migrations/env.py`
