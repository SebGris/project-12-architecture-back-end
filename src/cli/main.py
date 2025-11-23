"""
Main entry point for the Epic Events CRM application.
This module is referenced in pyproject.toml for the 'epicevents' command.
"""

from src.containers import Container
from src.cli import commands, permissions
from src.cli.commands import auth_commands, user_commands, client_commands, contract_commands, event_commands
from src.sentry_config import init_sentry


def main():
    """Main entry point for the application."""
    # 1. Initialize Sentry for error tracking
    init_sentry()

    # 2. Initialize the dependency injection container
    container = Container()

    # 3. Wire the container to enable automatic dependency injection
    # This tells dependency_injector to scan the commands and permissions modules
    # and inject dependencies marked with @inject and Provide[...]
    container.wire(modules=[
        auth_commands,
        user_commands,
        client_commands,
        contract_commands,
        event_commands,
        permissions
    ])

    # 4. Launch the Typer application
    try:
        commands.app()
    except Exception as e:
        # Capture unhandled exceptions in Sentry
        from src.sentry_config import capture_exception

        capture_exception(e, context={"location": "main"})
        raise
    finally:
        # 5. Clean up: unwire the container when application exits
        container.unwire()


if __name__ == "__main__":
    main()
