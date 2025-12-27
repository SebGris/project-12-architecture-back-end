# Guide de Démarrage Rapide - Authentification

## Prérequis

Avant de commencer, assurez-vous que :
- L'application est installée : `poetry install`
- La base de données est initialisée avec au moins un utilisateur

## Première Connexion

### 1. Créer un utilisateur (si nécessaire)

Si aucun utilisateur n'existe, créez-en un :

```bash
poetry run epicevents create-user
```

Exemple de saisie :
```
Nom d'utilisateur: admin
Prénom: Admin
Nom: System
Email: admin@epicevents.com
Téléphone: 0123456789
Mot de passe: ******** (minimum 8 caractères)

Départements disponibles:
1. COMMERCIAL
2. GESTION
3. SUPPORT

Choisir un département (numéro): 2
```

### 2. Se connecter

```bash
poetry run epicevents login
```

Saisir :
```
Nom d'utilisateur: admin
Mot de passe: ********
```

Résultat :
```
+-----------------------------------------------------------------------------+
|                           Authentification                                  |
+-----------------------------------------------------------------------------+

+-----------------------------------------------------------------------------+
| ✓ Bienvenue Admin System !                                                 |
| Département : GESTION                                                       |
| Session     : Valide pour 24 heures                                        |
+-----------------------------------------------------------------------------+
```

### 3. Vérifier l'authentification

```bash
poetry run epicevents whoami
```

Résultat :
```
+-----------------------------------------------------------------------------+
|                           Utilisateur actuel                                |
+-----------------------------------------------------------------------------+
| ID                : 1                                                       |
| Nom d'utilisateur : admin                                                   |
| Nom complet       : Admin System                                            |
| Email             : admin@epicevents.com                                    |
| Téléphone         : 0123456789                                              |
| Département       : GESTION                                                 |
+-----------------------------------------------------------------------------+
```

## Utilisation Quotidienne

### Commandes Disponibles (après connexion)

#### Gestion des Clients
```bash
# Créer un client
poetry run epicevents create-client

# Modifier un client
poetry run epicevents update-client
```

#### Gestion des Contrats
```bash
# Créer un contrat
poetry run epicevents create-contract

# Modifier un contrat
poetry run epicevents update-contract

# Filtrer les contrats non signés
poetry run epicevents filter-unsigned-contracts

# Filtrer les contrats non soldés
poetry run epicevents filter-unpaid-contracts
```

#### Gestion des Événements
```bash
# Créer un événement
poetry run epicevents create-event

# Assigner un contact support
poetry run epicevents assign-support

# Filtrer les événements sans support
poetry run epicevents filter-unassigned-events

# Filtrer mes événements (SUPPORT)
poetry run epicevents filter-my-events
```

#### Gestion des Utilisateurs (GESTION uniquement)
```bash
# Créer un utilisateur
poetry run epicevents create-user
```

### Déconnexion

```bash
poetry run epicevents logout
```

Résultat :
```
+-----------------------------------------------------------------------------+
|                             Déconnexion                                     |
+-----------------------------------------------------------------------------+
| ✓ Au revoir Admin System !                                                 |
+-----------------------------------------------------------------------------+
```

## Gestion des Erreurs

### Erreur : "Vous devez être connecté"

**Problème** : Le token JWT a expiré (> 24h) ou n'existe pas.

**Solution** :
```bash
poetry run epicevents login
```

### Erreur : "Action non autorisée pour votre département"

**Problème** : Vous n'avez pas les permissions pour cette action.

**Solution** : Vérifiez votre département avec `whoami` et consultez la matrice des permissions.

### Erreur : "Nom d'utilisateur ou mot de passe incorrect"

**Problème** : Identifiants invalides.

**Solution** :
1. Vérifiez votre nom d'utilisateur
2. Vérifiez votre mot de passe
3. Si oublié, contactez un administrateur GESTION

## Scénarios d'Utilisation

### Scénario 1 : Commercial crée un client et un événement

```bash
# 1. Se connecter en tant que commercial
poetry run epicevents login
# Username: john_commercial
# Password: ********

# 2. Créer un client (auto-assigné au commercial connecté)
poetry run epicevents create-client
# Prénom: Marie
# Nom: Martin
# Email: marie.martin@example.com
# ...

# 3. Créer un contrat pour ce client
poetry run epicevents create-contract
# ID du client: 1
# Montant total: 10000
# Montant restant: 5000
# Contrat signé ? true

# 4. Créer un événement pour ce contrat signé
poetry run epicevents create-event
# Nom: Mariage Marie Martin
# ID du contrat: 1
# Date début: 2026-01-15 14:00
# ...
```

### Scénario 2 : Gestion assigne un support à un événement

```bash
# 1. Se connecter en tant que gestionnaire
poetry run epicevents login
# Username: admin
# Password: Admin123!

# 2. Voir les événements sans support
poetry run epicevents filter-unassigned-events

# 3. Assigner un support
poetry run epicevents assign-support
# ID de l'événement: 1
# ID du contact support: 5
```

### Scénario 3 : Support consulte et met à jour ses événements

```bash
# 1. Se connecter en tant que support
poetry run epicevents login
# Username: bob_support
# Password: ********

# 2. Voir mes événements
poetry run epicevents filter-my-events
# ID du contact support: 5

# 3. Mettre à jour un événement (si implémenté)
# ...
```

## Configuration Avancée

### Variable d'Environnement (Production)

Pour la production, définissez une clé secrète sécurisée :

**Linux/Mac** :
```bash
export EPICEVENTS_SECRET_KEY="votre_cle_secrete_de_256_bits"
```

**Windows PowerShell** :
```powershell
$env:EPICEVENTS_SECRET_KEY="votre_cle_secrete_de_256_bits"
```

**Windows CMD** :
```cmd
set EPICEVENTS_SECRET_KEY=votre_cle_secrete_de_256_bits
```

### Générer une Clé Sécurisée

```python
import secrets
secret_key = secrets.token_hex(32)  # 256 bits
print(secret_key)
# Exemple de sortie: 3f7d2a8c9e1b4f6a8d3c7e2b9f1a4d6c8e3b7f2a9d1c4e6b8f3a7d2c9e1b4f6a
```

## Fichiers Importants

- **Token JWT** : `~/.epicevents/token`
  - Contient le jeton d'authentification
  - Permissions : 600 (lecture/écriture propriétaire uniquement)
  - Valide 24 heures

- **Base de données** : `epic_events_crm.db` (développement)
  - Contient tous les utilisateurs et données
  - Ne pas supprimer sans backup

## Dépannage

### Le fichier token n'existe pas

**Normal** : Le token est créé lors du premier login.

### Token invalide après redémarrage

**Cause** : En développement, la clé secrète est régénérée à chaque redémarrage.

**Solution** : Définir `EPICEVENTS_SECRET_KEY` dans les variables d'environnement.

### Permissions refusées sur token

**Cause** : Permissions fichier incorrectes.

**Solution** (Linux/Mac) :
```bash
chmod 600 ~/.epicevents/token
```

## Support

Pour toute question ou problème :
1. Consultez la documentation dans `/docs`
2. Vérifiez les logs d'erreur
3. Contactez l'équipe de développement
