# 🎯 Epic Events CRM - Système de Gestion Client

## 📋 Description

Système CRM sécurisé développé en ligne de commande pour Epic Events, permettant de gérer les clients, contrats et événements de l'entreprise.

**Projet OpenClassrooms N°12** - Formation Développeur d'Application Python

> **Note** : Ce projet utilise SQLite 3, une base de données légère et intégrée, parfaite pour le développement et les projets de taille moyenne.

## 🛠️ Technologies

- **Python 3.13**
- **SQLite 3** (Base de données intégrée)
- **SQLAlchemy** (ORM) - Interface Python pour SQLite
- **Alembic** (Migrations)
- **Typer** (CLI)
- **Sentry** (Monitoring des erreurs)
- **bcrypt** (Hachage des mots de passe)

## 📦 Installation

### Prérequis

- Python 3.13 ou supérieur
- Poetry (gestionnaire de dépendances)
- Git

### Étapes d'installation

1. **Cloner le dépôt**
```bash
git clone https://github.com/SebGris/project-12-architecture-back-end
cd project-12-architecture-back-end
```

2. **Installer les dépendances avec Poetry**
```bash
# Vérifier si Python est installé
python --version

# Installer Poetry
python -m pip install poetry

# Vérifier l'installation de Poetry
python -m poetry --version

# Installer les dépendances du projet
python -m poetry install

```

> **Note** : Sur Windows, utilisez toujours `python -m poetry` au lieu de `poetry` car le dossier Scripts n'est généralement pas dans le PATH.

> **Note** : SQLite est inclus par défaut dans Python, aucune installation supplémentaire n'est nécessaire !

3. **Configurer les variables d'environnement**

Créer un fichier `.env` à la racine (vous pouvez copier `.env.example`) :
```env
DATABASE_URL=sqlite:///data/epic_events_crm.db
EPICEVENTS_SECRET_KEY=your_secret_key_here_256_bits_minimum
SENTRY_DSN=votre_dsn_sentry
ENVIRONMENT=development
```

4. **Initialiser la base de données**
```bash
# Appliquer les migrations
python -m poetry run alembic upgrade head
```

## 🚀 Utilisation

### Installation de la commande

Après avoir installé les dépendances avec Poetry, la commande `epicevents` est automatiquement disponible dans votre environnement virtuel.

**Option 1 : Activer l'environnement virtuel manuellement**
```bash
# Activer l'environnement virtuel
.venv\Scripts\activate

# La commande epicevents est maintenant disponible
epicevents --help
```

**Option 2 : Utiliser poetry run (recommandé)**
```bash
# Exécuter directement sans activer l'environnement
python -m poetry run epicevents --help
```

### Liste des commandes

Si vous ne voulez pas utiliser Poetry shell, vous pouvez exécuter les commandes directement :

```bash
# Avec Poetry run
python -m poetry run epicevents login
python -m poetry run epicevents whoami
python -m poetry run epicevents logout

python -m poetry run epicevents create-user
python -m poetry run epicevents create-client

# Afficher l'aide
python -m poetry run epicevents --help
python -m poetry run epicevents create-user --help

# Ou en tant que module Python
python -m poetry run python -m src.cli.main
```

## 🔐 Sécurité

- Authentification par JWT
- Mots de passe hachés avec bcrypt
- Principe du moindre privilège (3 rôles : Commercial, Support, Gestion)
- Validation des entrées
- Protection contre les injections SQL via SQLAlchemy
- Journalisation avec Sentry

## 📊 Architecture

```
project-12-architecture-back-end/
├── data/
│   └── epic_events_crm.db    # Base de données SQLite
├── .env                       # Variables d'environnement
├── .env.example              # Template des variables d'env
├── .gitignore
├── README.md
├── pyproject.toml            # Configuration Poetry + entry points CLI
├── poetry.lock
├── alembic.ini               # Configuration Alembic
├── schema_de_la_base_de_donnees.png  # Schéma de la base de données
├── migrations/               # Migrations Alembic
│   └── versions/
├── src/
│   ├── __init__.py
│   ├── database.py           # Configuration DB et sessions
│   ├── containers.py         # Dependency Injection (dependency-injector)
│   ├── sentry_config.py      # Configuration Sentry
│   ├── models/               # Modèles SQLAlchemy ORM
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── client.py
│   │   ├── contract.py
│   │   └── event.py
│   ├── repositories/         # Repository pattern pour accès données
│   │   ├── client_repository.py
│   │   ├── sqlalchemy_client_repository.py
│   │   ├── user_repository.py
│   │   ├── sqlalchemy_user_repository.py
│   │   ├── contract_repository.py
│   │   ├── sqlalchemy_contract_repository.py
│   │   ├── event_repository.py
│   │   └── sqlalchemy_event_repository.py
│   ├── services/             # Logique métier
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── client_service.py
│   │   ├── contract_service.py
│   │   ├── event_service.py
│   │   ├── auth_service.py
│   │   └── password_hashing_service.py
│   └── cli/                  # Interface en ligne de commande
│       ├── __init__.py
│       ├── main.py           # Point d'entrée CLI (epicevents)
│       ├── permissions.py    # Décorateurs de permissions
│       ├── validators.py     # Validateurs de saisie
│       ├── constants.py      # Constantes CLI
│       ├── console.py        # Utilities d'affichage
│       └── commands/         # Commandes Typer modulaires
│           ├── __init__.py           # Agrégation des sous-applications
│           ├── auth_commands.py      # Commandes authentification
│           ├── user_commands.py      # Commandes utilisateurs
│           ├── client_commands.py    # Commandes clients
│           ├── contract_commands.py  # Commandes contrats
│           └── event_commands.py     # Commandes événements
├── tests/
│   ├── conftest.py           # Fixtures pytest partagées
│   ├── unit/                 # Tests unitaires
│   ├── integration/          # Tests d'intégration
│   └── fixtures/             # Fixtures de test
└── docs/                     # Documentation du projet
    └── IDENTIFIANTS-TEST.md
```

## 📝 Modèles de données

### User (Collaborateur)
- id, username, email, password_hash, first_name, last_name, phone, department, created_at, updated_at

### Client
- id, first_name, last_name, email, phone, company_name, sales_contact_id, created_at, updated_at

### Contract
- id, client_id, total_amount, remaining_amount, is_signed, created_at

### Event
- id, name, contract_id, support_contact_id, event_start, event_end, location, attendees, notes, created_at, updated_at

Pour plus de détails, voir le [schéma de la base de données](schema_de_la_base_de_donnees.png)

## 🔒 Permissions granulaires

Le système implémente des **permissions granulaires par département** pour sécuriser l'accès aux données :

### Matrice de permissions

| Commande | GESTION | COMMERCIAL | SUPPORT |
|----------|---------|------------|---------|
| **Clients** | | | |
| `create-client` | ✅ Tous | ✅ Auto-assigné | ❌ |
| `update-client` | ✅ Tous | ✅ **Ses clients** | ❌ |
| **Contrats** | | | |
| `create-contract` | ✅ Tous | ✅ Ses clients | ❌ |
| `update-contract` | ✅ Tous | ✅ **Ses contrats** | ❌ |
| **Événements** | | | |
| `create-event` | ✅ | ✅ | ❌ |
| `update-event-attendees` | ✅ Tous | ❌ | ✅ **Ses events** |
| `assign-support` | ✅ | ❌ | ❌ |
| `filter-my-events` | ❌ | ❌ | ✅ Auto-détection |

### Principe de moindre privilège

- **GESTION** : Accès complet à toutes les ressources
- **COMMERCIAL** : Peut gérer uniquement ses clients et leurs contrats
- **SUPPORT** : Peut gérer uniquement ses événements assignés

### Exemples

```bash
# En tant que COMMERCIAL
epicevents update-client  # ✅ OK si c'est son client
# ID du client: 1 (assigné à cet utilisateur)

epicevents update-client  # ❌ REFUSÉ si c'est le client d'un autre
# ID du client: 2 (assigné à un autre commercial)
# [ERREUR] Vous ne pouvez modifier que vos propres clients
```

Pour plus de détails, voir :
- [PERMISSIONS_GRANULAIRES.md](PERMISSIONS_GRANULAIRES.md) - Documentation complète
- [docs/AMELIORATIONS_PERMISSIONS.md](docs/AMELIORATIONS_PERMISSIONS.md) - Récapitulatif technique

## 💻 Aide-mémoire

### Gestion avec Poetry

```bash
# Installer les dépendances
python -m poetry install

# Activer l'environnement virtuel
python -m poetry shell

# Ajouter une dépendance
python -m poetry add nom-du-package

# Ajouter une dépendance de développement
python -m poetry add --group dev nom-du-package

# Mettre à jour les dépendances
python -m poetry update

# Exécuter une commande sans activer le shell
python -m poetry run epicevents create-user

# Quitter l'environnement virtuel
exit
```

### Gestion de la base SQLite

```bash
# Ouvrir la base avec l'outil sqlite3 (inclus avec Python)
sqlite3 epic_events_crm.db

# Commandes SQLite utiles:
.tables                    # Lister les tables
.schema table_name         # Voir la structure d'une table
.dump                      # Exporter toute la base
.backup backup.db          # Sauvegarder la base
.quit                      # Quitter
```

### Commandes SQLite courantes

```sql
-- Dans sqlite3:
.help                      -- Aide
.databases                 -- Lister les bases attachées
.headers on               -- Afficher les en-têtes de colonnes
.mode column              -- Mode d'affichage en colonnes
SELECT name FROM sqlite_master WHERE type='table';  -- Lister les tables
```

### Lancer les tests avec Poetry

```bash
pytest

# Tests avec couverture
pytest --cov=src tests/
```

### Résolution de problèmes courants

#### Base de données verrouillée
```bash
# Si la base SQLite est verrouillée, s'assurer qu'aucune connexion n'est ouverte
# Redémarrer l'application si nécessaire
```

#### Fichier de base de données non trouvé
```bash
# Vérifier que le chemin dans DATABASE_URL est correct
# SQLite créera automatiquement le fichier s'il n'existe pas
```

#### Problèmes de permissions
```bash
# S'assurer que le répertoire est accessible en écriture
# Vérifier les permissions du fichier .db
```

### Avantages de SQLite pour ce projet

- **Installation simple** : Aucune configuration serveur nécessaire
- **Portable** : Un seul fichier contient toute la base
- **Rapide** : Excellent pour le développement et les petites applications
- **Fiable** : Base de données mature et stable
- **Sauvegarde facile** : Copier le fichier .db suffit

## 🐛 Debugging avec Sentry

Le projet utilise Sentry pour le monitoring des erreurs en production. Les erreurs sont automatiquement capturées et envoyées au dashboard Sentry.

Configuration dans `.env`:
```
SENTRY_DSN=https://...@sentry.io/...
```

## 📚 Documentation

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [SQLAlchemy SQLite Tutorial](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html)
- [Python SQLite3 Module](https://docs.python.org/3/library/sqlite3.html)
- [Typer Documentation](https://typer.tiangolo.com/)
- [OWASP Security Guidelines](https://owasp.org/)

## 📄 Licence

Projet éducatif - OpenClassrooms

## 👤 Auteur

Sébastien - [GitHub](https://github.com/votre-username)

---

*Projet développé dans le cadre de la formation Développeur d'Application Python - OpenClassrooms*