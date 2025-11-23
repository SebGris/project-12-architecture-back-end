"""Sentry configuration for Epic Events CRM.

This module configures Sentry for error logging and monitoring.
"""

import os
import sentry_sdk
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def init_sentry():
    """Initialize Sentry SDK for error tracking and monitoring.

    This function configures Sentry with the following parameters:
    - DSN from SENTRY_DSN environment variable
    - Execution traces for performance monitoring
    - Profiles for detailed performance analysis
    - Environment (dev/staging/production)

    If SENTRY_DSN is not defined, Sentry will not be initialized.
    """
    sentry_dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "development")

    if not sentry_dsn:
        # Sentry not configured - development mode
        print("[INFO] Sentry not configured (SENTRY_DSN missing)")
        return False

    try:
        sentry_sdk.init(
            dsn=sentry_dsn,

            # Performance monitoring configuration
            # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring.
            # Adjust this value in production to reduce overhead
            traces_sample_rate=1.0,

            # Performance profiling configuration
            # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions.
            # Adjust this value in production
            profiles_sample_rate=1.0,

            # Environment (development, staging, production)
            environment=environment,

            # Enable SQL query logging
            enable_tracing=True,

            # Release version (optional - configure with git or CI/CD)
            # release="epic-events-crm@1.0.0",

            # Additional options
            send_default_pii=False,  # Do not send personal information
            attach_stacktrace=True,  # Attach stack trace to all messages
            max_breadcrumbs=50,      # Maximum number of breadcrumbs
        )

        print(f"[INFO] Sentry initialized successfully (environment: {environment})")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to initialize Sentry: {e}")
        return False


def capture_exception(exception: Exception, context: dict = None):
    """Capture an exception and send it to Sentry.

    Args:
        exception: The exception to capture
        context: Additional context dictionary (optional)

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
    """Capture a message and send it to Sentry.

    Args:
        message: The message to record
        level: Severity level ("debug", "info", "warning", "error", "fatal")
        context: Additional context dictionary (optional)

    Example:
        capture_message("Login attempt failed", level="warning",
                       context={"username": username})
    """
    if context:
        sentry_sdk.set_context("additional_info", context)

    sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: int, username: str, department: str = None):
    """Set user context for Sentry.

    Args:
        user_id: User ID
        username: Username
        department: User department (optional)

    Example:
        set_user_context(user.id, user.username, user.department.value)
    """
    sentry_sdk.set_user({
        "id": user_id,
        "username": username,
        "department": department
    })


def clear_user_context():
    """Clear user context (during logout)."""
    sentry_sdk.set_user(None)


def add_breadcrumb(message: str, category: str = "action", level: str = "info", data: dict = None):
    """Add a breadcrumb to trace user journey.

    Breadcrumbs are events that allow retracing user actions
    before an error occurs.

    Args:
        message: Action description
        category: Action category (action, navigation, http, etc.)
        level: Severity level
        data: Additional data (optional)

    Example:
        add_breadcrumb("Creating a client", category="action",
                      data={"client_email": email})
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )
