# Changements : Séparation des noms et ajout du téléphone

**Date** : 2025-10-11
**Auteur** : Projet Epic Events CRM
**Type** : Conception des modèles de données

---

## Contexte

Lors de la conception initiale des modèles `User` et `Client`, un seul champ `full_name` était utilisé pour stocker le nom complet des personnes. Cette approche présentait plusieurs limitations :

1. **Impossibilité de trier par nom de famille** séparément du prénom
2. **Difficultés pour les recherches** (chercher tous les "Smith" par exemple)
3. **Problèmes d'internationalisation** (ordre prénom/nom varie selon les cultures)
4. **Manque de granularité** pour les formulaires et validations

De plus, le modèle `User` n'avait pas de champ téléphone, contrairement au modèle `Client`, ce qui créait une asymétrie dans la structure des données.

---

## Problèmes identifiés

### 1. Champ `full_name` dans User et Client

**Avant :**
```python
# User et Client
full_name: Mapped[str] = mapped_column(String(100), nullable=False)
```

**Problèmes :**
- Impossible de séparer prénom et nom pour le tri ou l'affichage
- Validation complexe (comment vérifier qu'il y a bien un prénom ET un nom ?)
- Format libre pouvant contenir des erreurs de saisie
- Pas de cohérence avec les standards de l'industrie (la plupart des systèmes séparent first_name/last_name)

### 2. Absence de champ `phone` dans User

**Problème :**
- Incohérence : Client a un champ `phone`, mais pas User
- Impossibilité de contacter les collaborateurs par téléphone
- Manque d'informations pour les rapports et annuaires internes

---

## Solutions mises en œuvre

### Solution 1 : Séparation de `full_name` en `first_name` et `last_name`

**Maintenant :**
```python
# User et Client
first_name: Mapped[str] = mapped_column(String(50), nullable=False)
last_name: Mapped[str] = mapped_column(String(50), nullable=False)
```

**Avantages :**
- ✅ **Tri et recherche améliorés** : possibilité de trier par nom de famille
- ✅ **Validation plus précise** : chaque champ peut avoir sa propre validation (longueur min/max)
- ✅ **Flexibilité d'affichage** : on peut afficher "Prénom Nom" ou "Nom, Prénom" selon le contexte
- ✅ **Standard de l'industrie** : la plupart des systèmes CRM utilisent cette approche
- ✅ **Internationalisation** : facilite l'adaptation à différentes cultures

### Solution 2 : Ajout du champ `phone` au modèle User

**Maintenant :**
```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)  # ✅ Ajouté
    department: Mapped[Department] = mapped_column(SQLEnum(Department), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

**Avantages :**
- ✅ **Cohérence** : User et Client ont maintenant tous les deux un champ `phone`
- ✅ **Complétude des données** : possibilité de contacter tous les acteurs du système
- ✅ **Fonctionnalités futures** : base pour des notifications SMS, authentification 2FA, etc.

---

## Impacts sur le code

### 1. Modèles SQLAlchemy

**Fichiers modifiés :**
- `src/models/user.py` : Ajout de `phone`, remplacement de `full_name` par `first_name` et `last_name`
- `src/models/client.py` : Remplacement de `full_name` par `first_name` et `last_name`

**Méthode `__repr__` mise à jour :**
```python
# Client
def __repr__(self) -> str:
    return f"<Client(id={self.id}, name='{self.first_name} {self.last_name}', company='{self.company_name}')>"
```

### 2. Tests

**Fichiers modifiés :**
- `tests/conftest.py` : Fixtures `test_users` et `test_clients` mises à jour
- `tests/contract/test_auth_commands.py` : Validation du schéma JSON mise à jour

**Exemple de changement dans les fixtures :**
```python
# AVANT
admin = User(
    username="admin",
    full_name="Admin Gestion",
    department=Department.GESTION,
)

# APRÈS
admin = User(
    username="admin",
    first_name="Admin",
    last_name="Gestion",
    phone="+33 1 23 45 67 89",
    department=Department.GESTION,
)
```

### 3. Documentation

**Fichiers modifiés :**
- `docs/explication-models.md` : Exemples de modèles mis à jour
- `doc/database-schema.md` : Schéma de base de données complet mis à jour
- `docs/T007-contract-test-auth-commands.md` : Schéma JSON de réponse mis à jour

**Exemple de mise à jour du schéma JSON :**
```json
// AVANT
{
  "user": {
    "username": "admin",
    "full_name": "Administrator",
    "department": "GESTION"
  }
}

// APRÈS
{
  "user": {
    "username": "admin",
    "first_name": "Admin",
    "last_name": "Gestion",
    "department": "GESTION"
  }
}
```

---

## Exemples d'utilisation

### Création d'un User

```python
from src.models.user import User, Department

user = User(
    username="john.doe",
    first_name="John",
    last_name="Doe",
    phone="+33 6 12 34 56 78",
    department=Department.COMMERCIAL
)
user.set_password("SecurePass123")
```

### Création d'un Client

```python
from src.models.client import Client

client = Client(
    first_name="Jane",
    last_name="Smith",
    email="jane.smith@company.com",
    phone="+33 1 23 45 67 89",
    company_name="Smith Enterprises",
    sales_contact_id=commercial_user.id
)
```

### Recherche par nom de famille

```python
# Rechercher tous les utilisateurs avec le nom "Smith"
users = session.query(User).filter(User.last_name == "Smith").all()

# Trier les clients par nom de famille
clients = session.query(Client).order_by(Client.last_name).all()
```

### Affichage du nom complet

```python
# Option 1 : Prénom Nom
full_name = f"{user.first_name} {user.last_name}"

# Option 2 : Nom, Prénom (format administratif)
full_name = f"{user.last_name}, {user.first_name}"

# Option 3 : NOM Prénom (format français classique)
full_name = f"{user.last_name.upper()} {user.first_name}"
```

---

## Bénéfices attendus

### 1. Amélioration de l'UX

- **Formulaires plus clairs** : champs séparés pour prénom et nom
- **Validation plus précise** : messages d'erreur spécifiques à chaque champ
- **Flexibilité d'affichage** : adaptation selon le contexte (formel vs informel)

### 2. Amélioration des fonctionnalités

- **Recherche avancée** : recherche par prénom OU par nom de famille
- **Tri intelligent** : tri alphabétique par nom de famille
- **Rapports** : possibilité d'exporter des listes triées par nom

### 3. Préparation pour l'avenir

- **Internationalisation** : facilite l'adaptation à d'autres cultures
- **Intégrations tierces** : la plupart des API utilisent first_name/last_name
- **Notifications** : base pour SMS, appels, WhatsApp Business, etc.

---

## Conformité aux standards

### Standards de l'industrie

- ✅ **ISO/IEC 11179** : Séparation des noms en composants atomiques
- ✅ **RGPD** : Granularité des données personnelles pour le droit à l'oubli
- ✅ **Best practices CRM** : Structure standard utilisée par Salesforce, HubSpot, Zoho, etc.

### Standards de nommage SQLAlchemy

- ✅ **Type hints** : Utilisation de `Mapped[str]` pour le typage
- ✅ **Conventions** : `first_name` et `last_name` (snake_case)
- ✅ **Contraintes** : `nullable=False` pour champs obligatoires

---

## Conclusion

Cette conception améliore significativement la qualité et la maintenabilité du code en :

1. ✅ **Séparant les noms** en composants atomiques (`first_name`, `last_name`)
2. ✅ **Ajoutant le téléphone** au modèle User pour plus de cohérence
3. ✅ **Suivant les standards** de l'industrie et les bonnes pratiques
4. ✅ **Préparant l'avenir** pour de nouvelles fonctionnalités

Ces choix de conception sont essentiels pour un CRM moderne et professionnel, et permettront de répondre aux besoins actuels et futurs du projet Epic Events.

---

## Fichiers modifiés

### Modèles
- `src/models/user.py`
- `src/models/client.py`

### Tests
- `tests/conftest.py`
- `tests/contract/test_auth_commands.py`

### Documentation
- `docs/explication-models.md`
- `docs/T007-contract-test-auth-commands.md`
- `doc/database-schema.md`
- `docs/changements-separation-noms-ajout-telephone.md` (ce fichier)

---

**Statut** : ✅ Conception finalisée et documentée
