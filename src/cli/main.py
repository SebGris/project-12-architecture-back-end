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

    # 2. Wire the container to enable automatic dependency injection
    # This tells dependency_injector to scan the commands module
    # and inject dependencies marked with @inject and Provide[...]
    container.wire(modules=[commands])

    # 3. Launch the Typer application
    try:
        commands.app()
    finally:
        # 4. Clean up: unwire the container when application exits
        container.unwire()


if __name__ == "__main__":
    main()
