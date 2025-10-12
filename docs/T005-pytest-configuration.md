# T005: Configuration de pytest et coverage

## Description
Configuration du fichier `pytest.ini` avec les paramètres de couverture de code et découverte des tests pour le projet Epic Events CRM.

## Contexte
Cette tâche fait partie de la phase de configuration initiale du projet (Phase 3.1: Setup & Project Initialization). Elle peut être exécutée en parallèle avec d'autres tâches de configuration (T003, T004, T006) une fois que Poetry a été initialisé (T002).

## Objectif
Mettre en place la configuration pytest qui permettra :
- La découverte automatique des tests
- Le calcul de la couverture de code
- L'échec de la build si la couverture est inférieure à 80%
- La génération de rapports de couverture lisibles

## Fichier créé
`pytest.ini` (à la racine du projet)

## Contenu du fichier

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    -v
```

## Explications des paramètres

### Discovery (Découverte des tests)
- **testpaths = tests** : Indique à pytest de chercher les tests uniquement dans le répertoire `tests/`
- **python_files = test_*.py** : Découvre tous les fichiers commençant par `test_`
- **python_classes = Test*** : Découvre toutes les classes commençant par `Test`
- **python_functions = test_*** : Découvre toutes les fonctions commençant par `test_`

### Coverage (Couverture de code)
- **--cov=src** : Mesure la couverture du code dans le répertoire `src/`
- **--cov-report=html** : Génère un rapport HTML détaillé dans `htmlcov/`
- **--cov-report=term-missing** : Affiche dans le terminal les lignes non couvertes
- **--cov-fail-under=80** : Fait échouer la commande pytest si la couverture est < 80%

### Options générales
- **-v** : Mode verbose pour afficher plus de détails lors de l'exécution

## Dépendances
- **T002** : Initialisation de Python avec Poetry (pytest doit être installé)

## Critères de complétion
✅ Le fichier `pytest.ini` existe à la racine du projet
✅ La commande `pytest` s'exécute avec succès (même avec 0 tests collectés)
✅ Le message affiché confirme la configuration (testpaths, coverage settings)

## Commande de test

```bash
poetry run pytest
```

**Sortie attendue (sur projet vide)** :
```
============================= test session starts ==============================
platform win32 -- Python 3.13.x, pytest-x.x.x, pluggy-x.x.x
rootdir: d:\...\project-12-architecture-back-end
configfile: pytest.ini
testpaths: tests
plugins: cov-x.x.x
collected 0 items

---------- coverage: platform win32, python 3.13.x-final-0 ----------
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
TOTAL                       0      0   100%

============================== 0 passed in 0.01s ===============================
```

## Utilisation future

### Exécuter tous les tests
```bash
pytest
```

### Exécuter avec rapport de couverture détaillé
```bash
pytest --cov=src --cov-report=html
# Ouvrir htmlcov/index.html dans le navigateur
```

### Exécuter un fichier de test spécifique
```bash
pytest tests/contract/test_auth_commands.py
```

### Exécuter un test spécifique
```bash
pytest tests/contract/test_auth_commands.py::test_login_contract_success
```

### Mode verbose avec détails
```bash
pytest -vv
```

## Objectifs de couverture

### Couverture globale
- **Minimum requis** : 80% (--cov-fail-under=80)
- **Cible** : >85% pour tous les modules

### Couverture critique (100% requis)
- `src/services/auth_service.py` : Authentification JWT
- `src/services/permission_service.py` : Logique des permissions

### Fichiers exclus de la couverture
- `migrations/` : Fichiers Alembic (auto-générés)
- `tests/` : Les tests ne testent pas les tests
- `src/config.py` : Configuration simple (pas de logique métier)

## Prochaines étapes
Une fois cette tâche complétée, vous pourrez :
1. **T007-T011** : Écrire les tests de contrat (contract tests)
2. **T012-T019** : Écrire les tests d'intégration
3. **T020** : Créer les fixtures pytest dans `conftest.py`

## Notes importantes
- **TDD** : Les tests (T007-T020) doivent TOUS échouer avant de commencer l'implémentation (T021+)
- **Ordre d'exécution** : Cette configuration doit être en place avant d'écrire les tests
- **Parallélisation** : Cette tâche peut être exécutée en même temps que T003 (linting), T004 (Alembic), T006 (.env.example)

## Statut
✅ **Complétée** - Le fichier pytest.ini est configuré et opérationnel