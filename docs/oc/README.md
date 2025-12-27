# 📚 Documentation Epic Events CRM

Documentation organisée du projet Epic Events CRM pour OpenClassrooms.

---

## 🎯 **Pour la soutenance (Livrables OpenClassrooms)**

| Fichier | Description | Usage |
|---------|-------------|-------|
| **[guide-soutenance.md](guide-soutenance.md)** | 🔥 Guide de révision complet pour la soutenance | Réviser le code Python, sécurité, architecture |
| **[database-schema.md](database-schema.md)** | Schéma de base de données avec diagramme Mermaid | Expliquer la structure des tables |
| **[oc/DEMO_GUIDE.md](oc/DEMO_GUIDE.md)** | 🎬 Guide de démonstration des commandes CLI | Tester manuellement toutes les fonctionnalités |
| **[SUPPORT_REQUIREMENTS_ANALYSIS.md](SUPPORT_REQUIREMENTS_ANALYSIS.md)** | Analyse des exigences équipe SUPPORT | Vérifier conformité cahier des charges |

---

## 📖 **Documentation OpenClassrooms (dossier `oc/`)**

Analyses détaillées de conformité au cahier des charges :

| Fichier | Description |
|---------|-------------|
| **[oc/SOUTENANCE.md](oc/SOUTENANCE.md)** | Notes pour la soutenance |
| **[oc/GENERAL_REQUIREMENTS_ANALYSIS.md](oc/GENERAL_REQUIREMENTS_ANALYSIS.md)** | Besoins généraux (4/4 ✅) |
| **[oc/COMMERCIAL_REQUIREMENTS_ANALYSIS.md](oc/COMMERCIAL_REQUIREMENTS_ANALYSIS.md)** | Équipe COMMERCIAL (6/6 ✅) |
| **[oc/GESTION_REQUIREMENTS_ANALYSIS.md](oc/GESTION_REQUIREMENTS_ANALYSIS.md)** | Équipe GESTION (7/7 ✅) |
| **[oc/AUTHENTICATION.md](oc/AUTHENTICATION.md)** | Système d'authentification JWT |
| **[oc/DEMO_AUTHENTICATION.md](oc/DEMO_AUTHENTICATION.md)** | Démonstration authentification |
| **[oc/SECURITY_SUMMARY.md](oc/SECURITY_SUMMARY.md)** | Résumé sécurité (OWASP Top 10) |
| **[oc/SECURITE_TOKEN.md](oc/SECURITE_TOKEN.md)** | Sécurité des tokens JWT |
| **[oc/SENTRY_SETUP.md](oc/SENTRY_SETUP.md)** | Configuration Sentry monitoring |
| **[oc/TESTS_AUTHENTIFICATION.md](oc/TESTS_AUTHENTIFICATION.md)** | Tests d'authentification |

**Conformité totale : 19/19 exigences (100%)** 🎉

---

## 🛠️ **Guides de démarrage rapide**

| Fichier | Description |
|---------|-------------|
| **[QUICK_START_AUTH.md](QUICK_START_AUTH.md)** | Démarrage rapide authentification |
| **[IDENTIFIANTS-TEST.md](IDENTIFIANTS-TEST.md)** | Identifiants de test pour la démo |
| **[guide-outils-administration-sqlite.md](guide-outils-administration-sqlite.md)** | Outils pour gérer SQLite |

---

## 👨‍💻 **Documentation technique (dossier `dev/`)**

Documentation avancée pour les développeurs :

| Fichier | Description |
|---------|-------------|
| **[dev/ALEMBIC_ENV_PY.md](dev/ALEMBIC_ENV_PY.md)** | Configuration Alembic migrations |
| **[dev/TYPE_CHECKING_explained.md](dev/TYPE_CHECKING_explained.md)** | Explication TYPE_CHECKING en Python |
| **[dev/TYPER_SOUS_APPLICATIONS.md](dev/TYPER_SOUS_APPLICATIONS.md)** | Architecture modulaire CLI avec Typer |
| **[dev/DEPENDENCY_INJECTION_CLI.md](dev/DEPENDENCY_INJECTION_CLI.md)** | Injection de dépendance dans CLI |
| **[dev/DEPENDENCY_INJECTION_PATTERN.md](dev/DEPENDENCY_INJECTION_PATTERN.md)** | Pattern injection de dépendance |
| **[dev/explication-models.md](dev/explication-models.md)** | Explication modèles SQLAlchemy |
| **[dev/RESOURCES_WEB.md](dev/RESOURCES_WEB.md)** | Ressources web utiles |
| **[dev/document-reference.md](dev/document-reference.md)** | Documents de référence |

---

## 🗄️ **Archives (dossier `archived/`)**

Documentation historique du développement :

| Fichier | Description |
|---------|-------------|
| **[archived/FLUX_CREATION_CLIENT.md](archived/FLUX_CREATION_CLIENT.md)** | Flux création client (ancienne version) |
| **[archived/REFACTORING_DECORATOR.md](archived/REFACTORING_DECORATOR.md)** | Refactoring décorateur permissions |
| **[archived/PERMISSIONS_GRANULAIRES.md](archived/PERMISSIONS_GRANULAIRES.md)** | Permissions granulaires (ancienne version) |
| **[archived/AMELIORATIONS_PERMISSIONS.md](archived/AMELIORATIONS_PERMISSIONS.md)** | Améliorations permissions |
| **[archived/RESUME_SPRINT_PERMISSIONS.md](archived/RESUME_SPRINT_PERMISSIONS.md)** | Résumé sprint permissions |
| **[archived/TOKEN_STORAGE.md](archived/TOKEN_STORAGE.md)** | Stockage token (ancienne doc) |
| **[archived/PYTEST_MOCK_EXPLAINED.md](archived/PYTEST_MOCK_EXPLAINED.md)** | Explication pytest mocks |
| **[archived/EXPLICATION_TEST_WHOAMI_WITHOUT_AUTH.md](archived/EXPLICATION_TEST_WHOAMI_WITHOUT_AUTH.md)** | Explication test whoami |
| **[archived/PLAN_AMELIORATION_TESTS.md](archived/PLAN_AMELIORATION_TESTS.md)** | Plan amélioration tests |
| **[archived/CONFIGURATION_EXTERNALIZATION.md](archived/CONFIGURATION_EXTERNALIZATION.md)** | Externalisation configuration |

---

## 🚀 **Navigation rapide**

### Je veux...

- **Préparer ma soutenance** → [guide-soutenance.md](guide-soutenance.md)
- **Tester toutes les commandes** → [oc/DEMO_GUIDE.md](oc/DEMO_GUIDE.md)
- **Expliquer le schéma BDD** → [database-schema.md](database-schema.md)
- **Comprendre l'authentification** → [oc/AUTHENTICATION.md](oc/AUTHENTICATION.md)
- **Vérifier la sécurité** → [oc/SECURITY_SUMMARY.md](oc/SECURITY_SUMMARY.md)
- **Apprendre l'architecture** → [dev/DEPENDENCY_INJECTION_PATTERN.md](dev/DEPENDENCY_INJECTION_PATTERN.md)

---

## 📝 **Structure des dossiers**

```
docs/
├── README.md                          ← Ce fichier
├── guide-soutenance.md                ← 🔥 Guide révision soutenance
├── database-schema.md                 ← Schéma BDD avec Mermaid
├── SUPPORT_REQUIREMENTS_ANALYSIS.md   ← Analyse exigences SUPPORT
├── QUICK_START_AUTH.md
├── IDENTIFIANTS-TEST.md
├── guide-outils-administration-sqlite.md
│
├── oc/                                ← Documentation OpenClassrooms
│   ├── DEMO_GUIDE.md                  ← 🎬 Guide démo complet
│   ├── SOUTENANCE.md
│   ├── *_REQUIREMENTS_ANALYSIS.md     ← Analyses conformité
│   ├── AUTHENTICATION.md
│   ├── SECURITY_SUMMARY.md
│   └── ...
│
├── dev/                               ← Documentation technique
│   ├── ALEMBIC_ENV_PY.md
│   ├── DEPENDENCY_INJECTION_*.md
│   ├── explication-models.md
│   └── ...
│
└── archived/                          ← Archives historiques
    ├── FLUX_CREATION_CLIENT.md
    ├── PERMISSIONS_GRANULAIRES.md
    └── ...
```

---

**Dernière mise à jour** : 2025-11-23
**Projet** : Epic Events CRM - OpenClassrooms Projet 12
