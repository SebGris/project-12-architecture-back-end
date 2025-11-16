"""Tests unitaires pour les permissions granulaires."""

import pytest
from unittest.mock import Mock, patch
from typer.testing import CliRunner

from src.cli.commands import app
from src.models.user import Department, User
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event
from datetime import datetime
from decimal import Decimal


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_commercial_user():
    """Mock a COMMERCIAL user."""
    user = Mock(spec=User)
    user.id = 1
    user.username = "commercial1"
    user.first_name = "John"
    user.last_name = "Doe"
    user.department = Department.COMMERCIAL
    return user


@pytest.fixture
def mock_gestion_user():
    """Mock a GESTION user."""
    user = Mock(spec=User)
    user.id = 2
    user.username = "gestion1"
    user.first_name = "Alice"
    user.last_name = "Smith"
    user.department = Department.GESTION
    return user


@pytest.fixture
def mock_support_user():
    """Mock a SUPPORT user."""
    user = Mock(spec=User)
    user.id = 3
    user.username = "support1"
    user.first_name = "Bob"
    user.last_name = "Johnson"
    user.department = Department.SUPPORT
    return user


@pytest.fixture
def mock_client_owned_by_commercial():
    """Mock a client owned by commercial1."""
    sales_contact = Mock()
    sales_contact.id = 1
    sales_contact.first_name = "John"
    sales_contact.last_name = "Doe"

    client = Mock(spec=Client)
    client.id = 1
    client.first_name = "Client"
    client.last_name = "Test"
    client.sales_contact_id = 1
    client.sales_contact = sales_contact
    return client


@pytest.fixture
def mock_client_owned_by_other():
    """Mock a client owned by another commercial."""
    sales_contact = Mock()
    sales_contact.id = 99
    sales_contact.first_name = "Other"
    sales_contact.last_name = "Commercial"

    client = Mock(spec=Client)
    client.id = 2
    client.first_name = "Other"
    client.last_name = "Client"
    client.sales_contact_id = 99
    client.sales_contact = sales_contact
    return client


@pytest.fixture
def mock_event_owned_by_support():
    """Mock an event owned by support1."""
    support_contact = Mock()
    support_contact.id = 3
    support_contact.first_name = "Bob"
    support_contact.last_name = "Johnson"

    event = Mock(spec=Event)
    event.id = 1
    event.support_contact_id = 3
    event.support_contact = support_contact
    return event


@pytest.fixture
def mock_event_owned_by_other():
    """Mock an event owned by another support."""
    support_contact = Mock()
    support_contact.id = 99
    support_contact.first_name = "Other"
    support_contact.last_name = "Support"

    event = Mock(spec=Event)
    event.id = 2
    event.support_contact_id = 99
    event.support_contact = support_contact
    return event


class TestUpdateClientPermissions:
    """Tests for update-client command permissions."""

    @patch('src.cli.commands.Container')
    def test_commercial_can_update_own_client(
        self, mock_container, runner, mock_commercial_user, mock_client_owned_by_commercial
    ):
        """Test that a COMMERCIAL user can update their own client."""
        # Setup mocks
        container_instance = Mock()
        mock_container.return_value = container_instance

        mock_auth_service = Mock()
        mock_auth_service.get_current_user.return_value = mock_commercial_user

        mock_client_service = Mock()
        mock_client_service.get_client.return_value = mock_client_owned_by_commercial
        mock_client_service.update_client.return_value = mock_client_owned_by_commercial

        container_instance.auth_service.return_value = mock_auth_service
        container_instance.client_service.return_value = mock_client_service

        # Execute command with inputs
        result = runner.invoke(app, ['update-client'], input='1\nNewName\n\n\n\n\n')

        # Verify
        assert result.exit_code == 0 or "mis à jour avec succès" in result.stdout

    @patch('src.cli.commands.Container')
    def test_commercial_cannot_update_other_client(
        self, mock_container, runner, mock_commercial_user, mock_client_owned_by_other
    ):
        """Test that a COMMERCIAL user cannot update another's client."""
        # Setup mocks
        container_instance = Mock()
        mock_container.return_value = container_instance

        mock_auth_service = Mock()
        mock_auth_service.get_current_user.return_value = mock_commercial_user

        mock_client_service = Mock()
        mock_client_service.get_client.return_value = mock_client_owned_by_other

        container_instance.auth_service.return_value = mock_auth_service
        container_instance.client_service.return_value = mock_client_service

        # Execute command
        result = runner.invoke(app, ['update-client'], input='2\n')

        # Verify rejection
        assert result.exit_code == 1
        assert "Vous ne pouvez modifier que vos propres clients" in result.stdout

    @patch('src.cli.commands.Container')
    def test_gestion_can_update_any_client(
        self, mock_container, runner, mock_gestion_user, mock_client_owned_by_other
    ):
        """Test that a GESTION user can update any client."""
        # Setup mocks
        container_instance = Mock()
        mock_container.return_value = container_instance

        mock_auth_service = Mock()
        mock_auth_service.get_current_user.return_value = mock_gestion_user

        mock_client_service = Mock()
        mock_client_service.get_client.return_value = mock_client_owned_by_other
        mock_client_service.update_client.return_value = mock_client_owned_by_other

        container_instance.auth_service.return_value = mock_auth_service
        container_instance.client_service.return_value = mock_client_service

        # Execute command
        result = runner.invoke(app, ['update-client'], input='2\nTest\n\n\n\n\n')

        # Verify success
        assert result.exit_code == 0 or "mis à jour avec succès" in result.stdout


class TestUpdateEventAttendeesPermissions:
    """Tests for update-event-attendees command permissions."""

    @patch('src.cli.commands.Container')
    def test_support_can_update_own_event(
        self, mock_container, runner, mock_support_user, mock_event_owned_by_support
    ):
        """Test that a SUPPORT user can update their own event."""
        # Setup mocks
        container_instance = Mock()
        mock_container.return_value = container_instance

        mock_auth_service = Mock()
        mock_auth_service.get_current_user.return_value = mock_support_user

        mock_event_service = Mock()
        mock_event_service.get_event.return_value = mock_event_owned_by_support
        mock_event_service.update_attendees.return_value = mock_event_owned_by_support

        container_instance.auth_service.return_value = mock_auth_service
        container_instance.event_service.return_value = mock_event_service

        # Add required attributes for success message
        mock_event_owned_by_support.name = "Test Event"
        mock_event_owned_by_support.contract_id = 1
        mock_event_owned_by_support.event_start = datetime(2025, 6, 1, 14, 0)
        mock_event_owned_by_support.event_end = datetime(2025, 6, 1, 18, 0)
        mock_event_owned_by_support.location = "Test Location"
        mock_event_owned_by_support.attendees = 100
        mock_event_owned_by_support.notes = None

        # Execute command
        result = runner.invoke(app, ['update-event-attendees'], input='1\n100\n')

        # Verify success
        assert result.exit_code == 0 or "mis à jour avec succès" in result.stdout

    @patch('src.cli.commands.Container')
    def test_support_cannot_update_other_event(
        self, mock_container, runner, mock_support_user, mock_event_owned_by_other
    ):
        """Test that a SUPPORT user cannot update another's event."""
        # Setup mocks
        container_instance = Mock()
        mock_container.return_value = container_instance

        mock_auth_service = Mock()
        mock_auth_service.get_current_user.return_value = mock_support_user

        mock_event_service = Mock()
        mock_event_service.get_event.return_value = mock_event_owned_by_other

        container_instance.auth_service.return_value = mock_auth_service
        container_instance.event_service.return_value = mock_event_service

        # Execute command
        result = runner.invoke(app, ['update-event-attendees'], input='2\n')

        # Verify rejection
        assert result.exit_code == 1
        assert "Vous ne pouvez modifier que vos propres événements" in result.stdout

    @patch('src.cli.commands.Container')
    def test_gestion_can_update_any_event(
        self, mock_container, runner, mock_gestion_user, mock_event_owned_by_other
    ):
        """Test that a GESTION user can update any event."""
        # Setup mocks
        container_instance = Mock()
        mock_container.return_value = container_instance

        mock_auth_service = Mock()
        mock_auth_service.get_current_user.return_value = mock_gestion_user

        mock_event_service = Mock()
        mock_event_service.get_event.return_value = mock_event_owned_by_other
        mock_event_service.update_attendees.return_value = mock_event_owned_by_other

        container_instance.auth_service.return_value = mock_auth_service
        container_instance.event_service.return_value = mock_event_service

        # Add required attributes
        mock_event_owned_by_other.name = "Test Event"
        mock_event_owned_by_other.contract_id = 1
        mock_event_owned_by_other.event_start = datetime(2025, 6, 1, 14, 0)
        mock_event_owned_by_other.event_end = datetime(2025, 6, 1, 18, 0)
        mock_event_owned_by_other.location = "Test Location"
        mock_event_owned_by_other.attendees = 150
        mock_event_owned_by_other.notes = None

        # Execute command
        result = runner.invoke(app, ['update-event-attendees'], input='2\n150\n')

        # Verify success
        assert result.exit_code == 0 or "mis à jour avec succès" in result.stdout


class TestFilterMyEventsPermissions:
    """Tests for filter-my-events command."""

    @patch('src.cli.commands.Container')
    def test_filter_my_events_shows_only_own_events(
        self, mock_container, runner, mock_support_user
    ):
        """Test that filter-my-events shows only the user's own events."""
        # Setup mocks
        container_instance = Mock()
        mock_container.return_value = container_instance

        mock_auth_service = Mock()
        mock_auth_service.get_current_user.return_value = mock_support_user

        # Create mock events
        event1 = Mock()
        event1.id = 1
        event1.contract_id = 1
        event1.event_start = datetime(2025, 6, 1, 14, 0)
        event1.event_end = datetime(2025, 6, 1, 18, 0)
        event1.location = "Location 1"
        event1.attendees = 100
        event1.notes = None
        event1.contract = Mock()
        event1.contract.client = Mock()
        event1.contract.client.first_name = "Client"
        event1.contract.client.last_name = "One"
        event1.contract.client.email = "client@test.com"
        event1.contract.client.phone = "+33123456789"

        mock_event_service = Mock()
        mock_event_service.get_events_by_support_contact.return_value = [event1]

        container_instance.auth_service.return_value = mock_auth_service
        container_instance.event_service.return_value = mock_event_service

        # Execute command
        result = runner.invoke(app, ['filter-my-events'])

        # Verify
        assert result.exit_code == 0
        mock_event_service.get_events_by_support_contact.assert_called_once_with(mock_support_user.id)
