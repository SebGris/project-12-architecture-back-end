# Configuration Sentry - Epic Events CRM

Ce document explique comment configurer et utiliser Sentry pour la journalisation et le monitoring des erreurs dans l'application Epic Events CRM.

---

## 📋 Table des matières

1. [Pourquoi Sentry ?](#pourquoi-sentry-)
2. [Configuration initiale](#configuration-initiale)
3. [Variables d'environnement](#variables-denvironnement)
4. [Fonctionnalités implémentées](#fonctionnalités-implémentées)
5. [Test de l'intégration](#test-de-lintégration)
6. [Utilisation en production](#utilisation-en-production)

---

## Pourquoi Sentry ?

Sentry est une plateforme de monitoring d'erreurs qui permet de :

- 🔍 **Détecter les erreurs** en temps réel dans l'application
- 📊 **Monitorer les performances** des opérations critiques
- 🔐 **Tracer les tentatives de connexion** (succès et échecs)
- 🗺️ **Retracer le parcours utilisateur** avant une erreur (breadcrumbs)
- 📧 **Recevoir des alertes** par email ou Slack lors d'erreurs critiques
- 📈 **Analyser les tendances** d'erreurs et de performance

---

## Configuration initiale

### Étape 1 : Créer un compte Sentry

1. Aller sur [https://sentry.io](https://sentry.io)
2. Créer un compte gratuit (inclut jusqu'à 5 000 événements par mois)
3. Créer un nouveau projet :
   - **Platform** : Python
   - **Project name** : Epic Events CRM
   - **Team** : Votre équipe

### Étape 2 : Récupérer le DSN

Après la création du projet, Sentry vous fournira un **DSN** (Data Source Name) qui ressemble à :

```
https://abc123def456@o1234567.ingest.sentry.io/7654321
```

Ce DSN est la clé de connexion entre votre application et Sentry.

### Étape 3 : Configurer l'environnement

Ajoutez le DSN dans votre fichier `.env` :

```bash
# .env
EPICEVENTS_SECRET_KEY=40f04230e0ec57233c6ebb873c1142b7f86047a6bbd21c8f1d01a262a90651ba
SENTRY_DSN=https://abc123def456@o1234567.ingest.sentry.io/7654321
ENVIRONMENT=development
```

---

## Variables d'environnement

| Variable | Description | Valeur par défaut | Obligatoire |
|----------|-------------|------------------|-------------|
| `SENTRY_DSN` | DSN fourni par Sentry pour connecter l'application | Aucun | ❌ (optionnel) |
| `ENVIRONMENT` | Environnement d'exécution | `development` | ❌ |
| `EPICEVENTS_SECRET_KEY` | Clé secrète JWT | Aucun | ✅ |

**Notes** :
- Si `SENTRY_DSN` n'est pas défini, l'application fonctionne normalement sans Sentry
- L'`ENVIRONMENT` permet de filtrer les erreurs par environnement dans Sentry (dev/staging/production)

---

## Fonctionnalités implémentées

### 1. Initialisation automatique

Sentry est initialisé automatiquement au démarrage de l'application.

**Fichier** : `src/cli/main.py`

```python
def main():
    # Initialize Sentry for error tracking
    init_sentry()

    # ... reste du code
```

**Sortie console** :
```
[INFO] Sentry initialisé avec succès (environnement: development)
```

Ou si Sentry n'est pas configuré :
```
[INFO] Sentry non configuré (SENTRY_DSN manquant)
```

---

### 2. Traçage des tentatives de connexion

Toutes les tentatives de connexion (succès et échecs) sont journalisées dans Sentry.

**Fichier** : `src/services/auth_service.py`

#### Connexion réussie

```python
# Breadcrumb ajouté
"Connexion réussie pour l'utilisateur: admin"
```

#### Échec de connexion - Utilisateur inexistant

```python
# Message capturé avec niveau "warning"
"Tentative de connexion échouée - utilisateur inexistant: unknown_user"
```

#### Échec de connexion - Mot de passe incorrect

```python
# Message capturé avec niveau "warning"
"Tentative de connexion échouée - mot de passe incorrect: admin"
```

---

### 3. Contexte utilisateur

Après une connexion réussie, Sentry associe toutes les erreurs à l'utilisateur connecté.

**Fichier** : `src/cli/commands.py`

```python
# Lors du login
set_user_context(user.id, user.username, user.department.value)

# Lors du logout
clear_user_context()
```

**Avantage** : Dans Sentry, vous pouvez voir quel utilisateur a rencontré une erreur, son département, etc.

---

### 4. Breadcrumbs (fil d'Ariane)

Les breadcrumbs permettent de retracer les actions de l'utilisateur avant qu'une erreur ne se produise.

**Exemple de séquence** :
```
1. [auth] Tentative de connexion pour l'utilisateur: admin
2. [auth] Connexion réussie pour l'utilisateur: admin (user_id: 1, department: GESTION)
3. [action] Création d'un client
4. [error] IntegrityError: Email déjà existant
```

---

### 5. Capture d'exceptions non gérées

Toutes les exceptions non gérées dans l'application sont automatiquement capturées.

**Fichier** : `src/cli/main.py`

```python
try:
    commands.app()
except Exception as e:
    # Capture unhandled exceptions in Sentry
    capture_exception(e, context={"location": "main"})
    raise
```

---

## Test de l'intégration

### Test 1 : Vérifier l'initialisation

```bash
poetry run epicevents whoami
```

**Sortie attendue** :
```
[INFO] Sentry initialisé avec succès (environnement: development)
[ERREUR] Vous n'êtes pas connecté...
```

✅ Le message `[INFO] Sentry initialisé...` confirme que Sentry est configuré.

---

### Test 2 : Tester la journalisation des connexions

```bash
# Tentative avec un mauvais mot de passe
poetry run epicevents login
# Username: admin
# Password: wrong_password
```

**Vérification dans Sentry** :
1. Aller sur votre dashboard Sentry
2. Vous devriez voir un événement de niveau "warning" :
   ```
   Tentative de connexion échouée - mot de passe incorrect: admin
   ```

---

### Test 3 : Tester le contexte utilisateur

```bash
# Connexion réussie
poetry run epicevents login
# Username: admin
# Password: Admin123!

# Provoquer une erreur (exemple)
poetry run epicevents create-client
# (Saisir un email déjà existant pour provoquer une IntegrityError)
```

**Vérification dans Sentry** :
1. L'erreur sera associée à l'utilisateur `admin`
2. Vous verrez les breadcrumbs de connexion et de création de client
3. Le contexte utilisateur inclura :
   - `id`: 1
   - `username`: admin
   - `department`: GESTION

---

### Test 4 : Simuler une erreur

Pour tester la capture d'exceptions, créez temporairement une erreur :

```python
# Dans src/cli/commands.py, ajoutez temporairement dans la commande whoami :
def whoami():
    container = Container()
    auth_service = container.auth_service()

    # TEST: Simuler une erreur
    raise ValueError("Test Sentry - Cette erreur est volontaire")

    # ... reste du code
```

```bash
poetry run epicevents whoami
```

**Vérification dans Sentry** :
- Une erreur de type `ValueError` devrait apparaître
- Le message sera "Test Sentry - Cette erreur est volontaire"
- La stack trace complète sera disponible

**N'oubliez pas de supprimer cette ligne de test après !**

---

## Utilisation en production

### Configuration recommandée

```bash
# .env (production)
EPICEVENTS_SECRET_KEY=<votre_cle_production_super_securisee>
SENTRY_DSN=https://your-production-dsn@sentry.io/project
ENVIRONMENT=production
```

### Ajustement des taux d'échantillonnage

Pour la production, réduisez les taux d'échantillonnage pour économiser les quotas Sentry :

**Fichier** : `src/sentry_config.py`

```python
sentry_sdk.init(
    dsn=sentry_dsn,

    # Réduire à 10% en production
    traces_sample_rate=0.1,  # 10% des transactions
    profiles_sample_rate=0.1,  # 10% des profils

    environment=environment,
)
```

### Alertes et notifications

Dans Sentry, configurez des alertes pour :

1. **Erreurs critiques** (500 Internal Server Error)
   - Notification immédiate par email
   - Alerte Slack pour l'équipe

2. **Tentatives de connexion échouées répétées**
   - Alerte si > 10 tentatives échouées en 5 minutes
   - Possible attaque par force brute

3. **Erreurs d'intégrité de base de données**
   - Notification pour les `IntegrityError`
   - Peut indiquer un problème de données

---

## Architecture de logging Sentry

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Application                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  init_sentry()                        │   │
│  │         (Initialize at application start)             │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Event Tracking                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • add_breadcrumb() - User actions trail             │   │
│  │  • capture_message() - Info/Warning/Error messages   │   │
│  │  • capture_exception() - Unhandled exceptions        │   │
│  │  • set_user_context() - User identification          │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Sentry.io Platform                        │
│  • Error aggregation and analysis                           │
│  • Performance monitoring                                   │
│  • User impact tracking                                     │
│  • Alert notifications                                      │
│  • Issue assignment and resolution                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Événements journalisés

| Événement | Type | Niveau | Contexte |
|-----------|------|--------|----------|
| Tentative de connexion | Breadcrumb | info | username |
| Connexion réussie | Breadcrumb | info | user_id, department |
| Connexion échouée (user not found) | Message | warning | username, reason |
| Connexion échouée (wrong password) | Message | warning | username, reason |
| Déconnexion | Breadcrumb | info | username |
| Exception non gérée | Exception | error | stack trace complète |
| Erreur d'intégrité DB | Exception | error | error details |

---

## Conformité avec le cahier des charges

| Exigence | Implémentation | Statut |
|----------|----------------|--------|
| Journalisation avec Sentry | Module `src/sentry_config.py` | ✅ |
| Logging des exceptions | Capture automatique via `main.py` | ✅ |
| Logging des tentatives de connexion | `auth_service.py` avec capture_message | ✅ |
| Contexte utilisateur | set_user_context() dans login | ✅ |
| Breadcrumbs pour le parcours utilisateur | add_breadcrumb() dans les actions clés | ✅ |
| Configuration par environnement | Variable ENVIRONMENT dans .env | ✅ |

---

## Ressources supplémentaires

- **Documentation Sentry** : [https://docs.sentry.io/platforms/python/](https://docs.sentry.io/platforms/python/)
- **Intégration Python** : [https://docs.sentry.io/platforms/python/integrations/](https://docs.sentry.io/platforms/python/integrations/)
- **Best practices** : [https://docs.sentry.io/product/sentry-basics/](https://docs.sentry.io/product/sentry-basics/)

---

**Date de dernière mise à jour** : 2025-11-03
**Version** : 1.0
