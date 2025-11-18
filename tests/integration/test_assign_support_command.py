"""
Tests unitaires pour la commande assign-support.

Tests couverts:
- assign-support : erreur utilisateur non SUPPORT (validation métier)

Note: Autres tests assign-support complexes (double Container avec decorator)
"""

import pytest
from datetime import datetime
from typer.testing import CliRunner

from src.cli.commands import app
from src.models.user import Department, User
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event

runner = CliRunner()


@pytest.fixture
def mock_support_user(mocker):
    """Create a mock support user for testing."""
    user = mocker.Mock(spec=User)
    user.id = 3
    user.username = "support1"
    user.email = "support1@epicevents.com"
    user.first_name = "Charlie"
    user.last_name = "Support"
    user.phone = "+33 1 33 33 33 33"
    user.department = Department.SUPPORT
    return user


@pytest.fixture
def mock_commercial_user(mocker):
    """Create a mock commercial user for testing."""
    user = mocker.Mock(spec=User)
    user.id = 2
    user.username = "commercial1"
    user.email = "commercial1@epicevents.com"
    user.first_name = "Bob"
    user.last_name = "Commercial"
    user.phone = "+33 1 22 22 22 22"
    user.department = Department.COMMERCIAL
    return user


@pytest.fixture
def mock_gestion_user(mocker):
    """Create a mock gestion user for testing."""
    user = mocker.Mock(spec=User)
    user.id = 1
    user.username = "gestion1"
    user.email = "gestion1@epicevents.com"
    user.first_name = "Alice"
    user.last_name = "Gestion"
    user.phone = "+33 1 11 11 11 11"
    user.department = Department.GESTION
    return user


@pytest.fixture
def mock_event(mocker):
    """Create a mock event for testing."""
    event = mocker.Mock(spec=Event)
    event.id = 1
    event.name = "Conference Tech"
    event.contract_id = 1
    event.event_start = datetime(2025, 6, 15, 9, 0)
    event.event_end = datetime(2025, 6, 15, 18, 0)
    event.location = "Paris"
    event.attendees = 100
    event.notes = "Test conference"
    event.support_contact_id = None
    return event


class TestAssignSupportCommand:
    """Test assign-support command - validation métier."""

    def test_assign_support_user_not_support_department(
        self, mocker, mock_gestion_user, mock_event, mock_commercial_user
    ):
        """
        GIVEN user from COMMERCIAL department (not SUPPORT)
        WHEN assign-support is executed
        THEN error displayed about wrong department
        """
        # Mock Container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_event_service = mocker.MagicMock()
        mock_user_service = mocker.MagicMock()

        # Setup services - user is COMMERCIAL, not SUPPORT
        mock_event_service.get_event.return_value = mock_event
        mock_user_service.get_user.return_value = mock_commercial_user

        # Wire container
        mock_container.return_value.event_service.return_value = (
            mock_event_service
        )
        mock_container.return_value.user_service.return_value = (
            mock_user_service
        )

        # Execute command
        result = runner.invoke(
            app,
            ["assign-support"],
            input="1\n2\n",  # Try to assign commercial user as support
        )

        # Verify
        assert result.exit_code == 1
        assert (
            "support" in result.stdout.lower()
            or "département" in result.stdout.lower()
        )
        mock_event_service.assign_support_contact.assert_not_called()
