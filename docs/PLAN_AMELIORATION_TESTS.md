# Plan d'amélioration de la couverture de tests

**État actuel** : 44.54% de couverture
**Objectif** : 80% de couverture
**Gap** : +35.46 points

---

## 🎯 Priorités pour atteindre 80%

### Priorité 1 : Services (Logique métier critique)

#### Services à tester en priorité :
1. **client_service.py** (30% → 80%)
   - `create_client()` : validation + auto-assignation
   - `update_client()` : permissions granulaires
   - `get_client()` : récupération basique

2. **contract_service.py** (44% → 80%)
   - `create_contract()` : validation montants
   - `update_contract()` : logique métier déjà testée en CLI
   - `get_unpaid_contracts()` : filtre métier

3. **event_service.py** (39% → 80%)
   - `create_event()` : validation dates
   - `get_events_by_support_contact()` : filtre support
   - `get_unassigned_events()` : filtre gestion

4. **user_service.py** (57% → 80%)
   - `create_user()` : hashing bcrypt
   - `get_user_by_username()` : authentification

**Impact estimé** : +15 points de couverture

---

### Priorité 2 : Repositories SQLAlchemy

#### Repositories à tester :
1. **sqlalchemy_user_repository.py** (59% → 80%)
   - `create()` : insertion DB
   - `get_by_username()` : requête unique
   - `get_by_email()` : contrainte unicité

2. **sqlalchemy_contract_repository.py** (48% → 80%)
   - `create()` : relations client
   - `get_unsigned_contracts()` : filtre WHERE
   - `get_unpaid_contracts()` : filtre montants

3. **sqlalchemy_event_repository.py** (47% → 80%)
   - `create()` : relations contract
   - `get_by_support_contact()` : filtre support
   - `get_unassigned()` : filtre NULL

**Impact estimé** : +10 points de couverture

**Approche** : Tests d'intégration avec base de données en mémoire (SQLite)

---

### Priorité 3 : Validators (Sécurité)

#### Validators critiques :
1. **validate_email()** : Regex email
2. **validate_phone()** : Format téléphone français
3. **validate_password()** : Politique mots de passe
4. **validate_amount()** : Montants positifs
5. **validate_date()** : Dates futures

**Impact estimé** : +5 points de couverture

---

### Priorité 4 (optionnel) : CLI Commands

**Note** : Les commandes CLI sont complexes à tester (Typer prompts).
Focus sur les chemins critiques seulement :
- `create_user` : Hashing password
- `create_client` : Auto-assignation déjà testée indirectement
- Filtres : Logique métier dans services (déjà couverts si Priorité 1 faite)

**Impact estimé** : +5 points de couverture (optionnel)

---

## 📋 Plan d'action recommandé

### Phase 1 : Services (Semaine 1)
```bash
# Créer tests/unit/test_client_service.py
# Créer tests/unit/test_contract_service.py
# Créer tests/unit/test_event_service.py
# Compléter tests/unit/test_user_service.py
```

**Objectif** : 60% de couverture totale

### Phase 2 : Repositories (Semaine 2)
```bash
# Créer tests/integration/test_sqlalchemy_repositories.py
# Tests avec SQLite in-memory
```

**Objectif** : 70% de couverture totale

### Phase 3 : Validators (Semaine 2)
```bash
# Créer tests/unit/test_validators.py
# Tests de regex et validations
```

**Objectif** : 75-80% de couverture totale

---

## 🔧 Stratégie de tests

### Tests unitaires (Services)
```python
# Exemple : test_client_service.py
def test_create_client_with_auto_assignation(mocker):
    # Mock repository
    mock_repo = mocker.Mock()
    mock_repo.create.return_value = client

    # Test service
    service = ClientService(mock_repo)
    result = service.create_client(
        first_name="Jean",
        sales_contact_id=0,  # Auto-assignation
        current_user_id=2
    )

    # Vérifier auto-assignation
    assert mock_repo.create.called
    assert result.sales_contact_id == 2
```

### Tests d'intégration (Repositories)
```python
# Exemple : test_sqlalchemy_repositories.py
@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

def test_user_repository_create(in_memory_db):
    repo = SQLAlchemyUserRepository(in_memory_db)
    user = repo.create(
        username="test",
        email="test@example.com",
        password_hash="..."
    )
    assert user.id is not None
```

### Tests validators
```python
# Exemple : test_validators.py
def test_validate_email_valid():
    assert validate_email("user@example.com") == True

def test_validate_email_invalid():
    with pytest.raises(ValueError):
        validate_email("invalid-email")
```

---

## 📊 Suivi de progression

| Phase | Cible | Couverture | Statut |
|-------|-------|------------|--------|
| Initial | - | 44.54% | ✅ Actuel |
| Phase 1 (Services) | 60% | - | ⏳ À faire |
| Phase 2 (Repositories) | 70% | - | ⏳ À faire |
| Phase 3 (Validators) | 80% | - | ⏳ À faire |

---

## ✅ Conformité OpenClassrooms

### Déjà conforme ✅
- [x] Architecture Clean (Repository, DI, Layers)
- [x] Design patterns (Repository, Factory, Decorator)
- [x] PEP8 et formatage (black, flake8)
- [x] Documentation (docstrings, type hints)
- [x] Sécurité (SQLAlchemy ORM, JWT, bcrypt, RBAC)
- [x] Tests CLI authentification et permissions

### À compléter ⚠️
- [ ] **Couverture 80%** (actuellement 44.54%)
  - Services : 39-57% → 80%
  - Repositories : 47-59% → 80%
  - Validators : 26% → 80%

---

**Date de création** : 2025-11-17
**Dernière mise à jour** : 2025-11-17
**Version** : 1.0
