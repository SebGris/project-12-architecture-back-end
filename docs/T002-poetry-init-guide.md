# Guide d'initialisation Poetry

## Étapes après `poetry init --python "^3.13"`

Après avoir lancé la commande `poetry init --python "^3.13"`, Poetry vous demande de renseigner des informations pour créer votre fichier `pyproject.toml`.

### 1. Questions interactives

1. **Version** : Appuyez sur Entrée pour accepter `0.1.0` (valeur par défaut)
2. **Description** : Entrez une brève description de votre projet ou appuyez sur Entrée pour laisser vide
3. **Author** : Poetry propose généralement votre nom depuis git, appuyez sur Entrée pour accepter
4. **License** : Choisissez une licence (ex: MIT) ou appuyez sur Entrée pour laisser vide
5. **Compatible Python versions** : Déjà défini à `^3.13`, appuyez sur Entrée
6. **Define dependencies interactively** : Tapez `no` (vous les ajouterez après avec `poetry add`)
7. **Define dev dependencies interactively** : Tapez `no`
8. **Confirm generation** : Tapez `yes`

### 2. Après la création du `pyproject.toml`

```bash
# Créer l'environnement virtuel
poetry install

# Ajouter vos dépendances de production (projet CRM)
poetry add click rich sqlalchemy alembic python-jose[cryptography] passlib[bcrypt] pydantic sentry-sdk python-dotenv

# Ajouter des dépendances de développement
poetry add --group dev pytest pytest-cov pytest-mock black flake8 mypy
```

#### Explication des dépendances de production

- **click** : Créer des interfaces en ligne de commande (CLI)
- **rich** : Affichage enrichi dans le terminal (couleurs, tableaux, progress bars)
- **sqlalchemy** : ORM pour interagir avec la base de données
- **alembic** : Gestion des migrations de base de données
- **python-jose[cryptography]** : Création et validation de tokens JWT pour l'authentification
- **passlib[bcrypt]** : Hachage sécurisé des mots de passe
- **pydantic** : Validation des données et configuration
- **sentry-sdk** : Monitoring et gestion des erreurs en production
- **python-dotenv** : Charger les variables d'environnement depuis un fichier `.env`

#### Explication des dépendances de développement

- **pytest** : Framework de tests
- **pytest-cov** : Mesure de la couverture de code par les tests
- **pytest-mock** : Création de mocks pour les tests
- **black** : Formateur de code automatique
- **flake8** : Linter pour détecter les erreurs de style
- **mypy** : Vérification du typage statique

#### Qu'est-ce que `--group` ?

Le flag `--group` permet d'organiser les dépendances en **groupes** distincts dans Poetry.

**Différence clé :**
- **Sans `--group`** : Dépendances de **production** (nécessaires pour exécuter l'application)
- **Avec `--group dev`** : Dépendances de **développement** (uniquement pour développer/tester)

**Avantage :**
Quand vous déployez en production, vous pouvez installer **uniquement** les dépendances nécessaires :

```bash
# En production : n'installe PAS les dépendances de dev
poetry install --only main

# En développement : installe tout
poetry install
```

Cela réduit la taille de votre environnement de production et améliore la sécurité (pas d'outils de test/debug en prod).

**Autres groupes possibles :**
```bash
poetry add --group test pytest
poetry add --group docs sphinx
poetry add --group lint ruff
```

### 3. Commandes utiles

```bash
# Activer l'environnement virtuel
poetry shell

# Exécuter une commande dans l'environnement virtuel sans l'activer
poetry run python script.py

# Voir les dépendances installées
poetry show

# Mettre à jour les dépendances
poetry update

# Exporter les dépendances vers requirements.txt
poetry export -f requirements.txt --output requirements.txt
```

## Résultat

Vous obtiendrez un fichier `pyproject.toml` configuré avec Python 3.13+ et prêt pour gérer vos dépendances de manière moderne et reproductible.
