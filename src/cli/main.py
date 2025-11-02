"""
Main entry point for the Epic Events CRM application.
This module is referenced in pyproject.toml for the 'epicevents' command.
"""

from src.containers import Container
from src.cli import commands


def main():
    """Main entry point for the application."""
    # 1. Initialize the dependency injection container
    container = Container()

    # 2. Set the container in the commands module
    commands.set_container(container)

    # 3. Launch the Typer application
    commands.app()


if __name__ == "__main__":
    main()
