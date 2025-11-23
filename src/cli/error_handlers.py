"""Error handlers for CLI commands.

This module provides centralized error handling utilities
to reduce code duplication across CLI command modules.
"""

from sqlalchemy.exc import IntegrityError

from src.cli.console import print_error


def handle_integrity_error(
    error: IntegrityError, field_messages: dict[str, str]
) -> None:
    """Handle IntegrityError with context-specific messages.

    This function centralizes the handling of database integrity errors
    (unique constraints, foreign keys, etc.) to avoid code duplication.

    Args:
        error: The IntegrityError exception to handle
        field_messages: Dict mapping field names to error messages
            Example: {"username": "Username already exists",
                     "email": "Email already in use"}

    Example:
        try:
            user = user_service.create_user(...)
        except IntegrityError as e:
            handle_integrity_error(e, {
                "username": f"Le nom d'utilisateur '{username}' existe déjà",
                "email": f"L'email '{email}' est déjà utilisé"
            })
            raise typer.Exit(code=1)
    """
    # Extract error message from SQLAlchemy exception
    error_msg = str(error.orig).lower() if hasattr(error, "orig") else str(
        error
    ).lower()

    # Check for unique constraint violations
    if "unique" in error_msg or "duplicate" in error_msg:
        # Try to find which field caused the error
        for field_name, message in field_messages.items():
            if field_name.lower() in error_msg:
                print_error(message)
                return

        # Generic unique constraint message if field not found
        print_error("Un enregistrement avec ces informations existe déjà")
        return

    # Check for foreign key constraint violations
    if "foreign key" in error_msg or "constraint" in error_msg:
        print_error(
            "Erreur de contrainte : Une référence invalide a été détectée"
        )
        return

    # Generic integrity error message
    print_error(f"Erreur d'intégrité de la base de données: {error_msg}")
