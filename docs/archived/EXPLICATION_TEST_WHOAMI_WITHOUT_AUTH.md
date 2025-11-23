# Explication ligne par ligne : test_whoami_without_authentication

## Vue d'ensemble

Ce test vérifie que la commande `whoami` affiche un message d'erreur quand l'utilisateur n'est **pas authentifié**.

**Fichier** : [`tests/unit/test_authentication_commands.py`](../tests/unit/test_authentication_commands.py#L50-L68)

**Scénario testé** :
1. Aucun utilisateur n'est connecté (pas de token valide)
2. L'utilisateur exécute `epicevents whoami`
3. L'application affiche un message d'erreur et suggère de se connecter

---

## Code complet

```python
class TestWhoamiWithoutAuthentication:
    """Test whoami command when user is not authenticated."""

    def test_whoami_without_authentication(self, mocker):
        """
        GIVEN no authenticated user
        WHEN whoami command is executed
        THEN it should display an error message and exit with code 1
        """
        mock_container = mocker.patch("src.cli.commands.Container")
        # Mock auth_service to return None (no user authenticated)
        mock_auth_service = mocker.MagicMock()
        mock_auth_service.get_current_user.return_value = None
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute whoami command
        result = runner.invoke(app, ["whoami"])

        # Verify exit code and error message
        assert result.exit_code == 1
        assert "Vous n'êtes pas connecté" in result.stdout
        assert "epicevents login" in result.stdout
```

---

## Explication ligne par ligne

### Ligne 47-48 : Classe de tests

```python
class TestWhoamiWithoutAuthentication:
    """Test whoami command when user is not authenticated."""
```

**Pourquoi une classe ?**
- Organisation : Groupe les tests liés à `whoami` sans authentification
- Partage de fixtures : Si besoin de setup commun entre plusieurs tests
- Lisibilité : Structure claire dans les rapports pytest

**Convention de nommage** :
- Commence par `Test` (obligatoire pour pytest)
- Nom descriptif : `TestWhoamiWithoutAuthentication`

**Résultat dans pytest** :
```
tests/unit/test_authentication_commands.py::TestWhoamiWithoutAuthentication::test_whoami_without_authentication PASSED
```

---

### Ligne 50 : Signature de la méthode

```python
def test_whoami_without_authentication(self, mocker):
```

**Décomposition** :

#### `def test_whoami_without_authentication`
- **Doit commencer par `test_`** (convention pytest)
- Nom descriptif du scénario testé
- pytest détecte automatiquement cette fonction comme un test

#### `self`
- Référence à l'instance de la classe `TestWhoamiWithoutAuthentication`
- Obligatoire pour les méthodes de classe (même si non utilisé ici)

#### `mocker`
- **Fixture pytest-mock** injectée automatiquement
- Permet de créer des mocks (objets fictifs)
- Fournie par le plugin `pytest-mock`

**Équivalent sans classe** :
```python
def test_whoami_without_authentication(mocker):
    # Fonctionne aussi, pas besoin de 'self'
```

---

### Lignes 51-55 : Docstring (format Given-When-Then)

```python
"""
GIVEN no authenticated user
WHEN whoami command is executed
THEN it should display an error message and exit with code 1
"""
```

**Format BDD (Behavior-Driven Development)** :

| Section | Signification | Valeur ici |
|---------|---------------|------------|
| **GIVEN** | Contexte initial | Pas d'utilisateur authentifié |
| **WHEN** | Action effectuée | Exécution de `whoami` |
| **THEN** | Résultat attendu | Message d'erreur + code 1 |

**Pourquoi ce format ?**
- ✅ Lisible par tous (développeurs, testeurs, product owners)
- ✅ Spec exécutable : le test EST la documentation
- ✅ Couvre le "quoi" sans détailler le "comment"

**Exemple de lecture** :
> "**Étant donné** qu'aucun utilisateur n'est authentifié,
> **Quand** on exécute la commande whoami,
> **Alors** elle doit afficher un message d'erreur et se terminer avec le code 1."

---

### Ligne 56 : Patch du Container

```python
mock_container = mocker.patch("src.cli.commands.Container")
```

**Que fait cette ligne ?**

1. **Remplace** la classe `Container` dans le module `src.cli.commands`
2. Par un **mock** (objet fictif contrôlable)
3. Retourne une référence au mock pour configuration

**Visualisation** :

```
Code original (commands.py) :
┌──────────────────────────────────────┐
│ from src.containers import Container │
│                                      │
│ def whoami():                        │
│     container = Container()          │  ← Container réel
│     auth_service = container.auth_service() │
│     user = auth_service.get_current_user() │
└──────────────────────────────────────┘

Après mocker.patch() :
┌──────────────────────────────────────┐
│ from src.containers import Container │
│                                      │
│ def whoami():                        │
│     container = Container()          │  ← Container MOCKÉ
│     auth_service = container.auth_service() │
│     user = auth_service.get_current_user() │
└──────────────────────────────────────┘
```

**Pourquoi patcher ?**
- Évite de créer une vraie instance de Container
- Évite de se connecter à une vraie base de données
- Permet de contrôler exactement ce que retourne `auth_service`

**Équivalent sans pytest-mock** :
```python
from unittest.mock import patch

with patch("src.cli.commands.Container") as mock_container:
    # ... test logic
# Nettoyage automatique à la sortie du 'with'
```

**Avec pytest-mock (ce qu'on fait)** :
```python
mock_container = mocker.patch("src.cli.commands.Container")
# ... test logic
# Nettoyage automatique à la fin du test !
```

---

### Ligne 58 : Création d'un MagicMock

```python
mock_auth_service = mocker.MagicMock()
```

**Que fait cette ligne ?**

Crée un **objet mock** qui peut simuler n'importe quelle méthode ou attribut.

**Différence Mock vs MagicMock** :

```python
# Mock (basique)
mock = mocker.Mock()
mock.method()      # ✅ OK
len(mock)          # ❌ TypeError

# MagicMock (avec méthodes magiques)
magic = mocker.MagicMock()
magic.method()     # ✅ OK
len(magic)         # ✅ OK (retourne 0 par défaut)
str(magic)         # ✅ OK
magic["key"]       # ✅ OK
```

**Pourquoi MagicMock ici ?**
- Plus flexible si on veut ajouter des comportements complexes
- Convention dans le projet (cohérence)

**Ce qu'on peut faire avec** :
```python
mock_auth_service = mocker.MagicMock()

# Définir des valeurs de retour
mock_auth_service.get_current_user.return_value = None

# Définir des side effects (exceptions, fonctions custom)
mock_auth_service.authenticate.side_effect = ValueError("Invalid")

# Vérifier les appels après le test
mock_auth_service.get_current_user.assert_called_once()
```

---

### Ligne 59 : Configuration du mock (return_value)

```python
mock_auth_service.get_current_user.return_value = None
```

**Que fait cette ligne ?**

Configure le mock pour que `get_current_user()` retourne **`None`** (pas d'utilisateur authentifié).

**Décomposition** :

```python
mock_auth_service                      # L'objet mock
    .get_current_user                  # Attribut (sera une méthode)
    .return_value                      # Valeur à retourner quand appelée
    = None                             # Pas d'utilisateur connecté
```

**Simulation du comportement réel** :

```python
# Code réel (auth_service.py)
class AuthService:
    def get_current_user(self) -> Optional[User]:
        """Retourne l'utilisateur connecté ou None."""
        token = self.load_token()
        if not token:
            return None  # ← Ce qu'on simule !
        # ... validation JWT, récupération user
        return user

# Dans le test (simulation)
mock_auth_service.get_current_user.return_value = None
# Équivalent à : get_current_user() → None
```

**Flux d'exécution** :

```python
# Quand la commande whoami est exécutée :
auth_service.get_current_user()  # ← Appelle le mock
# Retourne : None (défini par return_value)
```

**Autres exemples de return_value** :

```python
# Retourner un utilisateur valide
mock_auth_service.get_current_user.return_value = mock_user

# Retourner différentes valeurs à chaque appel
mock_auth_service.get_current_user.side_effect = [None, mock_user, None]
# Appel 1 → None
# Appel 2 → mock_user
# Appel 3 → None

# Lever une exception
mock_auth_service.get_current_user.side_effect = RuntimeError("Token expiré")
```

---

### Ligne 60 : Chaînage des mocks

```python
mock_container.return_value.auth_service.return_value = mock_auth_service
```

**Cette ligne est COMPLEXE**, décomposons-la étape par étape.

#### Contexte : Code réel de whoami

Voici ce que fait réellement la commande `whoami` dans `commands.py` :

```python
@app.command()
def whoami():
    """Affiche l'utilisateur actuellement connecté."""
    # Étape 1 : Créer le container
    container = Container()

    # Étape 2 : Récupérer auth_service
    auth_service = container.auth_service()

    # Étape 3 : Récupérer l'utilisateur
    user = auth_service.get_current_user()
```

#### Chaînage des mocks pour simuler ce comportement

```python
mock_container.return_value.auth_service.return_value = mock_auth_service
# └─────┬──────┘ └──────┬─────┘ └───────┬──────┘ └────────┬────────┘
#       1                2               3                  4
```

**Étape par étape** :

##### 1️⃣ `mock_container`
```python
# Code réel :
container = Container()  # ← Container est patché !

# Dans le test :
container = mock_container()  # Retourne mock_container.return_value
```

##### 2️⃣ `.return_value`
```python
# Quand Container() est appelé, il retourne ceci :
container = mock_container.return_value
# container est maintenant un autre mock !
```

##### 3️⃣ `.auth_service`
```python
# Code réel :
auth_service = container.auth_service()

# Dans le test :
auth_service = mock_container.return_value.auth_service()
# Retourne : mock_container.return_value.auth_service.return_value
```

##### 4️⃣ `.return_value = mock_auth_service`
```python
# On définit ce que retourne auth_service()
mock_container.return_value.auth_service.return_value = mock_auth_service
```

**Visualisation complète du flux** :

```python
# Code réel exécuté                    # Ce que retourne le mock
container = Container()              # → mock_container.return_value
auth_service = container.auth_service() # → mock_auth_service
user = auth_service.get_current_user()  # → None (défini ligne 59)
```

**Schéma graphique** :

```
Container()
    ↓ (patché par mock_container)
mock_container.return_value
    ↓ (appelé : .auth_service())
mock_container.return_value.auth_service.return_value
    ↓ (on configure ça = mock_auth_service)
mock_auth_service
    ↓ (appelé : .get_current_user())
None (défini ligne 59)
```

**Pourquoi cette complexité ?**

Parce qu'on doit simuler **deux niveaux d'appels** :
1. `Container()` → retourne un objet container
2. `container.auth_service()` → retourne un objet auth_service

**Alternative plus lisible (mais moins idiomatique)** :

```python
# Option 1 : Notre code (concis)
mock_container.return_value.auth_service.return_value = mock_auth_service

# Option 2 : Verbose mais plus clair
mock_container_instance = mocker.MagicMock()
mock_container_instance.auth_service.return_value = mock_auth_service
mock_container.return_value = mock_container_instance
```

---

### Ligne 63 : Exécution de la commande

```python
result = runner.invoke(app, ["whoami"])
```

**Décomposition** :

#### `runner`
```python
# Défini au début du fichier (ligne 21)
from typer.testing import CliRunner
runner = CliRunner()
```

`CliRunner` est un utilitaire de **Typer** (framework CLI) qui permet de tester des commandes comme si elles étaient exécutées dans un terminal.

**Analogie** :
```bash
# Dans un vrai terminal :
$ epicevents whoami

# Dans le test :
runner.invoke(app, ["whoami"])
```

#### `.invoke(app, ["whoami"])`

**Signature** :
```python
runner.invoke(
    app,           # Application Typer (définie dans commands.py)
    ["whoami"],    # Commande et arguments (comme sys.argv)
    input="...",   # (optionnel) Saisie utilisateur simulée
    env={...}      # (optionnel) Variables d'environnement
)
```

**Paramètres** :

| Paramètre | Valeur | Signification |
|-----------|--------|---------------|
| `app` | `from src.cli.commands import app` | L'application Typer à tester |
| `["whoami"]` | Liste d'arguments | Équivalent à `sys.argv[1:]` |

**Équivalent en ligne de commande** :
```bash
epicevents whoami
# argv = ["epicevents", "whoami"]
#         ^^^^^^^^^^^^  ^^^^^^^
#         argv[0]       argv[1]  ← Ce qu'on passe dans le test
```

#### Objet `result`

`invoke()` retourne un objet `Result` contenant :

```python
result.exit_code   # Code de sortie (0 = succès, 1+ = erreur)
result.stdout      # Sortie standard (ce qui s'affiche)
result.stderr      # Sortie d'erreur (rarement utilisé)
result.exception   # Exception levée (si erreur non gérée)
```

**Exemple** :
```python
result = runner.invoke(app, ["whoami"])

print(result.exit_code)  # 1 (erreur attendue)
print(result.stdout)     # "Vous n'êtes pas connecté. Utilisez 'epicevents login'."
```

---

### Ligne 66 : Vérification du code de sortie

```python
assert result.exit_code == 1
```

**Que vérifie cette assertion ?**

La commande doit se terminer avec un **code d'erreur 1** (échec).

**Codes de sortie Unix/Linux** :

| Code | Signification | Utilisation |
|------|---------------|-------------|
| `0` | Succès | Commande exécutée sans erreur |
| `1` | Erreur générale | Erreur applicative (ex: pas authentifié) |
| `2` | Mauvais usage | Commande mal utilisée |
| `126` | Commande non exécutable | Problème de permissions |
| `127` | Commande introuvable | Commande n'existe pas |
| `130` | Interruption (Ctrl+C) | Terminé par signal |

**Dans notre code (commands.py)** :

```python
@app.command()
def whoami():
    container = Container()
    auth_service = container.auth_service()
    user = auth_service.get_current_user()

    if not user:
        console.print("[red]Vous n'êtes pas connecté.")
        console.print("Utilisez 'epicevents login'")
        raise typer.Exit(code=1)  # ← Exit avec code 1 !

    # Afficher les infos utilisateur...
```

**Pourquoi `assert` et pas `if` ?**

```python
# ❌ Mauvais
if result.exit_code != 1:
    print("Erreur : code incorrect")

# ✅ Bon
assert result.exit_code == 1
```

**Avantages de `assert`** :
- pytest capture automatiquement les échecs
- Message d'erreur informatif :
  ```
  AssertionError: assert 0 == 1
   +  where 0 = <Result>.exit_code
  ```
- Pas besoin de gérer manuellement les erreurs

---

### Ligne 67 : Vérification du message d'erreur

```python
assert "Vous n'êtes pas connecté" in result.stdout
```

**Que vérifie cette assertion ?**

Le message affiché doit contenir la phrase **"Vous n'êtes pas connecté"**.

**Pourquoi `in` et pas `==` ?**

```python
# ❌ Trop strict (cassera si on ajoute des couleurs ANSI, emoji, etc.)
assert result.stdout == "Vous n'êtes pas connecté."

# ✅ Flexible (vérifie juste que la phrase est présente)
assert "Vous n'êtes pas connecté" in result.stdout
```

**Exemple de sortie réelle** :

```python
result.stdout = """
[red]Vous n'êtes pas connecté.[/red]
Utilisez 'epicevents login' pour vous authentifier.
"""

# Ces assertions passent :
assert "Vous n'êtes pas connecté" in result.stdout  # ✅
assert "epicevents login" in result.stdout          # ✅

# Celle-ci échoue :
assert result.stdout == "Vous n'êtes pas connecté"  # ❌ (trop strict)
```

**Alternatives possibles** :

```python
# Vérifier plusieurs messages
assert "Vous n'êtes pas connecté" in result.stdout
assert "Utilisez 'epicevents login'" in result.stdout

# Vérifier avec regex (pour patterns complexes)
import re
assert re.search(r"Vous n'êtes pas connecté", result.stdout)

# Vérifier que le message N'est PAS présent
assert "Bienvenue" not in result.stdout
```

---

### Ligne 68 : Vérification de la suggestion

```python
assert "epicevents login" in result.stdout
```

**Que vérifie cette assertion ?**

Le message doit suggérer à l'utilisateur d'exécuter `epicevents login`.

**Pourquoi vérifier ça ?**

- ✅ **UX (User Experience)** : Guider l'utilisateur vers la solution
- ✅ **Documentation** : Le message est auto-descriptif
- ✅ **Support** : Moins de questions "Comment je me connecte ?"

**Exemple d'amélioration progressive** :

```python
# Version 1 (minimale)
print("Erreur : non authentifié")

# Version 2 (avec solution)
print("Erreur : non authentifié. Utilisez 'epicevents login'")

# Version 3 (avec couleurs)
console.print("[red]❌ Vous n'êtes pas connecté.")
console.print("[yellow]💡 Utilisez 'epicevents login' pour vous authentifier.")
```

**Le test s'assure que cette suggestion est présente !**

---

## Résumé du flux complet

### 1️⃣ Setup (lignes 56-60)
```python
# Remplacer Container par un mock
mock_container = mocker.patch("src.cli.commands.Container")

# Créer un auth_service fictif
mock_auth_service = mocker.MagicMock()

# Configurer pour retourner None (pas d'utilisateur)
mock_auth_service.get_current_user.return_value = None

# Connecter tout ensemble
mock_container.return_value.auth_service.return_value = mock_auth_service
```

### 2️⃣ Exécution (ligne 63)
```python
# Simuler l'exécution de : epicevents whoami
result = runner.invoke(app, ["whoami"])
```

### 3️⃣ Vérifications (lignes 66-68)
```python
# Vérifier le code d'erreur
assert result.exit_code == 1

# Vérifier le message d'erreur
assert "Vous n'êtes pas connecté" in result.stdout

# Vérifier la suggestion
assert "epicevents login" in result.stdout
```

---

## Ce que ce test garantit

✅ **Sécurité** : Un utilisateur non authentifié ne peut pas accéder aux infos
✅ **UX** : Message d'erreur clair avec suggestion
✅ **Comportement** : Code de sortie approprié (1 = erreur)
✅ **Robustesse** : Pas de crash si aucun token

---

## Ce que ce test NE teste PAS

❌ Validation réelle du JWT
❌ Connexion à la base de données
❌ Gestion des tokens expirés
❌ Permissions des fichiers

**Pourquoi ?**
- Ce sont des **tests unitaires** (une seule unité : la commande CLI)
- Les autres aspects sont testés ailleurs :
  - `test_user_creation.py` → Logique User
  - `test_authentication_commands.py` → Flux complet d'authentification
  - `test_permissions_logic.py` → Logique de permissions

---

## Équivalent sans mocks (pour comprendre)

```python
def test_whoami_without_authentication_no_mocks():
    """Version sans mocks (NE PAS FAIRE ÇA EN VRAI)."""
    # Créer une VRAIE base de données
    engine = create_engine("sqlite:///test.db")
    Base.metadata.create_all(engine)

    # Créer un VRAI container
    container = Container()

    # VRAIE commande whoami
    auth_service = container.auth_service()
    user = auth_service.get_current_user()

    # Vérification
    assert user is None  # Mais comment garantir qu'il n'y a pas de token ?

    # Nettoyage (facile à oublier !)
    os.remove("test.db")
```

**Problèmes de cette approche** :
- ❌ Lent (I/O disque)
- ❌ Fragile (dépend du système de fichiers)
- ❌ Difficile à contrôler (et si un token existe ?)
- ❌ Nettoyage manuel requis

**Avec mocks (ce qu'on fait)** :
- ✅ Rapide (RAM uniquement)
- ✅ Isolation totale
- ✅ Contrôle exact du comportement
- ✅ Nettoyage automatique

---

## Ressources

### Dans ce projet
- [`tests/unit/test_authentication_commands.py`](../tests/unit/test_authentication_commands.py) - Fichier complet
- [`docs/TESTS_AUTHENTIFICATION.md`](TESTS_AUTHENTIFICATION.md) - Guide complet des tests
- [`docs/PYTEST_MOCK_EXPLAINED.md`](PYTEST_MOCK_EXPLAINED.md) - Explication de pytest-mock

### Documentation externe
- [pytest assertions](https://docs.pytest.org/en/stable/assert.html)
- [Typer testing](https://typer.tiangolo.com/tutorial/testing/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)

---

**Date de création** : 2025-11-17
**Dernière mise à jour** : 2025-11-17
**Version** : 1.0
