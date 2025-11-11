# 🌐 Ressources Web - CLI avec Typer et JWT

Ce document regroupe toutes les ressources web utiles pour développer une application CLI Python avec authentification JWT.

## 📚 Table des matières

1. [Typer - Framework CLI](#typer---framework-cli)
2. [JWT Authentication](#jwt-authentication)
3. [Rich - Terminal UI](#rich---terminal-ui)
4. [SQLAlchemy](#sqlalchemy)
5. [Sécurité et bonnes pratiques](#sécurité-et-bonnes-pratiques)

---

## 🎯 Typer - Framework CLI

### Documentation officielle
- **Site officiel**: https://typer.tiangolo.com/
- **Tutorial complet**: https://typer.tiangolo.com/tutorial/
- **Alternatives (Typer vs Click)**: https://typer.tiangolo.com/alternatives/

### Tutoriels et comparaisons
- **Towards Data Science - Typer Tutorial**: https://towardsdatascience.com/typer-probably-the-simplest-to-use-python-command-line-interface-library-17abf1a5fd3e/
  - Excellent article sur pourquoi Typer est simple à utiliser
  - Exemples pratiques

- **CodeCut - Argparse vs Click vs Typer**: https://codecut.ai/comparing-python-command-line-interface-tools-argparse-click-and-typer/
  - Comparaison complète des 3 frameworks
  - Avantages et inconvénients

- **Medium - Navigating the CLI Landscape**: https://medium.com/@mohd_nass/navigating-the-cli-landscape-in-python-a-comparative-study-of-argparse-click-and-typer-480ebbb7172f
  - Étude comparative approfondie
  - Cas d'usage

- **Python in Plain English - Click vs Argparse vs Typer**: https://python.plainenglish.io/building-command-line-tools-in-python-click-vs-argparse-vs-typer-514442c25a56
  - Guide pratique pour choisir

### Points clés
- ✅ Typer est construit sur Click
- ✅ Utilise les type hints Python modernes
- ✅ Autocomplétion automatique
- ✅ Documentation auto-générée
- ✅ Meilleur choix pour nouveaux projets 2024-2025

---

## 🔐 JWT Authentication

### Pour applications CLI Python

- **Auth0 - Securing Python CLI Application**: https://auth0.com/blog/securing-a-python-cli-application-with-auth0/
  - **⭐ LE PLUS PERTINENT pour CLI**
  - Device authorization flow pour CLI
  - Validation et vérification des tokens
  - Stockage des données utilisateur
  - Gestion du logout

### PyJWT - Bibliothèque principale

- **PyJWT Documentation officielle**: https://pyjwt.readthedocs.io/en/stable/
  - Documentation complète
  - Encodage/décodage des tokens
  - Exemples de code
  - Pas de framework web requis

- **Auth0 - How to Handle JWTs in Python**: https://auth0.com/blog/how-to-handle-jwt-in-python/
  - Structure des JWT (header, payload, signature)
  - Utilisation basique de PyJWT
  - Concepts fondamentaux

- **WorkOS - How to handle JWT in Python**: https://workos.com/blog/how-to-handle-jwt-in-python
  - Approche moderne et sécurisée
  - Bonnes pratiques

- **Medium - Demystifying JWT Authentication**: https://mayurbirle.medium.com/demystifying-jwt-authentication-with-python-b4302c39bf91
  - Guide complet sans framework web
  - Implémentation PyJWT pure
  - Exemples réutilisables

### JWT pour applications web (Flask/FastAPI) - Pour référence

- **FreeCodeCamp - JWT Authentication in Flask**: https://www.freecodecamp.org/news/jwt-authentication-in-flask/
  - Guide complet Flask + JWT
  - Explications détaillées

- **Medium - RESTful API with Flask + SQLAlchemy + JWT**: https://obikastanya.medium.com/create-completed-restfull-api-with-flask-sql-alchemy-and-jwt-as-authenticator-4edd3f8f26b7
  - API REST complète
  - Architecture CRM

- **Pavel Tashev - Flask JWT Extended**: https://www.paveltashev.com/newsletter/flask-login-with-flask-jwt-extended-and-sqlalchemy-and-mongodb-token-storages/
  - Login/logout avec Flask-JWT-Extended
  - Stockage des tokens avec SQLAlchemy
  - Refresh tokens et révocation

- **FastAPI - OAuth2 with JWT**: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
  - Guide officiel FastAPI
  - OAuth2 + JWT

- **TestDriven.io - FastAPI JWT Auth**: https://testdriven.io/blog/fastapi-jwt-auth/
  - Tutorial complet FastAPI

### Concepts et standards

- **JWT.io**: https://jwt.io/
  - Décoder et comprendre les JWT
  - Debugger interactif

- **RFC 7519 - JWT Standard**: https://tools.ietf.org/html/rfc7519
  - Spécification officielle JWT

---

## 🎨 Rich - Terminal UI

### Documentation

- **Rich Documentation officielle**: https://rich.readthedocs.io/
  - Documentation complète
  - Exemples pour tous les composants

### Fonctionnalités principales

- **Console**: Texte coloré et formaté
- **Tables**: Tableaux formatés pour les listes
- **Prompts**: Saisie interactive élégante
- **Progress**: Barres de progression
- **Panels**: Panneaux avec bordures
- **Markdown**: Rendu markdown dans le terminal

---

## 💾 SQLAlchemy

### Documentation

- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **SQLAlchemy 2.0 Tutorial**: https://docs.sqlalchemy.org/en/20/tutorial/
- **SQLite Dialect**: https://docs.sqlalchemy.org/en/20/dialects/sqlite.html

### SQLite

- **SQLite Documentation**: https://www.sqlite.org/docs.html
- **Python sqlite3 Module**: https://docs.python.org/3/library/sqlite3.html

---

## 🔒 Sécurité et bonnes pratiques

### Password Hashing

- **Passlib Documentation**: https://passlib.readthedocs.io/
  - Bibliothèque pour hashing sécurisé
  - Support bcrypt

- **bcrypt**: https://github.com/pyca/bcrypt/
  - Hashing de mots de passe

### Sécurité générale

- **OWASP Security Guidelines**: https://owasp.org/
  - Bonnes pratiques de sécurité
  - Top 10 des vulnérabilités

- **Python Security Best Practices**: https://python.readthedocs.io/en/stable/library/security_warnings.html

---

## 📦 Gestion de projet

### Poetry

- **Poetry Documentation**: https://python-poetry.org/docs/
  - Gestionnaire de dépendances moderne
  - Meilleure alternative à pip + requirements.txt

### Alembic

- **Alembic Documentation**: https://alembic.sqlalchemy.org/
  - Migrations de base de données
  - Intégration SQLAlchemy

---

## 🧪 Testing

### Pytest

- **Pytest Documentation**: https://docs.pytest.org/
  - Framework de tests Python
  - Fixtures et mocking

- **Pytest-cov**: https://pytest-cov.readthedocs.io/
  - Couverture de code

---

## 🎓 Tutoriels spécifiques à notre cas d'usage

### Créer une CLI avec authentification JWT

**Stack: Python CLI + SQLAlchemy + JWT + Typer**

1. **Commencer par Typer**
   - https://typer.tiangolo.com/tutorial/first-steps/
   - Créer la structure de base

2. **Ajouter SQLAlchemy**
   - https://docs.sqlalchemy.org/en/20/tutorial/
   - Créer les modèles

3. **Implémenter JWT**
   - https://auth0.com/blog/securing-a-python-cli-application-with-auth0/
   - https://pyjwt.readthedocs.io/en/stable/
   - Créer AuthService

4. **Améliorer l'UI**
   - https://rich.readthedocs.io/
   - Ajouter Rich pour tableaux et couleurs

5. **Gérer les permissions**
   - Implémenter un système de rôles basé sur Enum
   - Décorateurs ou fonctions de vérification

---

## 🔍 Recherche de solutions

### Stack Overflow

- **JWT authentication in CLI**: https://stackoverflow.com/questions/tagged/jwt+python+cli
- **Typer + SQLAlchemy**: https://stackoverflow.com/questions/tagged/typer+sqlalchemy

### GitHub

- **Exemples de projets CLI avec Typer**:
  - Rechercher "typer jwt cli" sur GitHub
  - Étudier les projets open source

---

## 📊 Comparaisons et décisions

### Pourquoi Typer plutôt que Click ?

**Résumé des recherches**:
- Typer est construit sur Click
- Syntaxe plus moderne avec type hints
- Meilleure expérience développeur
- Autocomplétion automatique
- Recommandé pour nouveaux projets 2024-2025

**Sources**:
- https://typer.tiangolo.com/alternatives/
- https://github.com/fastapi/typer/issues/169

### Pourquoi PyJWT pour CLI ?

**Résumé des recherches**:
- Simple et léger
- Pas besoin de framework web
- Standard industriel (RFC 7519)
- Bien documenté
- Facile à intégrer avec SQLAlchemy

**Sources**:
- https://pyjwt.readthedocs.io/
- https://auth0.com/blog/securing-a-python-cli-application-with-auth0/

---

## 📝 Notes finales

### Installation des dépendances

```bash
# Avec Poetry (recommandé)
poetry add typer[all] rich sqlalchemy pyjwt bcrypt python-dotenv

# Ou avec pip
pip install "typer[all]" rich sqlalchemy pyjwt bcrypt python-dotenv
```

### Commandes utiles

```bash
# Aide Typer
python -m src.cli.main --help

# Générer autocomplétion
python -m src.cli.main --install-completion

# Décoder un JWT
# Aller sur https://jwt.io/ et coller votre token
```

---

## 🎯 Ressources par cas d'usage

### Je veux créer une CLI simple avec Typer
→ https://typer.tiangolo.com/tutorial/first-steps/

### Je veux ajouter l'authentification JWT
→ https://auth0.com/blog/securing-a-python-cli-application-with-auth0/
→ https://pyjwt.readthedocs.io/en/stable/

### Je veux améliorer l'interface utilisateur
→ https://rich.readthedocs.io/

### Je veux gérer les utilisateurs avec SQLAlchemy
→ https://docs.sqlalchemy.org/en/20/tutorial/

### Je veux sécuriser les mots de passe
→ https://passlib.readthedocs.io/

### Je veux comprendre JWT
→ https://jwt.io/introduction
→ https://auth0.com/blog/how-to-handle-jwt-in-python/

---

## 🤝 Communauté et support

- **Typer GitHub**: https://github.com/fastapi/typer
- **PyJWT GitHub**: https://github.com/jpadilla/pyjwt
- **SQLAlchemy GitHub**: https://github.com/sqlalchemy/sqlalchemy
- **Discord FastAPI** (inclut Typer): https://discord.gg/fastapi

---

**Date de création**: 2025
**Dernière mise à jour**: 2025
**Projet**: Epic Events CRM - OpenClassrooms
