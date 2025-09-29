# 🎯 Epic Events CRM - Système de Gestion Client

## 📋 Description

Système CRM sécurisé développé en ligne de commande pour Epic Events, permettant de gérer les clients, contrats et événements de l'entreprise.

**Projet OpenClassrooms N°12** - Formation Développeur d'Application Python

> **Note** : Ce projet utilise PostgreSQL 18 (dernière version sortie le 25 septembre 2025), offrant des performances optimisées et les dernières fonctionnalités de sécurité.

## 🛠️ Technologies

- **Python 3.10+**
- **PostgreSQL 18**
- **SQLAlchemy** (ORM)
- **Alembic** (Migrations)
- **Click** (CLI)
- **Sentry** (Monitoring des erreurs)
- **bcrypt** (Hachage des mots de passe)

## 📦 Installation

### Prérequis

- Python 3.10 ou supérieur
- PostgreSQL 18 installé et configuré
- Git
- **PATH configuré** pour PostgreSQL et Python (voir section [Aide-mémoire](#-aide-mémoire))

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone https://github.com/votre-username/epic-events-crm.git
cd epic-events-crm
```

2. **Créer et activer l'environnement virtuel**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer la base de données**
```bash
# Se connecter à PostgreSQL
psql -U postgres
```
Mot de passe : Proj12_!2025
```bash
# Créer la base de données pour le CRM
CREATE DATABASE epic_events_crm;
# Créer un utilisateur dédié pour l'application
CREATE USER crm_user WITH PASSWORD 'MotDePasseFort123!';
# Donner tous les privilèges sur la base epic_events_crm
GRANT ALL PRIVILEGES ON DATABASE epic_events_crm TO crm_user;
# Se connecter à la base epic_events_crm
\c epic_events_crm
# Quitter psql
\q
```

5. **Configurer les variables d'environnement**

Créer un fichier `.env` à la racine :
```env
DATABASE_URL=postgresql://crm_user:votre_mot_de_passe@localhost:5432/epic_events_crm
SENTRY_DSN=votre_dsn_sentry
SECRET_KEY=votre_cle_secrete
```

6. **Initialiser la base de données**
```bash
# Initialiser Alembic
alembic init alembic

# Appliquer les migrations
alembic upgrade head
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
├── .env                    # Variables d'environnement
├── .gitignore             
├── README.md              
├── requirements.txt       
├── alembic.ini            # Configuration Alembic
├── alembic/               # Migrations
│   └── versions/
├── src/
│   ├── __init__.py
│   ├── main.py            # Point d'entrée
│   ├── config.py          # Configuration
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py  # Connexion DB
│   │   └── models.py      # Modèles SQLAlchemy
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── commands.py    # Commandes Click
│   │   └── validators.py  # Validation des entrées
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── security.py    # Hachage, JWT
│   │   └── permissions.py # Gestion des droits
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── client_service.py
│   │   ├── contract_service.py
│   │   └── event_service.py
│   └── utils/
│       ├── __init__.py
│       └── logger.py      # Configuration Sentry
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

### Configuration du PATH (Windows 10)

Pour utiliser PostgreSQL et Python depuis n'importe quel terminal, vous devez ajouter leurs répertoires au PATH système :

#### Ajouter PostgreSQL au PATH
```bash
# Le chemin à ajouter (adapter selon votre version) :
C:\Program Files\PostgreSQL\18\bin
```

**Étapes :**
1. Appuyer sur **Win + R**, taper `sysdm.cpl` et Entrée
2. Cliquer sur l'onglet **Paramètres système avancés**
3. Cliquer sur **Variables d'environnement**
4. Dans **Variables système**, trouver **Path** et cliquer **Modifier**
5. Cliquer **Nouveau** et ajouter : `C:\Program Files\PostgreSQL\18\bin`
6. Cliquer **OK** sur toutes les fenêtres
7. **IMPORTANT** : Fermer et rouvrir le terminal pour appliquer les changements

#### Vérifier que le PATH est configuré
```bash
# PowerShell ou CMD
echo %PATH%

# Tester PostgreSQL
psql --version

# Tester Python
python --version
```

#### Ajouter Python au PATH (si nécessaire)
```bash
# Chemins Python typiques à ajouter :
C:\Users\VotreNom\AppData\Local\Programs\Python\Python310
C:\Users\VotreNom\AppData\Local\Programs\Python\Python310\Scripts
```

#### Variables d'environnement utiles
```bash
# Voir toutes les variables d'environnement
set

# Voir une variable spécifique
echo %POSTGRESQL_HOME%

# Créer une variable d'environnement (temporaire)
set PGUSER=postgres

# PowerShell - Voir le PATH formaté
$env:Path -split ';'
```

### Vérification du port PostgreSQL (5432)

#### Windows 10
```bash
# PowerShell (Admin)
netstat -an | findstr :5432

# Voir quel processus utilise le port
netstat -aon | findstr :5432

# Détails sur le processus (remplacer PID par le numéro obtenu)
tasklist | findstr PID
```

### Commandes PostgreSQL utiles

```bash
# Vérifier la version installée
psql --version
postgres --version

# Connexion
psql -U postgres -d epic_events_crm

# Dans psql:
SELECT version();      # Version détaillée de PostgreSQL
\l                 # Lister les bases de données
\c database_name   # Se connecter à une base
\dt                # Lister les tables
\d table_name      # Décrire une table
\q                 # Quitter

# Backup de la base
pg_dump -U postgres epic_events_crm > backup.sql

# Restaurer une base
psql -U postgres epic_events_crm < backup.sql
```

### Gestion du service PostgreSQL

#### Windows
```bash
# Démarrer PostgreSQL
net start postgresql-x64-18

# Arrêter PostgreSQL
net stop postgresql-x64-18

# Vérifier le statut (PowerShell)
Get-Service -Name "postgresql*"
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

#### Port 5432 déjà utilisé
```bash
# 1. Identifier le processus
netstat -aon | findstr :5432

# 2. Si c'est une ancienne instance PostgreSQL, la tuer (Windows)
taskkill /PID numero_pid /F

# 3. Ou changer le port dans postgresql.conf
```

#### Erreur de connexion PostgreSQL
```bash
# Vérifier que le service est démarré
# Vérifier pg_hba.conf pour les méthodes d'authentification
# Vérifier postgresql.conf pour listen_addresses
```

#### Erreur "FATAL: password authentication failed"
```sql
-- Réinitialiser le mot de passe
ALTER USER postgres PASSWORD 'nouveau_mot_de_passe';
```

## 🐛 Debugging avec Sentry

Le projet utilise Sentry pour le monitoring des erreurs en production. Les erreurs sont automatiquement capturées et envoyées au dashboard Sentry.

Configuration dans `.env`:
```
SENTRY_DSN=https://...@sentry.io/...
```

## 📚 Documentation

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [SqlAlchemy, l'ORM Python - Partie 1](https://blog.stephane-robert.info/docs/developper/programmation/python/sqlachemy-1/)
- [Click Documentation](https://click.palletsprojects.com/)
- [OWASP Security Guidelines](https://owasp.org/)

## 📄 Licence

Projet éducatif - OpenClassrooms

## 👤 Auteur

Sébastien - [GitHub](https://github.com/votre-username)

---

*Projet développé dans le cadre de la formation Développeur d'Application Python - OpenClassrooms*