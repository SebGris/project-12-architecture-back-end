# Système d'Authentification et d'Autorisation

## Vue d'ensemble

Le système d'authentification Epic Events CRM utilise **JSON Web Tokens (JWT)** pour gérer l'authentification et l'autorisation des utilisateurs de manière sécurisée et persistante.

## Architecture

### Composants principaux

1. **AuthService** (`src/services/auth_service.py`)
   - Gestion de l'authentification
   - Génération et validation des tokens JWT
   - Stockage sécurisé des tokens

2. **Permissions** (`src/cli/permissions.py`)
   - Décorateurs pour vérifier les permissions
   - Contrôle d'accès basé sur les rôles (RBAC)

3. **Commandes CLI**
   - `login` : Authentification
   - `logout` : Déconnexion
   - `whoami` : Afficher l'utilisateur actuel

## Sécurité

### JWT Configuration

- **Algorithme** : HS256 (HMAC with SHA-256)
- **Expiration** : 24 heures
- **Secret Key** :
  - Variable d'environnement `EPICEVENTS_SECRET_KEY` (production)
  - Génération automatique sécurisée (développement)

### Stockage des tokens

Les tokens JWT sont stockés localement dans :
```
~/.epicevents/token
```

Avec permissions restreintes (600) sur les systèmes Unix.

### Protection contre les vulnérabilités

✅ **Protégé contre** :
- Injection SQL : Utilisation d'ORM SQLAlchemy avec requêtes paramétrées
- Token replay : Expiration des tokens après 24h
- Token tampering : Signature HMAC vérifiée à chaque requête
- Stockage insécurisé : Tokens stockés avec permissions restrictives

❌ **Non implémenté** (hors scope) :
- Rotation des tokens
- Refresh tokens
- Blacklist de tokens
- Multi-device management

## Utilisation

### 1. Connexion

```bash
poetry run epicevents login
```

Saisir :
- Nom d'utilisateur
- Mot de passe (masqué)

Le token JWT est généré et stocké automatiquement.

### 2. Vérification de l'authentification

```bash
poetry run epicevents whoami
```

Affiche les informations de l'utilisateur connecté.

### 3. Déconnexion

```bash
poetry run epicevents logout
```

Supprime le token JWT stocké.

## Permissions par département

### GESTION
- ✅ Créer, modifier, supprimer des utilisateurs
- ✅ Créer et modifier tous les contrats
- ✅ Modifier et assigner les événements
- ✅ Filtrer tous les événements et contrats
- ✅ Accès complet (lecture/écriture) à toutes les données

### COMMERCIAL
- ✅ Créer des clients (auto-assignés)
- ✅ Modifier leurs propres clients
- ✅ Modifier les contrats de leurs clients
- ✅ Créer des événements pour leurs clients avec contrats signés
- ✅ Filtrer les contrats (non signés, non payés)
- ❌ Accès aux clients/contrats des autres commerciaux

### SUPPORT
- ✅ Modifier leurs événements assignés
- ✅ Filtrer leurs événements
- ❌ Créer/modifier des clients
- ❌ Créer/modifier des contrats
- ❌ Accès aux événements des autres supports

## Implémentation dans les commandes

### Exemple : Commande protégée

```python
from src.cli.permissions import require_department
from src.models.user import Department

@app.command()
@inject
@require_department(Department.GESTION)
def create_user(
    auth_service=Provide[Container.auth_service],
    user_service=Provide[Container.user_service],
    current_user: User = None,  # Injecté par le décorateur
    # ... autres paramètres
):
    # Seuls les utilisateurs GESTION peuvent exécuter cette commande
    pass
```

### Décorateurs disponibles

#### `@require_auth`
Vérifie que l'utilisateur est authentifié.

```python
@require_auth
def my_command(current_user: User = None):
    # current_user est automatiquement injecté
    pass
```

#### `@require_department(dept1, dept2, ...)`
Vérifie que l'utilisateur appartient à un des départements autorisés.

```python
@require_department(Department.COMMERCIAL, Department.GESTION)
def my_command(current_user: User = None):
    # Accessible uniquement pour COMMERCIAL et GESTION
    pass
```

### Fonctions utilitaires

#### `check_client_ownership(user, client)`
Vérifie si un utilisateur a le droit d'accéder à un client.

```python
if not check_client_ownership(current_user, client):
    print_error("Vous n'avez pas accès à ce client")
    raise typer.Exit(code=1)
```

#### `check_event_ownership(user, event)`
Vérifie si un utilisateur a le droit d'accéder à un événement.

```python
if not check_event_ownership(current_user, event):
    print_error("Vous n'avez pas accès à cet événement")
    raise typer.Exit(code=1)
```

## Flux d'authentification

```
1. Utilisateur exécute : epicevents login
   ↓
2. Saisie username + password
   ↓
3. AuthService.authenticate()
   - Récupère l'utilisateur depuis la DB
   - Vérifie le mot de passe avec bcrypt
   ↓
4. Si succès : AuthService.generate_token()
   - Crée payload JWT avec user_id, username, department
   - Signe avec secret key (HS256)
   - Expiration : 24h
   ↓
5. AuthService.save_token()
   - Stocke dans ~/.epicevents/token
   - Permissions 600 (lecture/écriture propriétaire uniquement)
   ↓
6. Commandes suivantes
   - Décorator @require_auth ou @require_department
   - AuthService.load_token()
   - AuthService.validate_token()
   - AuthService.get_current_user()
   ↓
7. Si token valide : commande exécutée
   Si token invalide/expiré : erreur + invite à se reconnecter
```

## Variables d'environnement

### EPICEVENTS_SECRET_KEY (Production)

**Important** : En production, définissez cette variable pour sécuriser les tokens JWT.

```bash
# Linux/Mac
export EPICEVENTS_SECRET_KEY="votre_secret_key_super_securisee_de_256_bits_minimum"

# Windows PowerShell
$env:EPICEVENTS_SECRET_KEY="votre_secret_key_super_securisee_de_256_bits_minimum"

# Windows CMD
set EPICEVENTS_SECRET_KEY=votre_secret_key_super_securisee_de_256_bits_minimum
```

**Génération d'une clé sécurisée** :

```python
import secrets
secret_key = secrets.token_hex(32)  # 256 bits
print(secret_key)
```

### Développement

En développement, si la variable n'est pas définie, une clé est générée automatiquement.
**Attention** : Les tokens ne seront pas valides entre les redémarrages.

## Tests

Pour tester l'authentification :

```bash
# 1. Créer un utilisateur de test
poetry run epicevents create-user

# 2. Se connecter
poetry run epicevents login

# 3. Vérifier l'authentification
poetry run epicevents whoami

# 4. Tester une commande protégée
poetry run epicevents filter-unsigned-contracts

# 5. Se déconnecter
poetry run epicevents logout

# 6. Vérifier que l'accès est refusé
poetry run epicevents filter-unsigned-contracts
# Devrait afficher : "Vous devez être connecté"
```

## Principe du moindre privilège

Le système respecte le **principe du moindre privilège** du cahier des charges :

1. **Authentification obligatoire** : Toutes les commandes sensibles nécessitent une authentification
2. **Contrôle d'accès basé sur les rôles** : Chaque département a des permissions spécifiques
3. **Filtrage contextuel** : Les données sont filtrées selon le rôle et les responsabilités
4. **Pas d'accès global** : Aucune commande ne permet d'accéder à toutes les données sans filtre

## Conformité avec le cahier des charges

✅ Authentification avec identifiants (username/password)
✅ Autorisation basée sur les rôles (départements)
✅ Jetons JWT pour authentification persistante
✅ Stockage sécurisé des jetons
✅ Principe du moindre privilège appliqué
✅ Protection contre les injections SQL
✅ Journalisation avec Sentry (à implémenter)
