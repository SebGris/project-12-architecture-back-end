"""
Main entry point for the Epic Events CRM application.
This module is referenced in pyproject.toml for the 'epicevents' command.
"""

from src.cli import commands
from src.sentry_config import init_sentry, capture_exception


def main():
    """Main entry point for the application."""
    # 1. Initialize Sentry for error tracking
    init_sentry()

    # 2. Launch the Typer application
    try:
        commands.app()
    except Exception as e:
        # Capture unhandled exceptions in Sentry
        capture_exception(e, context={"location": "main"})
        raise


if __name__ == "__main__":
    main()
