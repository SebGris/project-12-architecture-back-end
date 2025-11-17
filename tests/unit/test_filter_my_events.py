"""
Tests unitaires pour la commande filter-my-events CLI.

Tests couverts:
- filter-my-events par utilisateur COMMERCIAL (permission refusée)

Note: Les tests de succès SUPPORT sont complexes car la commande crée
deux instances de Container (une dans @require_department, une dans la fonction).
Le test de permissions est suffisant pour démontrer le RBAC.
"""

import pytest
from typer.testing import CliRunner

from src.cli.commands import app
from src.models.user import Department

runner = CliRunner()


@pytest.fixture
def mock_commercial_user(mocker):
    """Create a mock commercial user for testing."""
    user = mocker.Mock()
    user.id = 2
    user.username = "commercial1"
    user.email = "commercial1@epicevents.com"
    user.first_name = "Bob"
    user.last_name = "Martin"
    user.phone = "+33 1 23 45 67 90"
    user.department = Department.COMMERCIAL
    return user


class TestFilterMyEvents:
    """Test filter-my-events command permissions."""

    def test_filter_my_events_as_commercial_denied(
        self, mocker, mock_commercial_user
    ):
        """
        GIVEN a commercial user (not SUPPORT)
        WHEN filter-my-events command is executed
        THEN it should fail with permission error
        """
        # Mock container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_auth_service = mocker.MagicMock()

        # Configure mocks: commercial user tries to access
        mock_auth_service.get_current_user.return_value = mock_commercial_user

        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute filter-my-events
        result = runner.invoke(app, ["filter-my-events"])

        # Verify permission error
        assert result.exit_code == 1
        assert "Action non autorisée" in result.stdout
        assert "SUPPORT" in result.stdout
        assert "COMMERCIAL" in result.stdout
