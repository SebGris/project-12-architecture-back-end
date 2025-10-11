# Historique des Changements - Correction des Timestamps

**Date:** 2025-10-11
**Auteur:** Étudiant OpenClassrooms - Projet 12
**Révisé par:** Claude AI

## Contexte

Lors de la revue du code des modèles SQLAlchemy, un problème critique a été identifié concernant la gestion des timestamps `created_at` et `updated_at` dans tous les modèles de données.

## Problème Identifié

### Code Problématique (Avant)

```python
created_at: Mapped[datetime] = mapped_column(
    DateTime, default=datetime.utcnow
)
updated_at: Mapped[datetime] = mapped_column(
    DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
)
```

### Issues Identifiées

1. **Référence de fonction sans appel** : `datetime.utcnow` était passé sans parenthèses, ce qui signifie que la référence à la fonction était utilisée plutôt que son résultat. Cela aurait causé un timestamp identique pour tous les enregistrements créés lors de la même session Python.

2. **Dépréciation Python 3.12** : `datetime.utcnow()` est marqué comme déprécié depuis Python 3.12 en faveur de `datetime.now(timezone.utc)`.

3. **Gestion côté application vs côté base de données** : L'utilisation de `default` avec des fonctions Python signifie que le timestamp est généré par l'application Python, pas par la base de données. Cela peut causer des problèmes de cohérence temporelle.

## Solution Implémentée

### Code Corrigé (Après)

```python
created_at: Mapped[datetime] = mapped_column(
    DateTime, server_default=func.now()
)
updated_at: Mapped[datetime] = mapped_column(
    DateTime, server_default=func.now(), onupdate=func.now()
)
```

### Avantages de Cette Approche

1. **Timestamp généré par la base de données** : Utilisation de `server_default=func.now()` qui génère un timestamp SQLite natif
2. **Cohérence garantie** : Le timestamp est créé au moment de l'insertion dans la base de données, pas au moment de la création de l'objet Python
3. **Évite les bugs de référence de fonction** : Plus besoin d'appeler la fonction avec des parenthèses
4. **Conforme aux bonnes pratiques SQLAlchemy** : L'utilisation de `func.now()` est la méthode recommandée

## Fichiers Modifiés

### 1. [src/models/user.py](../src/models/user.py)

**Lignes modifiées:** 30-35

**Changements:**
- Ajout de l'import `func` depuis `sqlalchemy`
- Remplacement de `default=datetime.utcnow` par `server_default=func.now()`
- Remplacement de `onupdate=datetime.utcnow` par `onupdate=func.now()`

### 2. [src/models/client.py](../src/models/client.py)

**Lignes modifiées:** 4, 19-22

**Changements:**
- Ajout de l'import `func` depuis `sqlalchemy`
- Remplacement de `default=datetime.utcnow` par `server_default=func.now()`
- Remplacement de `onupdate=datetime.utcnow` par `onupdate=func.now()`

### 3. [src/models/contract.py](../src/models/contract.py)

**Lignes modifiées:** 11, 30-35

**Changements:**
- Ajout de l'import `func` dans la liste des imports SQLAlchemy
- Remplacement de `default=datetime.utcnow` par `server_default=func.now()`
- Remplacement de `onupdate=datetime.utcnow` par `onupdate=func.now()`

### 4. [src/models/event.py](../src/models/event.py)

**Lignes modifiées:** 4, 22-25

**Changements:**
- Ajout de l'import `func` depuis `sqlalchemy`
- Remplacement de `default=datetime.utcnow` par `server_default=func.now()`
- Remplacement de `onupdate=datetime.utcnow` par `onupdate=func.now()`

## Impact sur les Migrations

**Important:** Ces changements nécessiteront une nouvelle migration Alembic car nous modifions les valeurs par défaut des colonnes.

### Action Requise

```bash
# Générer une nouvelle migration
poetry run alembic revision --autogenerate -m "Fix timestamps to use server_default"

# Vérifier la migration générée avant de l'appliquer
# Puis appliquer la migration
poetry run alembic upgrade head
```

## Tests à Effectuer

Après l'application de la migration, vérifier que :

1. Les nouveaux enregistrements reçoivent automatiquement un `created_at` correct
2. Le champ `updated_at` se met à jour automatiquement lors des modifications
3. Les timestamps sont cohérents avec l'heure du serveur de base de données
4. Pas de régression sur les enregistrements existants (si applicable)

## Références

- [SQLAlchemy Server Defaults](https://docs.sqlalchemy.org/en/20/core/defaults.html#server-invoked-ddl-explicit-default-expressions)
- [SQLAlchemy func Documentation](https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.func)
- [Python datetime.utcnow() Deprecation](https://docs.python.org/3/library/datetime.html#datetime.datetime.utcnow)

## Notes pour le Mentor

Cette correction était nécessaire pour assurer la fiabilité du système de tracking temporel de l'application. Le bug aurait pu passer inaperçu en développement mais aurait causé des problèmes sérieux en production, notamment :

- Impossibilité d'auditer correctement les changements
- Timestamps incorrects dans les logs et rapports
- Potentiels problèmes de synchronisation entre plusieurs instances de l'application

La solution implémentée suit les bonnes pratiques SQLAlchemy et garantit une gestion robuste des timestamps.
