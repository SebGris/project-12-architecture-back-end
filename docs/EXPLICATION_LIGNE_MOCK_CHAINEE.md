# Explication : mock_container.return_value.auth_service.return_value

## La ligne mystérieuse

```python
mock_container.return_value.auth_service.return_value = mock_auth_service
```

Cette ligne est **la plus complexe** du test. Elle simule **2 niveaux d'appels** imbriqués.

---

## Étape 1 : Comprendre le code réel

### Code dans `commands.py` (lignes 185-193)

```python
def whoami():
    # Étape A : Créer le container
    container = Container()

    # Étape B : Récupérer auth_service
    auth_service = container.auth_service()

    # Étape C : Récupérer l'utilisateur
    user = auth_service.get_current_user()
```

**3 appels successifs** :
1. `Container()` → crée un objet container
2. `container.auth_service()` → récupère l'auth_service
3. `auth_service.get_current_user()` → récupère l'utilisateur

---

## Étape 2 : Le problème dans les tests

Dans le test, on veut **simuler** ces 3 appels sans toucher à la vraie base de données.

### Ce qu'on veut faire :

```python
# Code réel exécuté           → Ce qu'on veut retourner dans le test
Container()                   → mock_container_instance (objet fictif)
container.auth_service()      → mock_auth_service (objet fictif)
auth_service.get_current_user() → None (pas d'utilisateur)
```

### Le défi :

Comment dire à Python :
> "Quand le code appelle `Container()`, retourne un mock.
> Quand ce mock appelle `.auth_service()`, retourne un autre mock.
> Quand ce mock appelle `.get_current_user()`, retourne `None`."

---

## Étape 3 : Décortiquer la ligne

```python
mock_container.return_value.auth_service.return_value = mock_auth_service
# └─────┬──────┘ └──────┬─────┘ └───────┬──────┘ └────────┬────────┘
#       1                2               3                  4
```

### Partie 1 : `mock_container`

```python
# Dans le test (ligne 56)
mock_container = mocker.patch("src.cli.commands.Container")
```

**Ce que fait `patch`** : Remplace la classe `Container` par un mock.

```python
# Code réel
container = Container()  # ← Container est patché !

# Devient
container = mock_container()  # Appelle le mock comme une fonction
```

### Partie 2 : `.return_value`

**Question** : Que retourne `mock_container()` quand on l'appelle ?

**Réponse** : Ce qu'on met dans `mock_container.return_value` !

```python
# Configuration
mock_container.return_value = <quelque chose>

# Quand le code exécute
container = Container()  # ← Appelle mock_container()

# Ça retourne
container = mock_container.return_value  # ← C'est <quelque chose>
```

**Exemple visuel** :

```python
# Si on configure ça :
mock_container.return_value = "HELLO"

# Alors :
container = Container()  # ← container vaut "HELLO"
```

### Partie 3 : `.auth_service`

Maintenant, le code réel fait :

```python
auth_service = container.auth_service()
#              └───────────┬──────────┘
#                    Appelle cette méthode
```

**Question** : Comment simuler `container.auth_service()` ?

**Réponse** : `container` est en fait `mock_container.return_value`, donc :

```python
auth_service = container.auth_service()
#              ↓ (container est le return_value du mock)
auth_service = mock_container.return_value.auth_service()
```

Et que retourne `.auth_service()` ? Ce qu'on met dans `.return_value` !

```python
mock_container.return_value.auth_service.return_value = <quelque chose>
```

### Partie 4 : `= mock_auth_service`

On dit : "Quand `container.auth_service()` est appelé, retourne `mock_auth_service`."

```python
mock_container.return_value.auth_service.return_value = mock_auth_service
```

---

## Étape 4 : Visualisation complète du flux

### Setup dans le test

```python
# Ligne 56 : Patch Container
mock_container = mocker.patch("src.cli.commands.Container")

# Ligne 58 : Créer un mock pour auth_service
mock_auth_service = mocker.MagicMock()

# Ligne 59 : Configurer get_current_user pour retourner None
mock_auth_service.get_current_user.return_value = None

# Ligne 60 : LA LIGNE COMPLEXE
mock_container.return_value.auth_service.return_value = mock_auth_service
```

### Exécution du code réel

```python
# Code réel                            Ce qui se passe dans le test
# ─────────────────────────────────────────────────────────────────────

container = Container()               # Appelle mock_container()
                                      # Retourne : mock_container.return_value
                                      # container = un mock

auth_service = container.auth_service()  # Appelle mock_container.return_value.auth_service()
                                         # Retourne : mock_container.return_value.auth_service.return_value
                                         # auth_service = mock_auth_service

user = auth_service.get_current_user()  # Appelle mock_auth_service.get_current_user()
                                        # Retourne : None (configuré ligne 59)
                                        # user = None
```

---

## Étape 5 : Analogie avec des boîtes

Imagine des **boîtes gigognes** (poupées russes) :

```
┌─────────────────────────────────────────┐
│ Container()                             │  ← Appel 1
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ .auth_service()                   │ │  ← Appel 2
│  │                                   │ │
│  │  ┌─────────────────────────────┐ │ │
│  │  │ .get_current_user()         │ │ │  ← Appel 3
│  │  │                             │ │ │
│  │  │  Result: None               │ │ │  ← Résultat final
│  │  └─────────────────────────────┘ │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Configuration des boîtes** :

```python
# Boîte 1 : Container() retourne quoi ?
mock_container.return_value = <boîte 2>

# Boîte 2 : .auth_service() retourne quoi ?
mock_container.return_value.auth_service.return_value = <boîte 3>

# Boîte 3 : .get_current_user() retourne quoi ?
mock_auth_service.get_current_user.return_value = None
```

---

## Étape 6 : Pourquoi c'est si complexe ?

### Option 1 : Code idéal (simple)

Si le code était écrit comme ça :

```python
def whoami():
    auth_service = get_auth_service()  # ← Un seul appel
    user = auth_service.get_current_user()
```

Le mock serait simple :

```python
mock_auth = mocker.patch("src.cli.commands.get_auth_service")
mock_auth.return_value.get_current_user.return_value = None
```

### Option 2 : Code réel (complexe)

Mais le code fait ça :

```python
def whoami():
    container = Container()            # ← Appel 1
    auth_service = container.auth_service()  # ← Appel 2
    user = auth_service.get_current_user()   # ← Appel 3
```

Donc on doit simuler **2 niveaux** :

```python
mock_container.return_value.auth_service.return_value = mock_auth_service
#              └──────┬─────┘          └──────┬─────┘
#               Niveau 1                Niveau 2
```

---

## Étape 7 : Réécriture étape par étape (plus lisible)

### Version originale (concise mais difficile)

```python
mock_container.return_value.auth_service.return_value = mock_auth_service
```

### Version équivalente (verbeuse mais claire)

```python
# Étape 1 : Créer un mock pour l'instance de Container
mock_container_instance = mocker.MagicMock()

# Étape 2 : Dire que Container() retourne cette instance
mock_container.return_value = mock_container_instance

# Étape 3 : Dire que .auth_service() retourne mock_auth_service
mock_container_instance.auth_service.return_value = mock_auth_service
```

**Les deux versions font EXACTEMENT la même chose !**

---

## Étape 8 : Schéma avec flèches

```
Code réel                         Configuration du mock
════════════════════════════════════════════════════════════════

container = Container()     ←─┐
                              │
                              │    mock_container (patché)
                              │         ↓
                              │    .return_value
                              │         ↓
                              └────  mock_container_instance
                                     (objet fictif)

─────────────────────────────────────────────────────────────

auth_service = container.auth_service()  ←─┐
                                           │
                                           │   mock_container_instance
                                           │         ↓
                                           │    .auth_service()
                                           │         ↓
                                           │    .return_value
                                           │         ↓
                                           └────  mock_auth_service
                                                  (objet fictif)

─────────────────────────────────────────────────────────────

user = auth_service.get_current_user()  ←─┐
                                          │
                                          │   mock_auth_service
                                          │         ↓
                                          │    .get_current_user()
                                          │         ↓
                                          │    .return_value
                                          │         ↓
                                          └────  None
                                                (pas d'utilisateur)
```

---

## Étape 9 : Exemple concret avec valeurs réelles

Imaginons qu'on veuille tracer chaque étape :

```python
# Setup
mock_container = mocker.patch("src.cli.commands.Container")
mock_auth_service = mocker.MagicMock()
mock_auth_service.get_current_user.return_value = None

# LA LIGNE COMPLEXE
mock_container.return_value.auth_service.return_value = mock_auth_service

# ═══════════════════════════════════════════════════════════════

# Exécution du code réel
print("Étape 1 : Appel Container()")
container = Container()
print(f"  → container = {container}")
print(f"  → Type: {type(container)}")
# Output: container = <MagicMock id='140234567890123'>

print("\nÉtape 2 : Appel container.auth_service()")
auth_service = container.auth_service()
print(f"  → auth_service = {auth_service}")
print(f"  → Type: {type(auth_service)}")
# Output: auth_service = <MagicMock id='140234567890456'>

print("\nÉtape 3 : Appel auth_service.get_current_user()")
user = auth_service.get_current_user()
print(f"  → user = {user}")
print(f"  → Type: {type(user)}")
# Output: user = None
```

---

## Étape 10 : Test de compréhension

### Question 1 : Que retourne cette ligne ?

```python
container = Container()
```

**Réponse** : `mock_container.return_value`

### Question 2 : Que retourne cette ligne ?

```python
auth_service = container.auth_service()
```

**Réponse** : `mock_container.return_value.auth_service.return_value` = `mock_auth_service`

### Question 3 : Que retourne cette ligne ?

```python
user = auth_service.get_current_user()
```

**Réponse** : `None` (configuré ligne 59)

### Question 4 : Combien de fois validate_token() est appelé ?

**Réponse** : 0 fois ! On utilise des mocks, aucune vraie validation n'est faite.

---

## Étape 11 : Comparaison avec un cas plus simple

### Cas simple : 1 niveau

```python
# Code réel
service = get_service()
result = service.do_something()

# Mock (simple)
mock_service = mocker.patch("module.get_service")
mock_service.return_value.do_something.return_value = "OK"
```

### Cas complexe : 2 niveaux (votre code)

```python
# Code réel
container = Container()               # Niveau 1
service = container.get_service()      # Niveau 2
result = service.do_something()        # Niveau 3

# Mock (complexe)
mock_container = mocker.patch("module.Container")
mock_container.return_value.get_service.return_value = mock_service
mock_service.do_something.return_value = "OK"
```

---

## Étape 12 : Pourquoi ne pas simplifier le code réel ?

### Solution 1 : Injection de dépendances

```python
def whoami(auth_service=None):
    if not auth_service:
        container = Container()
        auth_service = container.auth_service()

    user = auth_service.get_current_user()
```

**Test simplifié** :

```python
mock_auth_service = mocker.MagicMock()
mock_auth_service.get_current_user.return_value = None

result = runner.invoke(app, ["whoami"], auth_service=mock_auth_service)
```

Mais Typer ne supporte pas facilement ce pattern.

### Solution 2 : Factory globale

```python
# module.py
_container = None

def get_container():
    global _container
    if not _container:
        _container = Container()
    return _container

def whoami():
    auth_service = get_container().auth_service()
    user = auth_service.get_current_user()
```

**Test simplifié** :

```python
mock_container = mocker.patch("module.get_container")
mock_container.return_value.auth_service.return_value = mock_auth_service
```

Mais ça introduit de l'état global (anti-pattern).

---

## Résumé en 3 niveaux

### Niveau 1 : Explication simple

"Cette ligne dit : Quand le code crée un Container et appelle `.auth_service()`, retourne `mock_auth_service`."

### Niveau 2 : Explication technique

"On configure le mock pour que `Container().auth_service()` retourne un objet fictif qu'on contrôle."

### Niveau 3 : Explication détaillée

"On patch `Container` avec `mock_container`. Quand le code appelle `Container()`, ça retourne `mock_container.return_value` (un mock). Quand le code appelle `.auth_service()` sur ce mock, ça retourne `mock_container.return_value.auth_service.return_value`, qu'on a configuré pour être `mock_auth_service`."

---

## Conclusion : Pourquoi c'est important

Cette ligne est **essentielle** pour :

1. ✅ **Isoler le test** : Pas de vraie base de données
2. ✅ **Contrôler le comportement** : On décide ce que retourne chaque appel
3. ✅ **Tester la logique** : On vérifie uniquement la commande CLI, pas les dépendances

**Sans cette ligne**, le test essaierait de :
- Créer un vrai Container
- Se connecter à une vraie base de données
- Lire un vrai fichier de token

**Avec cette ligne**, on simule tout et le test est :
- Rapide (< 1 seconde)
- Fiable (pas de dépendances externes)
- Prévisible (on contrôle tous les retours)

---

**Date de création** : 2025-11-17
**Dernière mise à jour** : 2025-11-17
**Version** : 1.0
