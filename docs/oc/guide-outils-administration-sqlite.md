# Guide des outils d'administration pour SQLite

## Vue d'ensemble

Ce guide compare les différents outils disponibles pour administrer votre base de données SQLite `epic_events_crm.db`.

---

## 🏆 Outil recommandé : DB Browser for SQLite

**DB Browser for SQLite** est l'outil le plus complet et facile à utiliser pour travailler avec SQLite.

### Pourquoi DB Browser ?

- ✅ **Interface graphique intuitive** - Comme Excel pour les bases de données
- ✅ **Visualisation des relations** - Voir les clés étrangères entre tables graphiquement
- ✅ **Éditeur SQL intégré** - Tester vos requêtes SQL avec autocomplétion
- ✅ **Modification facile des données** - Ajouter/modifier/supprimer des enregistrements visuellement
- ✅ **Export/Import** - CSV, JSON, SQL, HTML
- ✅ **Diagramme ERD** - Vue graphique des relations entre tables
- ✅ **Gratuit et open-source** - Licence GPL
- ✅ **Portable** - Pas besoin d'installation système (version portable disponible)
- ✅ **Multiplateforme** - Windows, macOS, Linux
- ✅ **Léger et rapide** - Environ 50 MB installé

---

## Installation de DB Browser for SQLite

### Étape 1 : Télécharger

1. Allez sur [https://sqlitebrowser.org/dl/](https://sqlitebrowser.org/dl/)
2. Section **"Windows"**
3. Deux options disponibles :

**Option A : Standard Installer (Recommandé)**
- Fichier : `DB.Browser.for.SQLite-X.X.X-win64.msi`
- Taille : ~40 MB
- Installation classique dans `C:\Program Files\`
- Raccourci dans le menu Démarrer

**Option B : Portable**
- Fichier : `DB.Browser.for.SQLite-X.X.X-win64.zip`
- Taille : ~50 MB
- Aucune installation requise
- Décompresser et lancer `DB Browser for SQLite.exe`

### Étape 2 : Installer

**Pour l'installeur (MSI) :**
1. Double-cliquez sur le fichier `.msi`
2. Suivez l'assistant d'installation
3. Acceptez les paramètres par défaut
4. Cliquez sur "Install"
5. Lancez depuis le menu Démarrer : "DB Browser for SQLite"

**Pour la version portable :**
1. Décompressez le ZIP dans un dossier (ex: `C:\Tools\SQLiteBrowser\`)
2. Lancez `DB Browser for SQLite.exe`
3. (Optionnel) Créez un raccourci sur le bureau

---

## Utilisation avec votre projet Epic Events

### 1. Ouvrir votre base de données

1. Lancez **DB Browser for SQLite**
2. Menu : **File → Open Database** (ou Ctrl+O)
3. Naviguez vers votre projet :
   ```
   D:\Users\sebas\Documents\VS Code\OpenClassrooms\project-12-architecture-back-end\
   ```
4. Sélectionnez `epic_events_crm.db`
5. La base s'ouvre avec 4 onglets principaux

---

### 2. Onglet "Database Structure" - Vue d'ensemble

**À quoi ça sert** : Voir toute la structure de votre base de données (tables, colonnes, index, triggers).

#### Ce que vous devriez voir :

```
📁 Tables (5)
  📊 alembic_version
  📊 users
  📊 clients
  📊 contracts
  📊 events
```

#### Fonctionnalités :

**Déplier une table** :
- Cliquez sur le triangle ▶ devant le nom de la table
- Vous verrez toutes les colonnes avec leurs propriétés

**Exemple pour la table `users` :**
```
▼ 📊 users
    🔑 id (INTEGER) PRIMARY KEY
    ✨ username (VARCHAR(50)) UNIQUE NOT NULL
    ✨ email (VARCHAR(255)) UNIQUE NOT NULL
       password_hash (VARCHAR(255)) NOT NULL
       first_name (VARCHAR(50)) NOT NULL
       last_name (VARCHAR(50)) NOT NULL
       phone (VARCHAR(20)) NOT NULL
       department (VARCHAR(10)) NOT NULL
       created_at (DATETIME) NOT NULL
       updated_at (DATETIME) NOT NULL
```

**Icônes importantes** :
- 🔑 = Clé primaire (PRIMARY KEY)
- 🔗 = Clé étrangère (FOREIGN KEY)
- ✨ = Contrainte UNIQUE
- ⚠️ = Index

**Actions possibles** :
- Clic droit sur une table → **Modify Table** : Voir/modifier la structure
- Clic droit sur une table → **Delete Table** : Supprimer la table
- Clic droit sur une table → **Copy CREATE Statement** : Copier le SQL de création

---

### 3. Onglet "Browse Data" - Voir et modifier les données

**À quoi ça sert** : Voir le contenu des tables, comme un tableur Excel.

#### Utilisation :

1. **Sélectionner une table** : Menu déroulant en haut → Choisir "users", "clients", etc.
2. **Voir les données** : Toutes les lignes s'affichent dans la grille
3. **Ajouter une ligne** : Bouton "New Record" ou clic sur la dernière ligne vide
4. **Modifier une cellule** : Double-clic sur la cellule → Taper la nouvelle valeur
5. **Supprimer une ligne** : Sélectionner la ligne → Bouton "Delete Record" (ou touche Suppr)
6. **Sauvegarder** : Bouton "Write Changes" (ou Ctrl+S)

#### Filtres et tri :

- **Filtrer** : En-tête de colonne → Clic droit → "Filter"
  - Exemple : Filtrer `department = 'COMMERCIAL'`
- **Trier** : Clic sur l'en-tête de colonne
  - 1er clic : Tri croissant (A→Z)
  - 2e clic : Tri décroissant (Z→A)

#### Export des données :

- **Export en CSV** : Bouton "Export to CSV"
- **Export en SQL** : File → Export → Table(s) as SQL file
- **Copier dans le presse-papiers** : Sélectionner des lignes → Ctrl+C

---

### 4. Onglet "Execute SQL" - Requêtes SQL personnalisées

**À quoi ça sert** : Exécuter des requêtes SQL pour interroger ou modifier la base.

#### Exemples de requêtes utiles :

**Vérifier que les tables existent :**
```sql
SELECT name, type FROM sqlite_master
WHERE type='table'
ORDER BY name;
```

**Voir la structure d'une table :**
```sql
PRAGMA table_info(users);
```

**Lister toutes les clés étrangères :**
```sql
-- Clés étrangères de la table clients
PRAGMA foreign_key_list(clients);

-- Clés étrangères de la table contracts
PRAGMA foreign_key_list(contracts);

-- Clés étrangères de la table events
PRAGMA foreign_key_list(events);
```

**Compter les enregistrements :**
```sql
SELECT
    'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'clients', COUNT(*) FROM clients
UNION ALL
SELECT 'contracts', COUNT(*) FROM contracts
UNION ALL
SELECT 'events', COUNT(*) FROM events;
```

**Voir les utilisateurs par département :**
```sql
SELECT department, COUNT(*) as total
FROM users
GROUP BY department;
```

**Trouver les clients sans contrat :**
```sql
SELECT c.id, c.first_name, c.last_name, c.company_name
FROM clients c
LEFT JOIN contracts ct ON ct.client_id = c.id
WHERE ct.id IS NULL;
```

**Voir les événements avec leurs informations complètes :**
```sql
SELECT
    e.id,
    e.name as event_name,
    e.event_start,
    e.location,
    c.first_name || ' ' || c.last_name as client_name,
    u.username as support_contact
FROM events e
JOIN contracts co ON e.contract_id = co.id
JOIN clients c ON co.client_id = c.id
LEFT JOIN users u ON e.support_contact_id = u.id;
```

#### Fonctionnalités de l'éditeur :

- **Autocomplétion** : Tapez `SEL` puis Ctrl+Space → Affiche `SELECT`
- **Exécuter** : Bouton ▶ (ou F5 ou Ctrl+Return)
- **Exécuter la sélection** : Sélectionner du texte → F5 (exécute seulement la sélection)
- **Historique** : Onglet "SQL Log" → Voir toutes les requêtes exécutées
- **Sauvegarder la requête** : File → Save SQL file

---

### 5. Onglet "DB Schema" - Diagramme visuel (ERD)

**À quoi ça sert** : Voir un diagramme graphique des tables et leurs relations.

#### Ce que vous verrez :

```
┌─────────────┐
│   users     │
│  id (PK)    │
│  username   │
│  department │
│  ...        │
└──────┬──────┘
       │
       ├──────────────────┐
       │                  │
       ↓                  ↓
┌─────────────┐    ┌─────────────┐
│  clients    │    │ contracts   │
│  id (PK)    │    │  id (PK)    │
│  sales_id ─→│    │  client_id ─┼→ clients
└──────┬──────┘    │  sales_id ──┼→ users
       │           └──────┬───────┘
       │                  │
       │                  ↓
       │           ┌─────────────┐
       │           │   events    │
       │           │  id (PK)    │
       └───────────┼→ contract_id│
                   │  support_id ┼→ users
                   └─────────────┘
```

**Relations que vous devriez voir :**
- `users` ──→ `clients` (via `sales_contact_id`)
- `users` ──→ `contracts` (via `sales_contact_id`)
- `users` ──→ `events` (via `support_contact_id`)
- `clients` ──→ `contracts` (via `client_id`)
- `contracts` ──→ `events` (via `contract_id`)

**Fonctionnalités** :
- **Zoom** : Molette de la souris ou boutons +/-
- **Déplacer** : Cliquer-glisser sur le fond
- **Réorganiser** : Cliquer-glisser une table
- **Export** : Bouton "Export" → PNG ou SVG

---

## Fonctionnalités avancées

### Import de données depuis CSV

Utile pour charger des données de test en masse.

1. File → Import → Table from CSV file
2. Sélectionnez votre fichier CSV
3. Choisissez la table de destination
4. Mappez les colonnes
5. Importez

**Exemple de CSV pour users :**
```csv
username,email,password_hash,first_name,last_name,phone,department
admin,admin@epicevents.com,$2b$12$hash...,Admin,Gestion,+33123456789,GESTION
john,john@epicevents.com,$2b$12$hash...,John,Doe,+33198765432,COMMERCIAL
```

### Export de la base complète

Pour backup ou migration :

1. File → Export → Database to SQL file
2. Choisissez l'emplacement
3. Options :
   - ✅ Export schema (CREATE TABLE)
   - ✅ Export data (INSERT INTO)
   - ⬜ Use transactions (recommandé)
4. Exporter

### Comparer deux bases de données

Pour comparer dev vs production :

1. Ouvrez deux instances de DB Browser
2. File → Open Database dans chaque fenêtre
3. Comparez visuellement les structures
4. Ou utilisez l'onglet "Execute SQL" pour générer des checksums

```sql
-- Checksum de la table users
SELECT COUNT(*), SUM(id), MAX(created_at) FROM users;
```

### Vacuum et optimisation

Pour compresser et optimiser la base :

1. Onglet "Execute SQL"
2. Exécutez : `VACUUM;`
3. La base est défragmentée et compressée

---

## Alternatives aux outils d'administration

### Option 2 : Extension VS Code "SQLite Viewer"

**Avantages** :
- ✅ Directement intégré dans VS Code
- ✅ Pas besoin de changer d'application
- ✅ Clic droit sur `.db` → "Open Database"

**Inconvénients** :
- ⚠️ Moins de fonctionnalités que DB Browser
- ⚠️ Pas de diagramme ERD
- ⚠️ Interface moins ergonomique

**Installation** :
1. Dans VS Code : Ctrl+Shift+X
2. Rechercher : **"SQLite Viewer"** (par `alexcvzz`) ou **"SQLite"** (par `qwtel`)
3. Installer
4. Clic droit sur `epic_events_crm.db` → "Open Database"

---

### Option 3 : SQLite CLI (Ligne de commande)

**Avantages** :
- ✅ Léger (< 2 MB)
- ✅ Scriptable et automatisable
- ✅ Accès rapide via terminal

**Inconvénients** :
- ⚠️ Pas d'interface graphique
- ⚠️ Courbe d'apprentissage

**Installation** :
1. Téléchargez depuis [https://sqlite.org/download.html](https://sqlite.org/download.html)
2. Section **"Precompiled Binaries for Windows"**
3. Téléchargez `sqlite-tools-win-x64-*.zip`
4. Extrayez `sqlite3.exe` dans un dossier du PATH (ex: `C:\sqlite\`)
5. Ajoutez au PATH Windows (Variables d'environnement)

**Commandes utiles** :
```bash
# Ouvrir la base
sqlite3 epic_events_crm.db

# Commandes internes (commencent par un point)
.help                            # Aide
.tables                          # Lister les tables
.schema users                    # Structure de la table users
.mode column                     # Affichage en colonnes
.headers on                      # Afficher les en-têtes
.output result.txt               # Rediriger vers un fichier
.quit                            # Quitter

# Requêtes SQL normales
SELECT * FROM users;
SELECT COUNT(*) FROM clients;
```

---

### Option 4 : DBeaver Community Edition

**Pour qui** : Projets avec plusieurs bases de données (SQLite + PostgreSQL + MySQL).

**Avantages** :
- ✅ IDE complet pour bases de données
- ✅ Support multi-DB
- ✅ Diagrammes ER automatiques avancés
- ✅ Autocomplétion SQL intelligente
- ✅ Gestion des migrations

**Inconvénients** :
- ⚠️ Lourd (~200 MB, basé sur Eclipse)
- ⚠️ Overkill pour uniquement SQLite

**Téléchargement** : [https://dbeaver.io/download/](https://dbeaver.io/download/)

---

### Option 5 : SQLite Viewer Online (Navigateur)

**Pour qui** : Usage ponctuel sans installation.

**Sites recommandés** :
- [https://sqliteviewer.app/](https://sqliteviewer.app/)
- [https://inloop.github.io/sqlite-viewer/](https://inloop.github.io/sqlite-viewer/)

**Avantages** :
- ✅ Aucune installation
- ✅ Fonctionne dans le navigateur
- ✅ Données restent locales (pas d'upload serveur)

**Inconvénients** :
- ⚠️ Fonctionnalités limitées
- ⚠️ Moins pratique pour usage régulier

---

## Comparatif des outils

| Outil | Interface | Installation | Fonctionnalités | Poids | Idéal pour |
|-------|-----------|--------------|-----------------|-------|------------|
| **DB Browser** ⭐ | GUI | Simple | ⭐⭐⭐⭐⭐ | 50 MB | **Tout usage** |
| VS Code Extension | GUI | Extension | ⭐⭐⭐ | Léger | Dev dans VS Code |
| SQLite CLI | CLI | Manuelle | ⭐⭐⭐ | 2 MB | Scripts, automation |
| DBeaver | GUI | Complexe | ⭐⭐⭐⭐⭐ | 200 MB | Multi-DB, pro |
| Online Viewer | Web | Aucune | ⭐⭐ | 0 | Dépannage rapide |

---

## Recommandation pour Epic Events CRM

Pour votre projet, je recommande **cette combinaison** :

### 1️⃣ DB Browser for SQLite (Usage principal)
- Exploration de la structure
- Vérification des données
- Tests de requêtes SQL
- Ajout de données de test
- Debug des relations

### 2️⃣ Script Python `check_db.py` (Automatisation)
- Vérifications automatiques après migrations
- Tests d'intégration
- CI/CD pipelines
- Documentation automatique

### 3️⃣ Extension VS Code (Optionnel, pour confort)
- Accès rapide sans quitter VS Code
- Vérifications rapides pendant le dev

---

## Checklist de vérification avec DB Browser

Après avoir appliqué la migration initiale, vérifiez dans DB Browser :

**Onglet "Database Structure" :**
- ✅ 5 tables existent : alembic_version, users, clients, contracts, events
- ✅ Table `users` : 10 colonnes, 2 contraintes UNIQUE (username, email)
- ✅ Table `clients` : 9 colonnes, 1 FK vers users
- ✅ Table `contracts` : 7 colonnes, 2 FK (vers clients et users)
- ✅ Table `events` : 11 colonnes, 2 FK (vers contracts et users)

**Onglet "Browse Data" :**
- ✅ Table `alembic_version` contient 1 ligne avec votre révision
- ✅ Les autres tables sont vides (pour l'instant)

**Onglet "Execute SQL" :**
- ✅ `PRAGMA foreign_key_list(clients);` retourne 1 ligne
- ✅ `PRAGMA foreign_key_list(contracts);` retourne 2 lignes
- ✅ `PRAGMA foreign_key_list(events);` retourne 2 lignes

**Onglet "DB Schema" :**
- ✅ Le diagramme montre les 4 tables principales
- ✅ Les flèches montrent les relations FK correctes

---

## Support et ressources

### Documentation officielle
- **DB Browser** : [https://sqlitebrowser.org/](https://sqlitebrowser.org/)
- **SQLite** : [https://sqlite.org/docs.html](https://sqlite.org/docs.html)

### Tutoriels
- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [DB Browser Video Tutorial (YouTube)](https://www.youtube.com/results?search_query=db+browser+for+sqlite+tutorial)

### Communauté
- DB Browser GitHub : [https://github.com/sqlitebrowser/sqlitebrowser](https://github.com/sqlitebrowser/sqlitebrowser)
- Issues / Questions : [https://github.com/sqlitebrowser/sqlitebrowser/issues](https://github.com/sqlitebrowser/sqlitebrowser/issues)

---

## Date de création
2025-10-12
