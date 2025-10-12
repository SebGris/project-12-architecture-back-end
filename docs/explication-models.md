# Explication des Modèles de Données - Epic Events CRM

## Vue d'ensemble

Ce document explique l'architecture des modèles de données pour le système CRM Epic Events. L'application utilise **SQLAlchemy 2.0** avec le pattern **ORM (Object-Relational Mapping)** pour gérer la base de données SQLite.

---

## Architecture Générale

### Base (`__init__.py`)

```python
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass
```

**Points clés à expliquer :**
- `DeclarativeBase` est la nouvelle approche SQLAlchemy 2.0 (plus moderne que l'ancienne `declarative_base()`)
- Tous les modèles héritent de cette classe `Base`
- Permet à SQLAlchemy de tracker automatiquement tous les modèles et leurs métadonnées
- Facilite la génération automatique des migrations avec Alembic

---

## Modèle User (Utilisateur)

### Structure

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    department: Mapped[Department] = mapped_column(SQLEnum(Department), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### Points à expliquer pendant la soutenance

#### 1. Type Hints avec `Mapped`
- **SQLAlchemy 2.0** utilise `Mapped[type]` pour le typage moderne
- Permet à MyPy et aux IDE de vérifier les types
- Améliore l'autocomplétion et détecte les erreurs avant l'exécution

#### 2. Énumération `Department`
```python
class Department(str, Enum):
    COMMERCIAL = "COMMERCIAL"
    GESTION = "GESTION"
    SUPPORT = "SUPPORT"
```
- Hérite de `str` ET `Enum` pour être compatible avec JSON et base de données
- Garantit que seules 3 valeurs sont possibles (validation automatique)
- Facilite les contrôles d'accès basés sur les rôles (RBAC - Role-Based Access Control)

#### 3. Sécurité du mot de passe
- `password_hash` : ne stocke JAMAIS le mot de passe en clair
- Méthodes `set_password()` et `verify_password()` préparées pour utiliser **bcrypt** via passlib
- Bcrypt est un algorithme de hachage adaptatif (résistant aux attaques par force brute)

#### 4. Timestamps automatiques
- `created_at` : horodatage lors de la création (immutable)
- `updated_at` : mis à jour automatiquement avec `onupdate=func.now()`
- Utilisation de `server_default=func.now()` : timestamp généré par la base de données (plus fiable)
- `DateTime(timezone=True)` : stocke les timestamps avec timezone (UTC) pour éviter les erreurs de comparaison
- Pattern standard pour l'audit et le suivi des modifications

---

## Modèle Client

### Structure

```python
class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    company_name: Mapped[str] = mapped_column(String(100), nullable=False)
    sales_contact_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
```

### Points à expliquer

#### 1. Clé étrangère (Foreign Key)
```python
sales_contact_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
```
- Référence l'ID d'un utilisateur (commercial)
- `nullable=False` : chaque client DOIT avoir un commercial assigné
- Maintient l'intégrité référentielle au niveau de la base de données

#### 2. Email unique
- `unique=True` sur l'email évite les doublons
- Base de données rejette automatiquement les insertions duplicates
- Crée un index automatique pour optimiser les recherches

#### 3. Relationships commentées
```python
# sales_contact: Mapped["User"] = relationship("User", back_populates="clients")
```
- Préparé mais commenté pour éviter les imports circulaires
- `relationship()` crée la navigation objet : `client.sales_contact.username`
- `back_populates` crée la relation bidirectionnelle

---

## Modèle Contract (Contrat)

### Structure

```python
class Contract(Base):
    __tablename__ = "contracts"

    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    remaining_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_signed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
```

### Points à expliquer

#### 1. Type `Numeric` pour l'argent
```python
Numeric(10, 2)
```
- **JAMAIS utiliser `float` pour l'argent** (problèmes d'arrondi)
- `Numeric(10, 2)` = 10 chiffres totaux, dont 2 décimales
- Exemple : 99 999 999.99 euros maximum
- Précision exacte garantie pour les calculs financiers

#### 2. Contraintes d'intégrité (`CheckConstraint`)
```python
__table_args__ = (
    CheckConstraint("total_amount >= 0", name="check_total_amount_positive"),
    CheckConstraint("remaining_amount >= 0", name="check_remaining_amount_positive"),
    CheckConstraint("remaining_amount <= total_amount", name="check_remaining_lte_total"),
)
```

**Pourquoi c'est important :**
- **Validation au niveau base de données** (pas seulement application)
- Empêche les montants négatifs
- Garantit que le restant dû ne dépasse jamais le total
- Protection même si quelqu'un accède directement à la BDD

#### 3. Statut de signature
```python
is_signed: Mapped[bool] = mapped_column(Boolean, default=False)
```
- Par défaut `False` : nouveau contrat = non signé
- Important pour les règles métier (ex: événement possible seulement si contrat signé)

---

## Modèle Event (Événement)

### Structure

```python
class Event(Base):
    __tablename__ = "events"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    event_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    event_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    attendees: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"), nullable=False)
    support_contact_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
```

### Points à expliquer

#### 1. Champs optionnels avec `Optional`
```python
notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
support_contact_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
```
- `Optional[type]` en Python correspond à `nullable=True` en SQL
- `notes` : peut être vide (pas toujours nécessaire)
- `support_contact_id` : peut être `NULL` (support pas encore assigné)

#### 2. Type `Text` vs `String`
```python
notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
```
- `String(n)` : longueur limitée (ex: String(100) = 100 caractères max)
- `Text` : longueur illimitée pour les notes longues
- Choix adapté au type de données

#### 3. Contraintes de validation métier
```python
__table_args__ = (
    CheckConstraint("event_end > event_start", name="check_event_dates_valid"),
    CheckConstraint("attendees >= 0", name="check_attendees_positive"),
)
```
- `event_end > event_start` : impossible de créer un événement incohérent
- `attendees >= 0` : pas de participants négatifs
- **Protection des données au niveau le plus bas**

---

## Relations entre les Modèles

### Diagramme conceptuel

```
User (Employee)
    ├─> Client (sales_contact_id)
    └─> Event (support_contact_id)

Client
    └─> Contract (client_id)

Contract
    └─> Event (contract_id)
```

### Explication des relations

#### 1. User → Client (One-to-Many)
- Un commercial (User) gère plusieurs clients (Client)
- Chaque client a UN seul commercial assigné

#### 2. User → Event (One-to-Many)
- Un membre du support (User) peut gérer plusieurs événements (Event)
- Un événement peut ne pas avoir de support assigné (`nullable=True`)

#### 3. Client → Contract (One-to-Many)
- Un client peut avoir plusieurs contrats
- Chaque contrat appartient à un seul client

#### 4. Contract → Event (One-to-Many)
- Un contrat peut avoir plusieurs événements
- Chaque événement est lié à un seul contrat

---

## Bonnes Pratiques Utilisées

### 1. Conventions de nommage
- Tables : pluriel en minuscules (`users`, `clients`, `contracts`, `events`)
- Clés étrangères : `{table}_id` (ex: `client_id`, `contract_id`)
- Contraintes : noms descriptifs (ex: `check_total_amount_positive`)

### 2. Méthode `__repr__`
```python
def __repr__(self) -> str:
    return f"<User(id={self.id}, username='{self.username}', department={self.department})>"
```
- Facilite le debugging (affichage lisible des objets)
- Utile dans le shell Python interactif
- Pattern standard Python

### 3. SQLAlchemy 2.0 moderne
- `Mapped[type]` pour le typage
- `mapped_column()` au lieu de `Column()`
- Type hints pour tous les champs
- Compatible avec les outils de vérification de type (MyPy)

### 4. Sécurité et validation
- Contraintes de base de données (`CheckConstraint`)
- Validation des types avec énumérations
- Clés étrangères pour l'intégrité référentielle
- Hash des mots de passe (préparé avec bcrypt)

---

## Points d'amélioration Future

### 1. Activation des relationships
Actuellement commentées pour éviter les imports circulaires :
```python
# sales_contact: Mapped["User"] = relationship("User", back_populates="clients")
```

**À activer pour :**
- Navigation objet simplifiée
- Chargement automatique des relations (lazy/eager loading)
- Meilleure expérience développeur

### 2. Soft delete
Ajouter un champ `deleted_at` pour ne pas supprimer physiquement les données :
```python
deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
```

### 3. Indexes supplémentaires
Pour optimiser les requêtes fréquentes :
```python
__table_args__ = (
    Index('idx_client_email', 'email'),
    Index('idx_contract_signed', 'is_signed'),
)
```

---

## Questions Potentielles lors de la Soutenance

### Q1 : Pourquoi SQLAlchemy plutôt que du SQL brut ?
**Réponse :**
- Abstraction de la base de données (portabilité SQLite/PostgreSQL/MySQL)
- Protection contre les injections SQL
- Migrations gérées avec Alembic
- Code Python plus maintenable

### Q2 : Pourquoi `Numeric` au lieu de `float` pour l'argent ?
**Réponse :**
- `float` a des problèmes d'arrondi (0.1 + 0.2 ≠ 0.3 en binaire)
- `Numeric` garantit la précision exacte
- Standard pour les applications financières

### Q3 : Pourquoi les contraintes dans la base de données ?
**Réponse :**
- **Dernier rempart de sécurité** : même si l'application a un bug, la BDD refuse les données invalides
- Protection contre les modifications directes de la base
- Documentation vivante des règles métier

### Q4 : Pourquoi ne pas activer les relationships maintenant ?
**Réponse :**
- Évite les imports circulaires pendant le développement initial
- Sera activé lors de l'implémentation des repositories
- Approche itérative : modèles d'abord, relations ensuite

### Q5 : Comment gérez-vous la sécurité des mots de passe ?
**Réponse :**
- Hash avec bcrypt (via passlib)
- Jamais de stockage en clair
- Coût adaptatif contre les attaques par force brute
- Méthodes `set_password()` et `verify_password()` dédiées

### Q6 : Pourquoi utiliser `server_default=func.now()` au lieu de `default=datetime.utcnow()` ?
**Réponse :**
- **Timestamp généré par la base de données** : garantit la cohérence même si plusieurs serveurs ont des horloges différentes
- **Évite les bugs de référence** : pas besoin d'appeler la fonction avec des parenthèses
- **Plus performant** : pas de round-trip Python → SQL pour générer le timestamp
- **Conforme aux bonnes pratiques SQLAlchemy** : recommandé dans la documentation officielle
- **Compatible avec les migrations** : Alembic gère mieux les valeurs par défaut côté serveur

### Q7 : Pourquoi `DateTime(timezone=True)` ?
**Réponse :**
- **Évite les erreurs de comparaison** : sans timezone, on ne peut pas comparer un datetime "naïf" avec un datetime "aware" (erreur TypeError)
- **Explicite et international** : tous les timestamps sont en UTC, peu importe le fuseau horaire du serveur
- **Bonne pratique moderne** : les applications internationales doivent toujours utiliser des timestamps timezone-aware
- **Facilite les tests** : pas de surprise avec les fuseaux horaires lors des tests automatisés
- **Exemple concret** : `if user.created_at < datetime.now(timezone.utc)` fonctionne sans erreur

---

## Conclusion

Ce design de modèles suit les principes **SOLID** et les bonnes pratiques de l'industrie :
- **Single Responsibility** : chaque modèle a une responsabilité claire
- **Type Safety** : utilisation complète du typage Python 3.13
- **Data Integrity** : contraintes et validations multi-niveaux
- **Maintenabilité** : code lisible et bien documenté
- **Évolutivité** : préparé pour les extensions futures

Cette architecture solide facilitera l'implémentation des couches Repository, Service et Controller.
