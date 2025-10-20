"""Error handlers for CLI commands.

This module centralizes error handling and user feedback,
separating the concern of error presentation from business logic.
"""

import logging
import typer
from rich.console import Console
from sqlalchemy.exc import IntegrityError, OperationalError, DBAPIError
from typing import Callable, Any, TypeVar, Optional
from contextlib import contextmanager

console = Console()
logger = logging.getLogger(__name__)

T = TypeVar('T')


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class DatabaseConnectionError(Exception):
    """Custom exception for database connection issues."""
    pass


class DuplicateRecordError(Exception):
    """Custom exception for duplicate record attempts."""
    pass


def handle_command_errors(operation: Callable[[], T]) -> Optional[T]:
    """Execute a command operation with standardized error handling.

    This function wraps command operations to provide consistent
    error handling and user feedback across all CLI commands.

    Args:
        operation: Callable that performs the command operation

    Returns:
        Result of the operation if successful, None if error occurred

    Raises:
        typer.Exit: On any error with appropriate exit code
    """
    try:
        return operation()
    except typer.Abort:
        # User pressed Ctrl+C during prompts
        console.print("\n[yellow]⚠[/yellow] Operation cancelled")
        logger.info("Operation cancelled by user")
        raise typer.Exit(code=130)  # Standard exit code for SIGINT

    except ValidationError as e:
        # Custom validation errors from business logic
        console.print(f"[red]✗[/red] Validation error: {e}")
        logger.warning(f"Validation error: {e}")
        raise typer.Exit(code=1)

    except DuplicateRecordError as e:
        # Specific handling for duplicate records
        console.print(f"[red]✗[/red] Duplicate record: {e}")
        logger.warning(f"Duplicate record error: {e}")
        raise typer.Exit(code=1)

    except IntegrityError as e:
        # Database constraint violations (duplicate username/email, etc.)
        error_msg = _parse_integrity_error(e)
        console.print(f"[red]✗[/red] Database constraint error: {error_msg}")
        logger.error(f"IntegrityError: {e}", exc_info=True)
        raise typer.Exit(code=1)

    except OperationalError as e:
        # Database operational errors (connection, timeout, etc.)
        console.print(
            "[red]✗[/red] Database connection error. Please check your database configuration."
        )
        logger.error(f"OperationalError: {e}", exc_info=True)
        raise typer.Exit(code=2)

    except DBAPIError as e:
        # Other database API errors
        console.print("[red]✗[/red] Database error occurred")
        logger.error(f"DBAPIError: {e}", exc_info=True)
        raise typer.Exit(code=2)

    except ValueError as e:
        # Validation errors from Python's built-in types
        console.print(f"[red]✗[/red] Invalid value: {e}")
        logger.warning(f"ValueError: {e}")
        raise typer.Exit(code=1)

    except KeyError as e:
        # Missing required data
        console.print(f"[red]✗[/red] Missing required field: {e}")
        logger.error(f"KeyError: {e}", exc_info=True)
        raise typer.Exit(code=1)

    except Exception as e:
        # Unexpected errors - log full traceback
        console.print(f"[red]✗[/red] Unexpected error: {e}")
        logger.exception(f"Unexpected error: {e}")
        raise typer.Exit(code=99)


def _parse_integrity_error(error: IntegrityError) -> str:
    """Parse IntegrityError to provide user-friendly message.

    Args:
        error: SQLAlchemy IntegrityError

    Returns:
        User-friendly error message
    """
    error_str = str(error.orig).lower()

    if 'unique' in error_str or 'duplicate' in error_str:
        if 'username' in error_str:
            return "Username already exists"
        elif 'email' in error_str:
            return "Email already exists"
        else:
            return "Record with these values already exists"

    elif 'foreign key' in error_str:
        return "Referenced record does not exist"

    elif 'not null' in error_str:
        return "Required field is missing"

    else:
        return "Database constraint violated"


def print_success(message: str) -> None:
    """Print a success message to the console.

    Args:
        message: Success message to display
    """
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print an error message to the console.

    Args:
        message: Error message to display
    """
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message to the console.

    Args:
        message: Warning message to display
    """
    console.print(f"[yellow]⚠[/yellow] {message}")
