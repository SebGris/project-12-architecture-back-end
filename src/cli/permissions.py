"""Permission decorators and checks for Epic Events CRM CLI.

This module provides decorators to enforce permissions based on user roles/departments.
"""

from functools import wraps
from typing import Callable

import typer

from src.cli.console import print_error, print_separator
from src.containers import Container
from src.models.user import Department, User


def require_auth(func: Callable) -> Callable:
    """Decorator to require authentication for a command.

    This decorator checks if the user is authenticated before executing the command.
    If not authenticated, it displays an error message and exits.

    Args:
        func: The command function to decorate

    Returns:
        The decorated function

    Example:
        @app.command()
        @require_auth
        def my_command(**kwargs):
            # current_user is automatically injected in kwargs by the decorator
            current_user = kwargs.get('current_user')
            pass
    """

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
            print_error("Vous devez être connecté pour effectuer cette action")
            print_error("Utilisez 'epicevents login' pour vous connecter")
            print_separator()
            raise typer.Exit(code=1)

        # Add user to kwargs for the command function
        kwargs["current_user"] = user

        return func(*args, **kwargs)

    return wrapper


def require_department(*allowed_departments: Department):
    """Decorator to require specific department(s) for a command.

    This decorator checks if the authenticated user belongs to one of the
    allowed departments before executing the command.

    Args:
        *allowed_departments: Variable number of Department enums

    Returns:
        A decorator function

    Example:
        @app.command()
        @require_department(Department.GESTION, Department.COMMERCIAL)
        def my_command(**kwargs):
            # current_user is automatically injected in kwargs by the decorator
            current_user = kwargs.get('current_user')
            # Services can be accessed from Container
            container = Container()
            service = container.some_service()
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

            # Check if user has the required department
            if user.department not in allowed_departments:
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
