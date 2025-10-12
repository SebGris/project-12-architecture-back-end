# Historique des changements - Epic Events CRM

Ce fichier résume les modifications apportées au projet pour faciliter le suivi par le mentor OpenClassrooms.

---

## 2025-10-12 : Création des utilisateurs de test (Seed Database)

**Base de données** : Création d'un script de seed (`seed_database.py`) pour peupler la base de données avec 5 utilisateurs de test répartis dans les 3 départements (1 GESTION, 2 COMMERCIAL, 2 SUPPORT). Implémentation du hashing sécurisé des mots de passe avec bcrypt. Script de test (`test_password_hash.py`) pour vérifier la sécurité du hashing.

📄 Documentation détaillée : [T009-seed-database-users.md](T009-seed-database-users.md)

**Utilisateurs créés** :
- `admin` (GESTION) - Alice Dubois - admin@epicevents.com
- `commercial1` (COMMERCIAL) - John Smith - john.smith@epicevents.com
- `commercial2` (COMMERCIAL) - Marie Martin - marie.martin@epicevents.com
- `support1` (SUPPORT) - Pierre Durand - pierre.durand@epicevents.com
- `support2` (SUPPORT) - Sophie Bernard - sophie.bernard@epicevents.com

**Sécurité** :
- Mots de passe hashés avec bcrypt (algorithme résistant aux attaques par force brute)
- Salage automatique intégré (chaque hash est unique)
- Tests de vérification réussis pour tous les utilisateurs

---

## 2025-10-12 : Guide des outils d'administration SQLite

**Documentation** : Création d'un guide complet comparant les outils d'administration pour SQLite (DB Browser, VS Code extensions, SQLite CLI, DBeaver, viewers en ligne). Recommandation de DB Browser for SQLite comme outil principal pour l'exploration visuelle de la base de données.

📄 Documentation détaillée : [guide-outils-administration-sqlite.md](guide-outils-administration-sqlite.md)

---

## 2025-10-12 : Création des tables de la base de données

**Base de données** : Application de la migration initiale Alembic pour créer les 4 tables du système CRM (users, clients, contracts, events) dans la base de données SQLite `epic_events.db`. Toutes les relations (clés étrangères), contraintes (unique, not null) et index sont correctement créés.

📄 Documentation détaillée : [T008-creation-tables-migration-initiale.md](T008-creation-tables-migration-initiale.md)

**Tables créées** :
- `users` : 10 colonnes, 2 contraintes UNIQUE (username, email)
- `clients` : 9 colonnes, 1 FK vers users (sales_contact_id)
- `contracts` : 7 colonnes, 2 FK vers clients et users
- `events` : 11 colonnes, 2 FK vers contracts et users

**Script de vérification** : Création de `check_db.py` pour inspecter la structure de la base via SQLAlchemy.

---

## 2025-10-11 : Ajout du champ email dans User

**Modèle User** : Ajout du champ `email` (VARCHAR(255), unique) au modèle User pour permettre la communication professionnelle, la récupération de mot de passe et les intégrations externes. Conforme aux standards des CRM d'entreprise.

📄 Documentation détaillée : Email est un champ essentiel dans tout CRM professionnel

---

## 2025-10-11 : Séparation des noms dans les modèles User et Client

**Modèles User et Client** : Remplacement du champ `full_name` par deux champs séparés `first_name` et `last_name` pour améliorer la recherche, le tri et la validation, conformément aux standards de l'industrie.

📄 Documentation détaillée : [changements-separation-noms-ajout-telephone.md](changements-separation-noms-ajout-telephone.md)

---

## 2025-10-11 : Ajout du champ téléphone dans User

**Modèle User** : Ajout du champ `phone` (VARCHAR(20), format E.164) au modèle User pour assurer la cohérence avec le modèle Client et permettre le contact des collaborateurs.

📄 Documentation détaillée : [changements-separation-noms-ajout-telephone.md](changements-separation-noms-ajout-telephone.md)

---

## 2025-10-11 : Correction des timestamps

**Modèles** : Correction des champs `created_at` et `updated_at` pour utiliser `DateTime(timezone=True)` et `server_default=func.now()` au lieu de `default=datetime.utcnow`, assurant ainsi la cohérence des timestamps et évitant les problèmes de comparaison de fuseaux horaires.

📄 Documentation détaillée : [changements-timestamps-models.md](changements-timestamps-models.md)

---

## 2025-10-05 : Configuration Alembic

**Infrastructure** : Configuration d'Alembic pour la gestion des migrations de base de données, incluant le fichier `alembic.ini`, le script d'environnement et le modèle de script de migration.

📄 Documentation détaillée : [T004-alembic-setup.md](T004-alembic-setup.md)

---

## 2025-10-05 : Configuration Pytest

**Tests** : Configuration de Pytest avec fichier `pytest.ini`, markers personnalisés (contract, integration, unit) et fixtures partagées dans `conftest.py` suivant le pattern TDD.

📄 Documentation détaillée : [T005-pytest-configuration.md](T005-pytest-configuration.md)

---

## 2025-10-05 : Tests de contrat pour authentification

**Tests** : Création de 8 tests de contrat pour les commandes `login` et `logout`, validant les schémas JSON de réponse, les codes de sortie et la gestion du fichier token JWT.

📄 Documentation détaillée : [T007-contract-test-auth-commands.md](T007-contract-test-auth-commands.md)

---

## 2025-10-04 : Suppression des codes HTTP

**Architecture** : Décision de ne pas utiliser de codes HTTP (200, 401, 404) dans une application CLI, au profit de codes de sortie shell standards (0 = succès, 1 = erreur générale, 2 = erreur d'utilisation).

📄 Documentation détaillée : [refactoring-http-codes-removal.md](refactoring-http-codes-removal.md)

---

## 2025-10-04 : Pattern TDD avec imports optionnels

**Tests** : Mise en place du pattern `try/except ImportError` dans les tests pour supporter le développement TDD, permettant aux tests d'être SKIPPED tant que les modules ne sont pas implémentés.

📄 Documentation détaillée : [TDD-pattern-optional-imports.md](TDD-pattern-optional-imports.md)

---

## 2025-10-03 : Initialisation du projet avec Poetry

**Infrastructure** : Configuration initiale du projet Python avec Poetry, incluant les dépendances (SQLAlchemy, Click, Pydantic, pytest, Alembic), configuration de Python 3.13 et structure du projet.

📄 Documentation détaillée : [T002-poetry-init-guide.md](T002-poetry-init-guide.md)

---

## Légende

- 📄 = Documentation détaillée disponible
- ✅ = Modification complétée
- ⏳ = En cours
- 🔄 = Refactoring
- 🆕 = Nouvelle fonctionnalité
- 🐛 = Correction de bug
- 📚 = Documentation
- ⚙️ = Configuration
