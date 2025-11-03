"""Configuration Sentry pour Epic Events CRM.

Ce module configure Sentry pour la journalisation et le monitoring des erreurs.
"""

import os
import sentry_sdk
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def init_sentry():
    """Initialize Sentry SDK for error tracking and monitoring.

    Cette fonction configure Sentry avec les paramètres suivants :
    - DSN depuis la variable d'environnement SENTRY_DSN
    - Traces d'exécution pour le monitoring de performance
    - Profils pour l'analyse de performance détaillée
    - Environnement (dev/staging/production)

    Si SENTRY_DSN n'est pas défini, Sentry ne sera pas initialisé.
    """
    sentry_dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "development")

    if not sentry_dsn:
        # Sentry non configuré - mode développement
        print("[INFO] Sentry non configuré (SENTRY_DSN manquant)")
        return False

    try:
        sentry_sdk.init(
            dsn=sentry_dsn,

            # Configuration du monitoring de performance
            # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring.
            # Adjust this value in production to reduce overhead
            traces_sample_rate=1.0,

            # Configuration des profils de performance
            # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions.
            # Adjust this value in production
            profiles_sample_rate=1.0,

            # Environnement (development, staging, production)
            environment=environment,

            # Activer le logging des requêtes SQL
            enable_tracing=True,

            # Release version (optionnel - à configurer avec git ou CI/CD)
            # release="epic-events-crm@1.0.0",

            # Options supplémentaires
            send_default_pii=False,  # Ne pas envoyer d'informations personnelles
            attach_stacktrace=True,  # Attacher la stack trace à tous les messages
            max_breadcrumbs=50,      # Nombre maximum de breadcrumbs
        )

        print(f"[INFO] Sentry initialisé avec succès (environnement: {environment})")
        return True

    except Exception as e:
        print(f"[ERREUR] Échec de l'initialisation de Sentry: {e}")
        return False


def capture_exception(exception: Exception, context: dict = None):
    """Capture une exception et l'envoie à Sentry.

    Args:
        exception: L'exception à capturer
        context: Dictionnaire de contexte additionnel (optionnel)

    Example:
        try:
            risky_operation()
        except Exception as e:
            capture_exception(e, {"user_id": user.id, "action": "create_client"})
    """
    if context:
        sentry_sdk.set_context("additional_info", context)

    sentry_sdk.capture_exception(exception)


def capture_message(message: str, level: str = "info", context: dict = None):
    """Capture un message et l'envoie à Sentry.

    Args:
        message: Le message à enregistrer
        level: Niveau de gravité ("debug", "info", "warning", "error", "fatal")
        context: Dictionnaire de contexte additionnel (optionnel)

    Example:
        capture_message("Tentative de connexion échouée", level="warning",
                       context={"username": username})
    """
    if context:
        sentry_sdk.set_context("additional_info", context)

    sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: int, username: str, department: str = None):
    """Définir le contexte utilisateur pour Sentry.

    Args:
        user_id: ID de l'utilisateur
        username: Nom d'utilisateur
        department: Département de l'utilisateur (optionnel)

    Example:
        set_user_context(user.id, user.username, user.department.value)
    """
    sentry_sdk.set_user({
        "id": user_id,
        "username": username,
        "department": department
    })


def clear_user_context():
    """Effacer le contexte utilisateur (lors de la déconnexion)."""
    sentry_sdk.set_user(None)


def add_breadcrumb(message: str, category: str = "action", level: str = "info", data: dict = None):
    """Ajouter un breadcrumb pour tracer le parcours de l'utilisateur.

    Les breadcrumbs sont des événements qui permettent de retracer les actions
    de l'utilisateur avant qu'une erreur ne se produise.

    Args:
        message: Description de l'action
        category: Catégorie de l'action (action, navigation, http, etc.)
        level: Niveau de gravité
        data: Données additionnelles (optionnel)

    Example:
        add_breadcrumb("Création d'un client", category="action",
                      data={"client_email": email})
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )
