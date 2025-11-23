# Comprendre pytest-mock et la fixture `mocker`

## Question : D'où vient `mocker` ?

Quand vous voyez ce code dans les tests :

```python
@pytest.fixture
def mock_user(mocker):
    """Create a mock user for testing."""
    user = mocker.Mock()
    # ...
```

Vous vous demandez peut-être : **"D'où vient `mocker` ?"**

**Réponse courte** : `mocker` est une **fixture automatique** fournie par le plugin **pytest-mock**.

---

## Installation et vérification

### 1. pytest-mock est installé via Poetry

Dans [`pyproject.toml`](../pyproject.toml) :

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^8.4.2"
pytest-mock = "^3.15.1"  # ← Fournit la fixture 'mocker'
pytest-cov = "^7.0.0"
```

### 2. Vérifier l'installation

```bash
# Vérifier que pytest-mock est installé
poetry show pytest-mock

# Sortie attendue :
# name         : pytest-mock
# version      : 3.15.1
# description  : Thin-wrapper around the mock package for easier use with pytest
```

### 3. Voir les fixtures disponibles

```bash
# Lister toutes les fixtures pytest
poetry run pytest --fixtures | grep mocker

# Sortie :
# mocker -- pytest_mock/plugin.py:666
#     Fixture for mocking with pytest-mock
```

---

## Comment fonctionne pytest-mock ?

### Architecture en couches

```
┌─────────────────────────────────────────────────┐
│  Votre test : test_login(mocker)                │
│  "Je demande la fixture 'mocker'"               │
└────────────────┬────────────────────────────────┘
                 │ pytest injecte automatiquement
                 ↓
┌─────────────────────────────────────────────────┐
│  pytest-mock (plugin)                           │
│  Fournit la fixture 'mocker'                    │
│  Code : pytest_mock/plugin.py                   │
└────────────────┬────────────────────────────────┘
                 │ utilise en interne
                 ↓
┌─────────────────────────────────────────────────┐
│  unittest.mock (bibliothèque standard Python)   │
│  Fournit Mock, MagicMock, patch, etc.           │
└─────────────────────────────────────────────────┘
```

### Code source simplifié de pytest-mock

Voici comment pytest-mock définit la fixture `mocker` (version simplifiée) :

```python
# pytest_mock/plugin.py (simplifié pour comprendre)

import pytest
from unittest.mock import Mock, MagicMock, patch

@pytest.fixture
def mocker():
    """
    Fixture qui fournit une interface pratique pour créer des mocks.
    Nettoyage automatique à la fin du test.
    """
    mock_registry = []  # Garde trace de tous les mocks créés

    class MockerFixture:
        """Wrapper autour de unittest.mock avec nettoyage automatique."""

        def Mock(self, *args, **kwargs):
            """Crée un Mock et l'enregistre pour nettoyage."""
            mock = Mock(*args, **kwargs)
            mock_registry.append(mock)
            return mock

        def MagicMock(self, *args, **kwargs):
            """Crée un MagicMock et l'enregistre."""
            mock = MagicMock(*args, **kwargs)
            mock_registry.append(mock)
            return mock

        def patch(self, target, *args, **kwargs):
            """Patch un module/classe/fonction."""
            patcher = patch(target, *args, **kwargs)
            mock = patcher.start()
            mock_registry.append(patcher)
            return mock

    # Crée l'instance de MockerFixture
    mocker_instance = MockerFixture()

    # Donne le mocker au test (yield permet cleanup après)
    yield mocker_instance

    # Après le test : nettoyage automatique
    for item in mock_registry:
        if hasattr(item, 'stop'):
            item.stop()  # Arrête les patches
        elif hasattr(item, 'reset_mock'):
            item.reset_mock()  # Réinitialise les mocks
```

---

## Comparaison : unittest.mock vs pytest-mock

### Ancienne approche (unittest.mock)

```python
from unittest.mock import Mock, patch

def test_login():
    # 1. Import manuel nécessaire
    user = Mock()
    user.username = "admin"

    # 2. Patch manuel
    with patch("src.cli.commands.Container") as mock_container:
        mock_container.return_value = ...
        # Test logic

    # 3. Nettoyage manuel (ou risque de fuite)
    # Pas de nettoyage automatique !
```

**Problèmes** :
- ❌ Import manuel dans chaque fichier
- ❌ Syntaxe verbose (`with patch(...)`)
- ❌ Pas de nettoyage automatique
- ❌ Risque de "fuite de mock" entre tests

### Nouvelle approche (pytest-mock)

```python
# Aucun import nécessaire !

def test_login(mocker):
    # 1. Aucun import, mocker est injecté automatiquement
    user = mocker.Mock()
    user.username = "admin"

    # 2. Patch simplifié
    mock_container = mocker.patch("src.cli.commands.Container")
    mock_container.return_value = ...
    # Test logic

    # 3. Nettoyage automatique à la fin du test !
```

**Avantages** :
- ✅ Aucun import nécessaire
- ✅ Syntaxe concise
- ✅ Nettoyage automatique garanti
- ✅ Isolation totale entre tests

---

## Les 3 concepts clés

### 1. Fixture pytest (`@pytest.fixture`)

Une **fixture** est une fonction qui prépare des données ou objets pour les tests.

```python
@pytest.fixture
def database_connection():
    """Crée une connexion DB pour les tests."""
    conn = create_connection()  # Setup
    yield conn                  # Donne au test
    conn.close()                # Cleanup après test
```

**Utilisation** :
```python
def test_query(database_connection):
    # pytest injecte automatiquement database_connection
    result = database_connection.execute("SELECT * FROM users")
    assert len(result) > 0
```

**Analogie** : Une fixture est comme une "recette" que pytest exécute automatiquement quand un test en a besoin.

### 2. Fixture automatique (fournie par plugin)

Certaines fixtures sont **déjà définies** par pytest ou ses plugins.

**Exemples de fixtures automatiques** :

| Fixture | Fournie par | Description |
|---------|-------------|-------------|
| `tmp_path` | pytest (core) | Crée un répertoire temporaire unique |
| `mocker` | pytest-mock (plugin) | Interface pour créer des mocks |
| `capfd` | pytest (core) | Capture stdout/stderr |
| `monkeypatch` | pytest (core) | Modifie temporairement des attributs |

**Vous n'avez PAS besoin de les définir**, il suffit de les demander en paramètre :

```python
def test_example(mocker, tmp_path, capfd):
    # pytest injecte automatiquement les 3 fixtures !
    user = mocker.Mock()
    file = tmp_path / "test.txt"
    out, err = capfd.readouterr()
```

### 3. Injection de dépendances (Dependency Injection)

Quand vous écrivez :

```python
def test_login(mocker, mock_user):
    # ...
```

pytest fait ceci :

1. **Détecte les paramètres** : `mocker` et `mock_user`
2. **Cherche les fixtures** correspondantes :
   - `mocker` → fournie par pytest-mock
   - `mock_user` → définie dans votre fichier de test
3. **Résout les dépendances** : `mock_user` dépend de `mocker`
4. **Exécute dans l'ordre** :
   ```python
   # Étape 1 : pytest-mock crée mocker
   mocker_instance = MockerFixture()

   # Étape 2 : pytest exécute votre fixture mock_user
   user = mock_user(mocker_instance)

   # Étape 3 : pytest appelle votre test
   test_login(mocker_instance, user)
   ```

---

## Exemple complet avec explications

### Fichier : `tests/unit/test_authentication_commands.py`

```python
import pytest
from typer.testing import CliRunner
from src.cli.commands import app
from src.models.user import Department

# ┌─────────────────────────────────────────────────┐
# │ Étape 1 : Définir une fixture réutilisable      │
# └─────────────────────────────────────────────────┘
@pytest.fixture
def mock_user(mocker):  # ← 'mocker' injecté automatiquement par pytest-mock
    """Create a mock user for testing."""
    user = mocker.Mock()  # ← Crée un mock avec nettoyage automatique
    user.id = 1
    user.username = "admin"
    user.email = "admin@epicevents.com"
    user.first_name = "Alice"
    user.last_name = "Dubois"
    user.phone = "+33 1 23 45 67 89"
    user.department = Department.GESTION
    return user  # ← Retourne le mock configuré

# ┌─────────────────────────────────────────────────┐
# │ Étape 2 : Utiliser la fixture dans un test      │
# └─────────────────────────────────────────────────┘
class TestWhoamiWithAuthentication:
    def test_whoami_with_authentication(self, mocker, mock_user):
        #                                    ^^^^^^  ^^^^^^^^^
        #                                      |         |
        #                      pytest-mock ───┘         └─── votre fixture

        # 'mocker' est disponible pour créer d'autres mocks
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_auth_service = mocker.MagicMock()

        # 'mock_user' est déjà configuré avec toutes les propriétés !
        mock_auth_service.get_current_user.return_value = mock_user
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute command
        runner = CliRunner()
        result = runner.invoke(app, ["whoami"])

        # Verify
        assert result.exit_code == 0
        assert "Alice Dubois" in result.stdout  # ← Utilise mock_user.first_name
        assert "GESTION" in result.stdout       # ← Utilise mock_user.department
```

### Ce qui se passe en coulisses

```python
# Quand pytest exécute test_whoami_with_authentication :

# 1. pytest détecte les paramètres 'mocker' et 'mock_user'
parameters = ['mocker', 'mock_user']

# 2. pytest résout les dépendances
# mocker : fourni par pytest-mock (plugin automatique)
mocker_instance = pytest_mock.plugin.mocker()

# mock_user : défini dans votre fichier, dépend de 'mocker'
user_instance = mock_user(mocker_instance)

# 3. pytest appelle votre test avec les fixtures résolues
test_whoami_with_authentication(
    self=TestWhoamiWithAuthentication(),
    mocker=mocker_instance,
    mock_user=user_instance
)

# 4. Après le test : nettoyage automatique
mocker_instance.cleanup()  # Réinitialise tous les mocks
```

---

## Pourquoi utiliser des Mocks ?

### Scénario : Tester la commande `login`

**Ce qu'on veut tester** :
- ✅ La commande CLI fonctionne
- ✅ Les messages affichés sont corrects
- ✅ Le token est sauvegardé
- ✅ Les erreurs sont gérées

**Ce qu'on NE veut PAS tester** :
- ❌ La vraie base de données
- ❌ La vraie génération de JWT
- ❌ Le vrai système de fichiers

### Option 1 : Sans mocks (❌ mauvaise idée)

```python
def test_login():
    # Nécessite une vraie base de données
    db = create_real_database()
    user = User(username="admin", ...)
    db.add(user)
    db.commit()

    # Nécessite un vrai token JWT
    token = jwt.encode(...)

    # Écrit dans le vrai système de fichiers
    with open(os.path.expanduser("~/.epicevents/token"), "w") as f:
        f.write(token)

    # Test...
```

**Problèmes** :
- ❌ Lent (I/O disque, DB)
- ❌ Fragile (dépend de l'environnement)
- ❌ Difficile à nettoyer
- ❌ Tests interdépendants

### Option 2 : Avec mocks (✅ ce qu'on fait)

```python
def test_login(mocker, mock_user):
    # Mock de la base de données (pas de vraie DB)
    mock_auth_service = mocker.MagicMock()
    mock_auth_service.authenticate.return_value = mock_user

    # Mock du token (pas de vrai JWT)
    mock_auth_service.generate_token.return_value = "fake.jwt.token"

    # Mock du fichier (pas de vrai I/O)
    mock_token_file = tmp_path / "token"  # Fichier temporaire

    # Test de la commande CLI uniquement !
    result = runner.invoke(app, ["login"], input="admin\nAdmin123!\n")
    assert result.exit_code == 0
```

**Avantages** :
- ✅ Ultra-rapide (RAM uniquement)
- ✅ Isolation totale
- ✅ Nettoyage automatique
- ✅ Contrôle total

---

## Mock vs Stub vs Fake vs Spy

### Terminologie des doublures de test

| Type | Description | Exemple |
|------|-------------|---------|
| **Mock** | Objet avec vérification des appels | `mock.method.assert_called_once()` |
| **Stub** | Retourne des valeurs prédéfinies | `stub.get() → "fixed value"` |
| **Fake** | Implémentation simplifiée | `FakeDatabase` avec dict en mémoire |
| **Spy** | Enregistre les appels | `spy.calls → [call1, call2]` |

### Exemples concrets

#### Mock (ce qu'on utilise le plus)

```python
def test_login(mocker):
    mock_auth = mocker.MagicMock()
    mock_auth.authenticate.return_value = User(...)

    # ... test logic

    # VÉRIFICATION des appels
    mock_auth.authenticate.assert_called_once_with("admin", "Admin123!")
    mock_auth.generate_token.assert_called_once()
```

**Quand utiliser ?** Quand vous voulez vérifier COMMENT le code appelle les dépendances.

#### Stub (retour simple)

```python
def test_example():
    stub_auth = StubAuth()
    stub_auth.get_user = lambda: User(username="admin")

    # Pas de vérification, juste retourne une valeur
    user = stub_auth.get_user()
    assert user.username == "admin"
```

**Quand utiliser ?** Quand vous ne vous souciez pas des appels, juste du résultat.

#### Fake (implémentation simplifiée)

```python
class FakeUserRepository:
    """Fake repository using in-memory dict."""
    def __init__(self):
        self.users = {}

    def add(self, user):
        self.users[user.id] = user

    def get(self, user_id):
        return self.users.get(user_id)

def test_user_service():
    fake_repo = FakeUserRepository()
    service = UserService(fake_repo)

    service.create_user("admin", "admin@example.com")
    user = service.get_user(1)
    assert user.username == "admin"
```

**Quand utiliser ?** Quand vous voulez une vraie logique mais sans dépendances externes.

#### Spy (enregistrement des appels)

```python
def test_with_spy(mocker):
    spy_function = mocker.spy(MyClass, 'method')

    obj = MyClass()
    obj.method("arg1")
    obj.method("arg2")

    # Vérifier que la méthode a été appelée 2 fois
    assert spy_function.call_count == 2
    assert spy_function.call_args_list == [
        mocker.call("arg1"),
        mocker.call("arg2")
    ]
```

**Quand utiliser ?** Quand vous voulez observer les appels SANS modifier le comportement.

---

## FAQ

### Q1 : Pourquoi pas juste `from unittest.mock import Mock` ?

**Réponse** : Vous pouvez, mais vous perdez les avantages de pytest-mock :

```python
# ❌ Ancienne approche
from unittest.mock import Mock, patch

def test_login():
    with patch("src.cli.commands.Container") as mock_container:
        user = Mock()
        # ... test logic
    # Risque de fuite si exception levée avant 'with' termine

# ✅ Nouvelle approche
def test_login(mocker):
    mock_container = mocker.patch("src.cli.commands.Container")
    user = mocker.Mock()
    # ... test logic
    # Nettoyage GARANTI même si exception
```

### Q2 : Puis-je utiliser `mocker` sans créer de fixture ?

**Oui** ! `mocker` peut être utilisé directement :

```python
def test_example(mocker):
    # Utilisation directe, pas de fixture intermédiaire
    user = mocker.Mock()
    user.username = "admin"

    mock_service = mocker.patch("src.services.UserService")
    # ... test logic
```

**Quand créer une fixture ?** Quand vous réutilisez le même setup dans plusieurs tests.

### Q3 : Comment tester plusieurs scénarios avec le même mock ?

**Solution 1** : Paramétrer la fixture

```python
@pytest.fixture
def mock_user(mocker, request):
    """Create mock user with custom username."""
    user = mocker.Mock()
    user.username = request.param if hasattr(request, 'param') else "admin"
    return user

@pytest.mark.parametrize('mock_user', ['alice', 'bob'], indirect=True)
def test_login(mock_user):
    # Test sera exécuté 2 fois : avec 'alice' et 'bob'
    assert mock_user.username in ['alice', 'bob']
```

**Solution 2** : Créer le mock directement dans le test

```python
def test_login_multiple_users(mocker):
    for username in ['alice', 'bob', 'charlie']:
        user = mocker.Mock()
        user.username = username
        # ... test logic with this user
```

### Q4 : Différence entre `Mock()` et `MagicMock()` ?

```python
def test_difference(mocker):
    # Mock : basique
    mock = mocker.Mock()
    mock.method()  # OK
    len(mock)      # ❌ TypeError: object of type 'Mock' has no len()

    # MagicMock : avec méthodes magiques
    magic_mock = mocker.MagicMock()
    magic_mock.method()  # OK
    len(magic_mock)      # ✅ OK, retourne 0 par défaut
    str(magic_mock)      # ✅ OK
    magic_mock[0]        # ✅ OK
```

**Règle** : Utilisez `MagicMock` si vous voulez supporter `len()`, `str()`, `[]`, etc.

### Q5 : Comment voir tous les appels sur un mock ?

```python
def test_debug_calls(mocker):
    mock_service = mocker.MagicMock()

    # Faire des appels
    mock_service.create_user("alice")
    mock_service.create_user("bob")
    mock_service.delete_user(1)

    # Inspecter les appels
    print(mock_service.method_calls)
    # Sortie :
    # [call.create_user('alice'),
    #  call.create_user('bob'),
    #  call.delete_user(1)]

    # Vérifier un appel spécifique
    mock_service.create_user.assert_any_call("alice")
    assert mock_service.create_user.call_count == 2
```

---

## Ressources

### Documentation officielle
- [pytest-mock documentation](https://pytest-mock.readthedocs.io/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
- [pytest fixtures guide](https://docs.pytest.org/en/stable/fixture.html)

### Dans ce projet
- [`tests/unit/test_authentication_commands.py`](../tests/unit/test_authentication_commands.py) - Exemples d'utilisation de mocker
- [`tests/unit/test_permissions_logic.py`](../tests/unit/test_permissions_logic.py) - Mocks pour tester les permissions
- [`docs/TESTS_AUTHENTIFICATION.md`](TESTS_AUTHENTIFICATION.md) - Guide complet des tests

---

## Résumé en 5 points

1. **`mocker` vient de pytest-mock** : Un plugin pytest installé via `poetry add --group dev pytest-mock`

2. **C'est une fixture automatique** : Pas besoin de la définir, pytest l'injecte automatiquement quand vous écrivez `def test(mocker):`

3. **Wrapper autour de unittest.mock** : `mocker.Mock()` ≈ `unittest.mock.Mock()` mais avec nettoyage automatique

4. **Isolation garantie** : Chaque test reçoit un nouveau `mocker`, impossible d'avoir des "fuites" entre tests

5. **Syntaxe plus simple** : `mocker.patch()` au lieu de `with patch() as mock:`, moins de boilerplate

---

**Date de création** : 2025-11-17
**Dernière mise à jour** : 2025-11-17
**Version** : 1.0
