"""Permission decorators and checks for Epic Events CRM CLI.

This module provides decorators to enforce permissions based on user roles/departments.
"""

from functools import wraps
from typing import Callable

import typer

from src.cli.console import print_error, print_separator
from src.containers import Container
from src.models.user import Department, User


def require_department(*allowed_departments: Department):
    """Decorator to require authentication and optionally specific department(s).

    This decorator checks if the user is authenticated before executing the command.
    If departments are specified, it also checks if the user belongs to one of them.
    If no departments are specified, it only requires authentication (behaves like require_auth).

    Args:
        *allowed_departments: Variable number of Department enums (optional)

    Returns:
        A decorator function

    Examples:
        # Require only authentication (no department restriction)
        @app.command()
        @require_department()
        def my_command(**kwargs):
            current_user = kwargs.get('current_user')
            pass

        # Require specific department(s)
        @app.command()
        @require_department(Department.GESTION, Department.COMMERCIAL)
        def restricted_command(**kwargs):
            current_user = kwargs.get('current_user')
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get auth_service from kwargs (injected by dependency_injector)
            auth_service = kwargs.get("auth_service")

            if not auth_service:
                # If auth_service is not in kwargs, create one manually
                container = Container()
                container.wire(modules=[__name__])
                auth_service = container.auth_service()

            # Check if user is authenticated
            user = auth_service.get_current_user()

            if not user:
                print_separator()
                print_error(
                    "Vous devez être connecté pour effectuer cette action"
                )
                print_error("Utilisez 'epicevents login' pour vous connecter")
                print_separator()
                raise typer.Exit(code=1)

            # Check if user has the required department (only if departments are specified)
            if allowed_departments and user.department not in allowed_departments:
                dept_names = ", ".join([d.value for d in allowed_departments])
                print_separator()
                print_error(f"Action non autorisée pour votre département")
                print_error(f"Départements autorisés : {dept_names}")
                print_error(f"Votre département : {user.department.value}")
                print_separator()
                raise typer.Exit(code=1)

            # Add user to kwargs for the command function
            kwargs["current_user"] = user

            return func(*args, **kwargs)

        return wrapper

    return decorator
