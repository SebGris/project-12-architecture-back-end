# Tests d'Authentification CLI

## Vue d'ensemble

Ce document explique les tests automatisés pour les commandes d'authentification du CRM Epic Events (`login`, `logout`, `whoami`).

**Fichier de tests** : [`tests/unit/test_authentication_commands.py`](../tests/unit/test_authentication_commands.py)

**Couverture** : 8 tests couvrant tous les scénarios d'authentification de la section "2. Démonstration - Authentification" de [SOUTENANCE.md](oc/SOUTENANCE.md).

---

## Technologies utilisées

### pytest-mock
Les tests utilisent `pytest-mock` au lieu de `unittest.mock` pour une meilleure intégration avec pytest :

```python
# ❌ Ancienne approche (unittest.mock)
from unittest.mock import Mock, patch
with patch("src.cli.commands.Container") as mock_container:
    user = Mock(spec=User)

# ✅ Nouvelle approche (pytest-mock)
def test_example(mocker):
    mock_container = mocker.patch("src.cli.commands.Container")
    user = mocker.Mock(spec=User)
```

**Avantages** :
- Nettoyage automatique des mocks après chaque test
- Syntaxe plus simple et cohérente avec pytest
- Meilleure intégration avec les fixtures

### CliRunner (Typer)
Permet de tester les commandes CLI comme si elles étaient exécutées dans un terminal :

```python
from typer.testing import CliRunner
from src.cli.commands import app

runner = CliRunner()
result = runner.invoke(app, ["login"], input="admin\nAdmin123!\n")
```

---

## Fixtures partagées

### mock_user
Crée un utilisateur fictif du département GESTION pour les tests :

```python
@pytest.fixture
def mock_user(mocker):
    """Create a mock user for testing."""
    user = mocker.Mock()
    user.id = 1
    user.username = "admin"
    user.email = "admin@epicevents.com"
    user.first_name = "Alice"
    user.last_name = "Dubois"
    user.phone = "+33 1 23 45 67 89"
    user.department = Department.GESTION
    return user
```

**Pourquoi un Mock ?** On ne teste pas la création d'utilisateur ici, mais le comportement des commandes CLI.

### mock_token_file
Crée un fichier de token temporaire dans un répertoire isolé :

```python
@pytest.fixture
def mock_token_file(tmp_path):
    """Create a temporary token file for testing."""
    token_dir = tmp_path / ".epicevents"
    token_dir.mkdir(exist_ok=True)
    token_file = token_dir / "token"
    return token_file
```

**Avantages** :
- `tmp_path` est une fixture pytest qui crée un répertoire temporaire unique
- Nettoyage automatique après le test
- Isolation complète (pas d'interférence avec le vrai fichier token)

---

## Tests détaillés

### 1. TestWhoamiWithoutAuthentication

#### test_whoami_without_authentication

**Scénario** : Un utilisateur non authentifié essaie d'exécuter `whoami`

**Comportement attendu** :
- Code de sortie : 1 (erreur)
- Message affiché : "Vous n'êtes pas connecté" et "epicevents login"

**Code simplifié** :
```python
def test_whoami_without_authentication(self, mocker):
    # 1. Mock du container de dépendances
    mock_container = mocker.patch("src.cli.commands.Container")

    # 2. Mock de auth_service qui retourne None (pas d'utilisateur)
    mock_auth_service = mocker.MagicMock()
    mock_auth_service.get_current_user.return_value = None
    mock_container.return_value.auth_service.return_value = mock_auth_service

    # 3. Exécution de la commande
    result = runner.invoke(app, ["whoami"])

    # 4. Vérifications
    assert result.exit_code == 1
    assert "Vous n'êtes pas connecté" in result.stdout
    assert "epicevents login" in result.stdout
```

**Pourquoi mocker Container ?**
- Permet d'injecter un faux `auth_service` sans toucher à la base de données
- Isolation totale du test

---

### 2. TestLoginCommand

#### test_login_with_valid_credentials

**Scénario** : Login avec des credentials valides

**Flux testé** :
1. L'utilisateur entre `admin` / `Admin123!`
2. `auth_service.authenticate()` retourne un utilisateur valide
3. `auth_service.generate_token()` génère un JWT
4. `auth_service.save_token()` sauvegarde le token dans le fichier
5. Message de bienvenue affiché

**Code simplifié** :
```python
def test_login_with_valid_credentials(self, mocker, mock_user, mock_token_file):
    # 1. Setup des mocks
    mock_container = mocker.patch("src.cli.commands.Container")
    mock_auth_service = mocker.MagicMock()

    # Simulate successful authentication
    mock_auth_service.authenticate.return_value = mock_user
    mock_auth_service.generate_token.return_value = "fake.jwt.token"
    mock_auth_service.TOKEN_FILE = mock_token_file

    # Mock save_token pour écrire dans notre fichier temporaire
    def save_token_mock(token):
        mock_token_file.write_text(token)
    mock_auth_service.save_token.side_effect = save_token_mock

    mock_container.return_value.auth_service.return_value = mock_auth_service
    mocker.patch("src.sentry_config.set_user_context")

    # 2. Exécution avec input simulé
    result = runner.invoke(app, ["login"], input="admin\nAdmin123!\n")

    # 3. Vérifications
    mock_auth_service.authenticate.assert_called_once_with("admin", "Admin123!")
    mock_auth_service.generate_token.assert_called_once_with(mock_user)
    mock_auth_service.save_token.assert_called_once_with("fake.jwt.token")

    assert result.exit_code == 0
    assert "Bienvenue Alice Dubois" in result.stdout
    assert "GESTION" in result.stdout
    assert "Valide pour 24 heures" in result.stdout
```

**Points clés** :
- `input="admin\nAdmin123!\n"` simule la saisie interactive
- `side_effect` permet d'exécuter une vraie action (écrire dans le fichier)
- On vérifie à la fois les appels de méthodes ET l'affichage

#### test_login_with_invalid_credentials

**Scénario** : Login avec un mauvais mot de passe

**Comportement attendu** :
- `auth_service.authenticate()` retourne `None`
- Code de sortie : 1
- Message d'erreur affiché

**Code simplifié** :
```python
def test_login_with_invalid_credentials(self, mocker):
    mock_container = mocker.patch("src.cli.commands.Container")
    mock_auth_service = mocker.MagicMock()

    # Simulate failed authentication
    mock_auth_service.authenticate.return_value = None
    mock_container.return_value.auth_service.return_value = mock_auth_service

    result = runner.invoke(app, ["login"], input="admin\nWrongPassword123!\n")

    assert result.exit_code == 1
    assert "Nom d'utilisateur ou mot de passe incorrect" in result.stdout
```

---

### 3. TestTokenStorage

#### test_token_saved_to_file

**Scénario** : Vérifier que le token JWT est bien sauvegardé dans le fichier système

**Ce qu'on teste** :
1. Le fichier `~/.epicevents/token` est créé
2. Le contenu est le JWT généré (format correct)

**Code simplifié** :
```python
def test_token_saved_to_file(self, mocker, mock_user, mock_token_file):
    mock_container = mocker.patch("src.cli.commands.Container")
    mock_auth_service = mocker.MagicMock()

    mock_auth_service.authenticate.return_value = mock_user
    mock_auth_service.generate_token.return_value = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.fake_signature"
    )
    mock_auth_service.TOKEN_FILE = mock_token_file

    # Simulate token file creation
    def save_token_mock(token):
        mock_token_file.write_text(token)
    mock_auth_service.save_token.side_effect = save_token_mock

    mock_container.return_value.auth_service.return_value = mock_auth_service
    mocker.patch("src.sentry_config.set_user_context")

    # Execute login
    result = runner.invoke(app, ["login"], input="admin\nAdmin123!\n")

    # Verify file exists and contains token
    assert mock_token_file.exists()
    token_content = mock_token_file.read_text()
    assert token_content == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.fake_signature"
```

**Note sur les permissions** :
- Les permissions Unix 0o600 (lecture/écriture propriétaire uniquement) sont expliquées dans [TOKEN_STORAGE.md](TOKEN_STORAGE.md)
- Ce test ne vérifie plus les permissions (simplifié pour compatibilité Windows/Unix)

---

### 4. TestWhoamiWithAuthentication

#### test_whoami_with_authentication

**Scénario** : Un utilisateur authentifié exécute `whoami`

**Comportement attendu** :
- Affiche les informations de l'utilisateur (nom, email, département)
- Code de sortie : 0 (succès)

**Code simplifié** :
```python
def test_whoami_with_authentication(self, mocker, mock_user):
    mock_container = mocker.patch("src.cli.commands.Container")
    mock_auth_service = mocker.MagicMock()

    # Simulate authenticated user
    mock_auth_service.get_current_user.return_value = mock_user
    mock_container.return_value.auth_service.return_value = mock_auth_service

    result = runner.invoke(app, ["whoami"])

    assert result.exit_code == 0
    assert "admin" in result.stdout
    assert "Alice Dubois" in result.stdout
    assert "admin@epicevents.com" in result.stdout
    assert "GESTION" in result.stdout
```

---

### 5. TestLogoutCommand

#### test_logout_deletes_token

**Scénario** : Un utilisateur authentifié se déconnecte

**Flux testé** :
1. Un fichier token existe (créé au préalable)
2. L'utilisateur exécute `logout`
3. `auth_service.delete_token()` supprime le fichier
4. Message d'au revoir affiché

**Code simplifié** :
```python
def test_logout_deletes_token(self, mocker, mock_user, mock_token_file):
    # Create a fake token file
    mock_token_file.write_text("fake.jwt.token")
    assert mock_token_file.exists()

    mock_container = mocker.patch("src.cli.commands.Container")
    mock_auth_service = mocker.MagicMock()
    mock_auth_service.get_current_user.return_value = mock_user
    mock_auth_service.TOKEN_FILE = mock_token_file

    # Simulate token deletion
    def delete_token_mock():
        if mock_token_file.exists():
            mock_token_file.unlink()
    mock_auth_service.delete_token.side_effect = delete_token_mock

    mock_container.return_value.auth_service.return_value = mock_auth_service
    mocker.patch("src.sentry_config.clear_user_context")
    mocker.patch("src.sentry_config.add_breadcrumb")

    # Execute logout
    result = runner.invoke(app, ["logout"])

    assert result.exit_code == 0
    assert "Au revoir Alice Dubois" in result.stdout
    mock_auth_service.delete_token.assert_called_once()
    assert not mock_token_file.exists()  # File deleted!
```

**Pourquoi `side_effect` ?**
- Permet de simuler l'action réelle de suppression du fichier
- On peut vérifier que le fichier n'existe plus après le test

#### test_logout_without_authentication

**Scénario** : Un utilisateur non authentifié essaie de se déconnecter

**Comportement attendu** :
- Code de sortie : 1 (erreur)
- Message d'erreur : "Vous n'êtes pas connecté"

**Code simplifié** :
```python
def test_logout_without_authentication(self, mocker):
    mock_container = mocker.patch("src.cli.commands.Container")
    mock_auth_service = mocker.MagicMock()

    # No authenticated user
    mock_auth_service.get_current_user.return_value = None
    mock_container.return_value.auth_service.return_value = mock_auth_service

    result = runner.invoke(app, ["logout"])

    assert result.exit_code == 1
    assert "Vous n'êtes pas connecté" in result.stdout
```

---

### 6. TestAuthenticationFlow

#### test_complete_authentication_flow

**Scénario** : Flux complet login → whoami → logout

**Ce test est CRITIQUE** car il valide l'ensemble du cycle d'authentification tel qu'il sera démontré lors de la soutenance.

**Flux testé** :
1. **Login** : Génération et sauvegarde du token
2. **Whoami** : Vérification que l'utilisateur est authentifié
3. **Logout** : Suppression du token et déconnexion

**Code simplifié** :
```python
def test_complete_authentication_flow(self, mocker, mock_user, mock_token_file):
    mock_container = mocker.patch("src.cli.commands.Container")
    mock_auth_service = mocker.MagicMock()
    mock_auth_service.TOKEN_FILE = mock_token_file

    # Helper functions
    def save_token_mock(token):
        mock_token_file.write_text(token)

    def delete_token_mock():
        if mock_token_file.exists():
            mock_token_file.unlink()

    mock_auth_service.save_token.side_effect = save_token_mock
    mock_auth_service.delete_token.side_effect = delete_token_mock
    mock_container.return_value.auth_service.return_value = mock_auth_service

    # Mock Sentry
    mocker.patch("src.sentry_config.set_user_context")
    mocker.patch("src.sentry_config.clear_user_context")
    mocker.patch("src.sentry_config.add_breadcrumb")

    # Step 1: Login
    mock_auth_service.authenticate.return_value = mock_user
    mock_auth_service.generate_token.return_value = "fake.jwt.token"

    result = runner.invoke(app, ["login"], input="admin\nAdmin123!\n")
    assert result.exit_code == 0
    assert mock_token_file.exists()  # Token created ✓

    # Step 2: Whoami (authenticated)
    mock_auth_service.get_current_user.return_value = mock_user

    result = runner.invoke(app, ["whoami"])
    assert result.exit_code == 0
    assert "Alice Dubois" in result.stdout  # User info displayed ✓

    # Step 3: Logout
    result = runner.invoke(app, ["logout"])
    assert result.exit_code == 0
    assert not mock_token_file.exists()  # Token deleted ✓
```

**Pourquoi ce test est important ?**
- Simule exactement ce qui se passera lors de la démonstration
- Valide que les 3 commandes fonctionnent ensemble
- Vérifie la persistance du token entre les commandes

---

## Concepts clés pour comprendre les tests

### 1. Mock vs Stub vs Fake

**Mock** (ce qu'on utilise ici) :
```python
mock_auth_service = mocker.MagicMock()
mock_auth_service.authenticate.return_value = mock_user
# On peut vérifier les appels :
mock_auth_service.authenticate.assert_called_once_with("admin", "Admin123!")
```

**Stub** (retour prédéfini sans vérification) :
```python
def authenticate_stub(username, password):
    return mock_user
```

**Fake** (implémentation simplifiée) :
```python
class FakeAuthService:
    def authenticate(self, username, password):
        if username == "admin" and password == "Admin123!":
            return User(...)
```

**Pourquoi Mock ?** On peut vérifier COMMENT les méthodes sont appelées, pas seulement le résultat.

### 2. return_value vs side_effect

**return_value** : Retourne toujours la même valeur
```python
mock_auth_service.get_current_user.return_value = mock_user
# Chaque appel retourne mock_user
```

**side_effect** : Exécute une fonction ou retourne des valeurs différentes
```python
# Fonction custom
mock_auth_service.save_token.side_effect = save_token_mock

# Valeurs différentes à chaque appel
mock_auth_service.get_current_user.side_effect = [None, mock_user, None]
```

### 3. Patch vs Mock

**Patch** : Remplace un module/classe/fonction dans le code
```python
mocker.patch("src.cli.commands.Container")
# Remplace Container dans le module commands
```

**Mock** : Crée un objet fictif
```python
user = mocker.Mock(spec=User)
# Crée un objet qui ressemble à User
```

### 4. Pourquoi tester les commandes CLI ?

**Alternative : tester uniquement les services**
```python
def test_auth_service_authenticate():
    service = AuthService(...)
    user = service.authenticate("admin", "Admin123!")
    assert user is not None
```

**Problème** : On ne teste pas l'interface CLI !
- Erreurs de typage dans les commandes Typer
- Erreurs de validation des entrées
- Erreurs d'affichage des messages

**Solution : tester les commandes** (ce qu'on fait ici)
```python
result = runner.invoke(app, ["login"], input="admin\nAdmin123!\n")
assert "Bienvenue Alice Dubois" in result.stdout
```

On valide :
- ✅ La commande existe et fonctionne
- ✅ Les entrées sont correctement validées
- ✅ Les messages affichés sont corrects
- ✅ Les codes de sortie sont appropriés

---

## Exécution des tests

### Lancer uniquement les tests d'authentification
```bash
poetry run pytest tests/unit/test_authentication_commands.py -v
```

### Lancer avec couverture de code
```bash
poetry run pytest tests/unit/test_authentication_commands.py --cov=src.cli.commands --cov-report=html
```

### Lancer un seul test
```bash
poetry run pytest tests/unit/test_authentication_commands.py::TestLoginCommand::test_login_with_valid_credentials -v
```

### Résultat attendu
```
tests/unit/test_authentication_commands.py::TestWhoamiWithoutAuthentication::test_whoami_without_authentication PASSED
tests/unit/test_authentication_commands.py::TestLoginCommand::test_login_with_valid_credentials PASSED
tests/unit/test_authentication_commands.py::TestLoginCommand::test_login_with_invalid_credentials PASSED
tests/unit/test_authentication_commands.py::TestTokenStorage::test_token_saved_to_file PASSED
tests/unit/test_authentication_commands.py::TestWhoamiWithAuthentication::test_whoami_with_authentication PASSED
tests/unit/test_authentication_commands.py::TestLogoutCommand::test_logout_deletes_token PASSED
tests/unit/test_authentication_commands.py::TestLogoutCommand::test_logout_without_authentication PASSED
tests/unit/test_authentication_commands.py::TestAuthenticationFlow::test_complete_authentication_flow PASSED

============================== 8 passed in 1.50s ==============================
```

---

## Maintenance et évolution

### Ajouter un nouveau test

**Exemple** : Tester l'expiration du token

```python
class TestTokenExpiration:
    """Test JWT token expiration."""

    def test_whoami_with_expired_token(self, mocker, mock_token_file):
        """
        GIVEN an expired JWT token
        WHEN whoami command is executed
        THEN it should display an error message
        """
        # Create expired token
        mock_token_file.write_text("expired.jwt.token")

        mock_container = mocker.patch("src.cli.commands.Container")
        mock_auth_service = mocker.MagicMock()

        # Simulate expired token
        mock_auth_service.get_current_user.return_value = None
        mock_container.return_value.auth_service.return_value = mock_auth_service

        result = runner.invoke(app, ["whoami"])

        assert result.exit_code == 1
        assert "Token expiré" in result.stdout
```

### Refactoring des fixtures

Si plusieurs tests utilisent le même setup, créez une fixture :

```python
@pytest.fixture
def authenticated_user_setup(mocker, mock_user, mock_token_file):
    """Setup an authenticated user with a valid token."""
    mock_token_file.write_text("fake.jwt.token")

    mock_container = mocker.patch("src.cli.commands.Container")
    mock_auth_service = mocker.MagicMock()
    mock_auth_service.get_current_user.return_value = mock_user
    mock_auth_service.TOKEN_FILE = mock_token_file
    mock_container.return_value.auth_service.return_value = mock_auth_service

    return mock_auth_service

# Utilisation
def test_whoami_with_authentication(authenticated_user_setup):
    result = runner.invoke(app, ["whoami"])
    assert result.exit_code == 0
```

---

## Correspondance avec SOUTENANCE.md

Ces tests valident automatiquement la section **"2. Démonstration - Authentification (3 minutes)"** :

| Étape SOUTENANCE.md | Test correspondant |
|---------------------|-------------------|
| ✅ `epicevents login` avec credentials valides | `test_login_with_valid_credentials` |
| ✅ Token JWT sauvegardé dans `~/.epicevents/token` | `test_token_saved_to_file` |
| ✅ `epicevents whoami` affiche les infos utilisateur | `test_whoami_with_authentication` |
| ✅ `epicevents logout` supprime le token | `test_logout_deletes_token` |
| ✅ `epicevents whoami` échoue après logout | `test_whoami_without_authentication` |
| ✅ Login avec mauvais credentials échoue | `test_login_with_invalid_credentials` |
| ✅ Flux complet login → whoami → logout | `test_complete_authentication_flow` |

**Avantage** : Si un test échoue, on sait immédiatement quelle partie de la démo est cassée !

---

## Ressources complémentaires

- [pytest-mock documentation](https://pytest-mock.readthedocs.io/)
- [Typer Testing documentation](https://typer.tiangolo.com/tutorial/testing/)
- [TOKEN_STORAGE.md](TOKEN_STORAGE.md) - Explication du stockage sécurisé des tokens
- [SOUTENANCE.md](oc/SOUTENANCE.md) - Guide de présentation du projet

---

**Date de création** : 2025-11-17
**Dernière mise à jour** : 2025-11-17
**Version** : 1.0
