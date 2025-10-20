"""CLI commands for Epic Events CRM.

This module defines the command-line interface commands.
Each command is responsible only for orchestrating the flow,
delegating specific responsibilities to specialized modules.
"""

import typer
from rich.console import Console
from src.cli.dependencies import (
    db_session_scope,
    get_client_service,
    get_user_service,
)
from src.cli.input_handlers import prompt_client_data, prompt_user_data
from src.cli.error_handlers import handle_command_errors, print_success

console = Console()
app = typer.Typer()

# Sous-applications pour mieux organiser
clients = typer.Typer(rich_markup_mode="rich")
users = typer.Typer(rich_markup_mode="rich")
events = typer.Typer(rich_markup_mode="rich")

app.add_typer(clients, name="client")
app.add_typer(users, name="user")
app.add_typer(events, name="event")


@clients.command("create")
def create_client():
    """Create a new client with interactive prompts."""

    def operation():
        # Header visuel
        console.rule("[bold cyan]Création d'un nouveau client[/bold cyan]")
        # Collect input data
        client_data = prompt_client_data()

        # Execute business logic with automatic session management
        with db_session_scope() as db:
            client_service = get_client_service(db)
            client = client_service.create_client(**client_data)

            # Provide feedback
            print_success(
                f"Client {client.first_name} {client.last_name} créé avec succès !"
            )
            return client

    handle_command_errors(operation)


@users.command("create")
def create_user():
    """Create a new user with interactive prompts."""

    def operation():
        # Collect input data
        user_data = prompt_user_data()

        # Execute business logic with automatic session management
        with db_session_scope() as db:
            user_service = get_user_service(db)
            user = user_service.create_user(**user_data)

            # Provide feedback
            print_success(f"Utilisateur {user.username} créé avec succès !")
            return user

    handle_command_errors(operation)


if __name__ == "__main__":
    app()
