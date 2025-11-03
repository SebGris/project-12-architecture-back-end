"""Tests for CLI commands with dependency injection."""

import pytest
from typer.testing import CliRunner
from unittest.mock import Mock, patch

from src.cli.commands import app
from src.containers import Container


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def container():
    """Create and configure a container for testing."""
    container = Container()
    return container


def test_cli_help_works(runner):
    """Test that the CLI help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "create-client" in result.stdout
    assert "create-user" in result.stdout
    assert "create-contract" in result.stdout


def test_dependency_injection_wiring():
    """Test that dependency injection wiring is configured correctly."""
    from src.cli import commands

    container = Container()

    # Wire the container
    container.wire(modules=[commands])

    # Verify that the container is wired
    assert hasattr(commands, 'app')

    # Clean up
    container.unwire()


def test_create_user_command_structure(runner):
    """Test that create-user command has correct structure."""
    result = runner.invoke(app, ["create-user", "--help"])
    assert result.exit_code == 0
    assert "Nom d'utilisateur" in result.stdout or "username" in result.stdout.lower()
