"""Permission decorators and checks for Epic Events CRM CLI.

This module provides decorators to enforce permissions based on user roles/departments.
"""

import inspect
from functools import wraps
from typing import Callable

import typer

from src.cli.console import print_error, print_separator
from src.containers import Container
from src.models.user import Department

# Error messages
MSG_NOT_LOGGED_IN = "Vous devez être connecté pour effectuer cette action"
MSG_LOGIN_HINT = "Utilisez 'epicevents login' pour vous connecter"
MSG_UNAUTHORIZED = "Action non autorisée pour votre département"


def require_department(*valid_departments: Department):
    """Decorator to require authentication and optionally specific department(s).

    This decorator checks if the user is authenticated before executing the command.
    If departments are specified, it also checks if the user belongs to one of them.
    If no departments are specified, it only requires authentication (behaves like require_auth).

    The decorator instantiates auth_service internally and injects current_user
    as an explicit parameter to the decorated function.

    Args:
        *valid_departments: Variable number of Department enums (optional)

    Returns:
        A decorator function

    Examples:
        # Require only authentication (no department restriction)
        @app.command()
        @require_department()
        def my_command(current_user: User):
            # current_user is automatically injected
            pass

        # Require specific department(s)
        @app.command()
        @require_department(Department.GESTION, Department.COMMERCIAL)
        def restricted_command(current_user: User):
            # current_user is automatically injected
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Instantiate auth_service directly from container
            container = Container()
            auth_service = container.auth_service()

            # Check if user is authenticated
            user = auth_service.get_current_user()

            if not user:
                print_separator()
                print_error(MSG_NOT_LOGGED_IN)
                print_error(MSG_LOGIN_HINT)
                print_separator()
                raise typer.Exit(code=1)

            # Check if user has the required department (only if departments are specified)
            if valid_departments and user.department not in valid_departments:
                dept_names = ", ".join(d.value for d in valid_departments)
                print_separator()
                print_error(MSG_UNAUTHORIZED)
                print_error(f"Départements autorisés : {dept_names}")
                print_error(f"Votre département : {user.department.value}")
                print_separator()
                raise typer.Exit(code=1)

            # Inject current_user only if the function expects it
            sig = inspect.signature(func)
            if "current_user" in sig.parameters:
                kwargs["current_user"] = user

            return func(*args, **kwargs)

        return wrapper

    return decorator
