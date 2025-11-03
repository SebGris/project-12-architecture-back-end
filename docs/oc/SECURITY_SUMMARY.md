# Résumé des Mesures de Sécurité - Epic Events CRM

## ✅ Conformité avec le Cahier des Charges

### Exigences de sécurité implémentées

1. **✅ Protection contre les injections SQL**
   - Utilisation d'**SQLAlchemy ORM** avec requêtes paramétrées
   - Aucune concaténation de chaînes SQL
   - Validation des inputs utilisateur

2. **✅ Principe du moindre privilège**
   - Authentification JWT obligatoire
   - Contrôle d'accès basé sur les rôles (RBAC)
   - Filtrage contextuel des données
   - **Suppression des méthodes `get_all()` dangereuses**

3. **✅ Authentification persistante**
   - Jetons JWT avec expiration (24h)
   - Stockage sécurisé local (~/.epicevents/token)
   - Algorithme HMAC-SHA256
   - Secret key via variable d'environnement

4. **⏳ Journalisation avec Sentry** (à implémenter)
   - Configuration Sentry à ajouter
   - Logging des exceptions et erreurs

## 🔒 Mesures de Sécurité Implémentées

### 1. Authentification JWT

**Fichier** : `src/services/auth_service.py`

- **Algorithme** : HS256 (HMAC with SHA-256)
- **Expiration** : 24 heures
- **Secret Key** : Variable d'environnement `EPICEVENTS_SECRET_KEY`
- **Stockage** : ~/.epicevents/token (permissions 600)

**Commandes CLI** :
- `epicevents login` - Connexion
- `epicevents logout` - Déconnexion
- `epicevents whoami` - Utilisateur actuel

### 2. Autorisation par Rôle

**Fichier** : `src/cli/permissions.py`

**Décorateurs disponibles** :
```python
@require_auth  # Nécessite authentification
@require_department(Department.GESTION, ...)  # Nécessite département spécifique
```

**Permissions par département** :

| Action | GESTION | COMMERCIAL | SUPPORT |
|--------|---------|------------|---------|
| Créer/modifier utilisateurs | ✅ | ❌ | ❌ |
| Créer clients | ✅ | ✅ (auto-assigné) | ❌ |
| Modifier clients | ✅ | ✅ (leurs clients) | ❌ |
| Créer/modifier contrats | ✅ | ✅ (leurs clients) | ❌ |
| Créer événements | ✅ | ✅ (leurs clients) | ❌ |
| Assigner support | ✅ | ❌ | ❌ |
| Modifier événements | ✅ | ❌ | ✅ (leurs événements) |

### 3. Protection contre get_all()

**Problème** : `get_all()` expose toutes les données sans filtrage
- Risque de DoS (Denial of Service)
- Violation du principe du moindre privilège
- Performance dégradée

**Solution** : Supprimé de tous les repositories et services

**Fichiers modifiés** :
- ❌ `src/repositories/*_repository.py` - Interfaces
- ❌ `src/repositories/sqlalchemy_*_repository.py` - Implémentations
- ❌ `src/services/*_service.py` - Services
- ❌ `src/cli/commands.py` - Commandes list-*

**Remplacé par** : Filtres contextuels
- `filter_unsigned_contracts()` - Contrats non signés
- `filter_unpaid_contracts()` - Contrats non soldés
- `filter_unassigned_events()` - Événements sans support
- `filter_my_events(user_id)` - Événements d'un utilisateur

### 4. Validation des Inputs

**Fichier** : `src/cli/validators.py`

**Validations implémentées** :
- ✅ Email (regex)
- ✅ Téléphone (regex + longueur minimale)
- ✅ Username (regex + longueur 4-50)
- ✅ Password (longueur minimale 8)
- ✅ Noms/prénoms (regex, lettres/espaces/tirets/apostrophes)
- ✅ Montants (positifs, format décimal)
- ✅ IDs (positifs)
- ✅ Dates (format YYYY-MM-DD HH:MM)

### 5. Hachage des Mots de Passe

**Fichier** : `src/models/user.py`

- **Algorithme** : bcrypt
- **Salt** : Généré automatiquement par bcrypt
- **Méthodes** :
  - `set_password(password)` - Hash le mot de passe
  - `verify_password(password)` - Vérifie le mot de passe

### 6. Gestion des Erreurs

**Protection des informations sensibles** :
- Messages d'erreur génériques pour l'authentification
- Pas de divulgation d'informations système
- Gestion appropriée des exceptions SQLAlchemy

**Exemple** :
```python
# ❌ Mauvais
print_error("L'utilisateur 'admin' n'existe pas")

# ✅ Bon
print_error("Nom d'utilisateur ou mot de passe incorrect")
```

## 🚫 Vulnérabilités Évitées

### 1. Injection SQL
**Protection** : ORM SQLAlchemy avec requêtes paramétrées
```python
# ✅ Sécurisé
user = session.query(User).filter_by(username=username).first()

# ❌ Dangereux (non utilisé)
query = f"SELECT * FROM users WHERE username = '{username}'"
```

### 2. Exposition de Données
**Protection** : Principe du moindre privilège
- Pas de `get_all()` sans filtrage
- Filtres basés sur les permissions
- Vérification des droits d'accès

### 3. Token Tampering
**Protection** : Signature HMAC des JWT
- Token signé avec secret key
- Validation de la signature à chaque requête
- Expiration automatique après 24h

### 4. Brute Force
**Protection** : Hachage bcrypt lent
- Bcrypt est intentionnellement lent
- Résistant aux attaques par force brute
- Salt unique par utilisateur

### 5. Stockage Insécurisé
**Protection** : Permissions fichier restreintes
- Token stocké dans ~/.epicevents/token
- Permissions 600 (lecture/écriture propriétaire uniquement)
- Pas de token dans le code source

## 📋 Checklist de Sécurité

### Implémenté ✅

- [x] Authentification JWT
- [x] Autorisation basée sur les rôles
- [x] Hachage bcrypt des mots de passe
- [x] Protection contre injection SQL (ORM)
- [x] Validation des inputs
- [x] Principe du moindre privilège
- [x] Suppression des get_all() dangereux
- [x] Stockage sécurisé des tokens
- [x] Expiration des tokens
- [x] Messages d'erreur sécurisés
- [x] Journalisation Sentry
- [x] Logging des tentatives de connexion
- [x] Capture des exceptions
- [x] Contexte utilisateur et breadcrumbs

### À implémenter ⏳

- [ ] Rate limiting (optionnel)
- [ ] Rotation des tokens (optionnel)
- [ ] Blacklist de tokens (optionnel)
- [ ] 2FA (hors scope)

## 🔐 Configuration de Production

### Variables d'Environnement Requises

```bash
# Secret key pour JWT (OBLIGATOIRE en production)
export EPICEVENTS_SECRET_KEY="votre_cle_secrete_de_256_bits_minimum"

# Sentry DSN pour logging (optionnel)
export SENTRY_DSN="https://xxx@sentry.io/xxx"

# Configuration base de données
export DATABASE_URL="postgresql://user:pass@host:port/db"
```

### Recommandations

1. **Secret Key**
   - ✅ Minimum 256 bits (32 octets)
   - ✅ Générer avec `secrets.token_hex(32)`
   - ✅ Ne JAMAIS committer dans Git
   - ✅ Différente entre environnements

2. **Base de données**
   - ✅ Utiliser PostgreSQL en production (pas SQLite)
   - ✅ Connexion chiffrée (SSL/TLS)
   - ✅ Credentials via variables d'environnement
   - ✅ Backups réguliers

3. **Logs**
   - ✅ Configurer Sentry pour production
   - ✅ Logger les tentatives d'authentification échouées
   - ✅ Monitorer les erreurs d'intégrité
   - ❌ Ne pas logger les mots de passe ou tokens

4. **Permissions Fichiers**
   - ✅ Token file : 600 (rw-------)
   - ✅ Config files : 600
   - ✅ Database file : 600 (si SQLite)

## 📊 Matrice des Permissions

### Clients

| Action | GESTION | COMMERCIAL | SUPPORT |
|--------|---------|------------|---------|
| Créer | ✅ | ✅ | ❌ |
| Lire tous | ✅ | ❌ | ❌ |
| Lire assignés | ✅ | ✅ | ❌ |
| Modifier tous | ✅ | ❌ | ❌ |
| Modifier assignés | ✅ | ✅ | ❌ |

### Contrats

| Action | GESTION | COMMERCIAL | SUPPORT |
|--------|---------|------------|---------|
| Créer | ✅ | ✅* | ❌ |
| Lire tous | ✅ | ❌ | ❌ |
| Lire filtrés | ✅ | ✅ | ❌ |
| Modifier tous | ✅ | ❌ | ❌ |
| Modifier clients assignés | ✅ | ✅ | ❌ |

*Contrats de leurs clients uniquement

### Événements

| Action | GESTION | COMMERCIAL | SUPPORT |
|--------|---------|------------|---------|
| Créer | ✅ | ✅* | ❌ |
| Lire tous | ✅ | ❌ | ❌ |
| Lire assignés | ✅ | ❌ | ✅ |
| Modifier tous | ✅ | ❌ | ❌ |
| Modifier assignés | ✅ | ❌ | ✅ |
| Assigner support | ✅ | ❌ | ❌ |

*Événements de leurs clients avec contrat signé

### Utilisateurs

| Action | GESTION | COMMERCIAL | SUPPORT |
|--------|---------|------------|---------|
| Créer | ✅ | ❌ | ❌ |
| Lire tous | ✅ | ❌ | ❌ |
| Modifier | ✅ | ❌ | ❌ |
| Supprimer | ✅ | ❌ | ❌ |

## 🎯 Conformité Finale

| Exigence | Status |
|----------|--------|
| Python 3.9+ | ✅ |
| Application CLI | ✅ |
| Protection injection SQL | ✅ |
| Principe moindre privilège | ✅ |
| Authentification persistante | ✅ |
| Journalisation Sentry | ⏳ |

**Légende** :
- ✅ Implémenté et testé
- ⏳ À implémenter
- ❌ Non applicable
