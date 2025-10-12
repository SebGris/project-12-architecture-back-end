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
- Git

### Étapes d'installation

1. **Créer et activer l'environnement virtuel**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

2. **Installer SQLAlchemy**

SQLAlchemy est l'ORM (Object-Relational Mapping) qui permet d'interagir avec SQLite depuis Python :

```bash
# Installer SQLAlchemy
pip install sqlalchemy

# SQLite est inclus dans Python - aucun driver supplémentaire nécessaire
```

> **Note** : SQLite est inclus par défaut dans Python, aucune installation supplémentaire n'est nécessaire !

3. **Configurer les variables d'environnement**

Créer un fichier `.env` à la racine :
```env
DATABASE_URL=sqlite:///epic_events_crm.db
SENTRY_DSN=votre_dsn_sentry
SECRET_KEY=votre_cle_secrete
```

4. **Initialiser la base de données**
```bash
# Initialiser Alembic
alembic init alembic

# Appliquer les migrations
alembic upgrade head
```

### Exemple de connexion SQLAlchemy

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Créer le moteur de connexion SQLite
engine = create_engine('sqlite:///epic_events_crm.db')

# Créer une session
Session = sessionmaker(bind=engine)
session = Session()

# Tester la connexion
try:
    connection = engine.connect()
    print("✅ Connexion à SQLite réussie!")
    connection.close()
except Exception as e:
    print(f"❌ Erreur de connexion: {e}")
```

## 🚀 Utilisation

### Commandes principales

```bash
# Lancer l'application
python src/main.py

# Créer un utilisateur
python src/main.py user create

# Connexion
python src/main.py login

# Créer un client
python src/main.py client create

# Lister les contrats
python src/main.py contract list

# Créer un événement
python src/main.py event create
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
epic_events_crm/
├── epic_events_crm.db     # Base de données SQLite
├── .env                   # Variables d'environnement
├── .gitignore             
├── README.md              
├── requirements.txt       
├── alembic.ini           # Configuration Alembic
├── alembic/              # Migrations
│   └── versions/
├── src/
│   ├── __init__.py
│   ├── main.py           # Point d'entrée
│   ├── config.py         # Configuration
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py # Connexion DB
│   │   └── models.py     # Modèles SQLAlchemy
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── commands.py   # Commandes Click
│   │   └── validators.py # Validation des entrées
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── security.py   # Hachage, JWT
│   │   └── permissions.py # Gestion des droits
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── client_service.py
│   │   ├── contract_service.py
│   │   └── event_service.py
│   └── utils/
│       ├── __init__.py
│       └── logger.py     # Configuration Sentry
└── tests/
    ├── __init__.py
    ├── test_auth.py
    ├── test_models.py
    └── test_services.py
```

## 📝 Modèles de données

### User (Collaborateur)
- id, email, password, role, created_at

### Client
- id, name, email, phone, company, created_by, commercial_id, created_at, updated_at

### Contract
- id, client_id, commercial_id, total_amount, amount_due, status, created_at

### Event
- id, contract_id, support_id, name, location, start_date, end_date, attendees, notes

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=src tests/

# Test spécifique
pytest tests/test_auth.py
```

## 💻 Aide-mémoire

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

### Python - Environnement virtuel

```bash
# Windows
python -m venv venv
venv\Scripts\activate
deactivate
# Geler les dépendances
pip freeze > requirements.txt
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
- [Click Documentation](https://click.palletsprojects.com/)
- [OWASP Security Guidelines](https://owasp.org/)

## 📄 Licence

Projet éducatif - OpenClassrooms

## 👤 Auteur

Sébastien - [GitHub](https://github.com/votre-username)

---

*Projet développé dans le cadre de la formation Développeur d'Application Python - OpenClassrooms*