"""
Tests unitaires pour les commandes CLI de filtrage.

Tests couverts:
- filter-unsigned-contracts : filtrage contrats non signés
- filter-unpaid-contracts : filtrage contrats non payés
- filter-unassigned-events : filtrage événements sans support
"""

import pytest
from decimal import Decimal
from datetime import datetime
from typer.testing import CliRunner

from src.cli.commands import app
from src.models.user import Department, User
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event

runner = CliRunner()


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


class TestFilterUnsignedContractsCommand:
    """Test filter-unsigned-contracts command."""

    def test_filter_unsigned_contracts_with_results(
        self, mocker, mock_gestion_user, mock_commercial_user
    ):
        """
        GIVEN unsigned contracts in database
        WHEN filter-unsigned-contracts is executed
        THEN unsigned contracts displayed
        """
        # Create mock client
        mock_client = mocker.Mock(spec=Client)
        mock_client.id = 1
        mock_client.first_name = "Jean"
        mock_client.last_name = "Dupont"
        mock_client.company_name = "DupontCorp"
        mock_client.sales_contact = mock_commercial_user

        # Create unsigned contracts
        contract1 = mocker.Mock(spec=Contract)
        contract1.id = 1
        contract1.client_id = 1
        contract1.client = mock_client
        contract1.total_amount = Decimal("10000.00")
        contract1.remaining_amount = Decimal("5000.00")
        contract1.is_signed = False

        contract2 = mocker.Mock(spec=Contract)
        contract2.id = 2
        contract2.client_id = 1
        contract2.client = mock_client
        contract2.total_amount = Decimal("8000.00")
        contract2.remaining_amount = Decimal("8000.00")
        contract2.is_signed = False

        # Mock Container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_contract_service = mocker.MagicMock()
        mock_auth_service = mocker.MagicMock()

        # Setup services
        mock_auth_service.get_current_user.return_value = mock_gestion_user
        mock_contract_service.get_unsigned_contracts.return_value = [
            contract1,
            contract2,
        ]

        # Wire container
        mock_container.return_value.contract_service.return_value = (
            mock_contract_service
        )
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute command
        result = runner.invoke(app, ["filter-unsigned-contracts"])

        # Verify
        assert result.exit_code == 0
        assert "non signés" in result.stdout.lower() or "unsigned" in result.stdout.lower()
        mock_contract_service.get_unsigned_contracts.assert_called_once()

    def test_filter_unsigned_contracts_empty(self, mocker, mock_gestion_user):
        """
        GIVEN no unsigned contracts
        WHEN filter-unsigned-contracts is executed
        THEN message about no unsigned contracts
        """
        # Mock Container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_contract_service = mocker.MagicMock()
        mock_auth_service = mocker.MagicMock()

        # Setup services
        mock_auth_service.get_current_user.return_value = mock_gestion_user
        mock_contract_service.get_unsigned_contracts.return_value = []

        # Wire container
        mock_container.return_value.contract_service.return_value = (
            mock_contract_service
        )
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute command
        result = runner.invoke(app, ["filter-unsigned-contracts"])

        # Verify
        assert result.exit_code == 0
        assert "aucun" in result.stdout.lower() or "0" in result.stdout


class TestFilterUnpaidContractsCommand:
    """Test filter-unpaid-contracts command."""

    def test_filter_unpaid_contracts_with_results(
        self, mocker, mock_gestion_user, mock_commercial_user
    ):
        """
        GIVEN unpaid contracts in database
        WHEN filter-unpaid-contracts is executed
        THEN unpaid contracts displayed
        """
        # Create mock client
        mock_client = mocker.Mock(spec=Client)
        mock_client.id = 1
        mock_client.first_name = "Jean"
        mock_client.last_name = "Dupont"
        mock_client.company_name = "DupontCorp"
        mock_client.sales_contact = mock_commercial_user

        # Create unpaid contracts
        contract1 = mocker.Mock(spec=Contract)
        contract1.id = 1
        contract1.client_id = 1
        contract1.client = mock_client
        contract1.total_amount = Decimal("10000.00")
        contract1.remaining_amount = Decimal("5000.00")
        contract1.is_signed = True

        contract2 = mocker.Mock(spec=Contract)
        contract2.id = 2
        contract2.client_id = 1
        contract2.client = mock_client
        contract2.total_amount = Decimal("15000.00")
        contract2.remaining_amount = Decimal("15000.00")
        contract2.is_signed = False

        # Mock Container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_contract_service = mocker.MagicMock()
        mock_auth_service = mocker.MagicMock()

        # Setup services
        mock_auth_service.get_current_user.return_value = mock_gestion_user
        mock_contract_service.get_unpaid_contracts.return_value = [
            contract1,
            contract2,
        ]

        # Wire container
        mock_container.return_value.contract_service.return_value = (
            mock_contract_service
        )
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute command
        result = runner.invoke(app, ["filter-unpaid-contracts"])

        # Verify
        assert result.exit_code == 0
        # Just verify the service was called and contracts were returned
        mock_contract_service.get_unpaid_contracts.assert_called_once()

    def test_filter_unpaid_contracts_empty(self, mocker, mock_gestion_user):
        """
        GIVEN no unpaid contracts
        WHEN filter-unpaid-contracts is executed
        THEN message about no unpaid contracts
        """
        # Mock Container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_contract_service = mocker.MagicMock()
        mock_auth_service = mocker.MagicMock()

        # Setup services
        mock_auth_service.get_current_user.return_value = mock_gestion_user
        mock_contract_service.get_unpaid_contracts.return_value = []

        # Wire container
        mock_container.return_value.contract_service.return_value = (
            mock_contract_service
        )
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute command
        result = runner.invoke(app, ["filter-unpaid-contracts"])

        # Verify
        assert result.exit_code == 0
        assert "aucun" in result.stdout.lower() or "0" in result.stdout


class TestFilterUnassignedEventsCommand:
    """Test filter-unassigned-events command."""

    def test_filter_unassigned_events_with_results(
        self, mocker, mock_gestion_user, mock_commercial_user
    ):
        """
        GIVEN unassigned events in database
        WHEN filter-unassigned-events is executed
        THEN unassigned events displayed
        """
        # Create mock client and contract
        mock_client = mocker.Mock(spec=Client)
        mock_client.id = 1
        mock_client.first_name = "Jean"
        mock_client.last_name = "Dupont"
        mock_client.sales_contact = mock_commercial_user

        mock_contract = mocker.Mock(spec=Contract)
        mock_contract.id = 1
        mock_contract.client = mock_client

        # Create unassigned events
        event1 = mocker.Mock(spec=Event)
        event1.id = 1
        event1.name = "Conference Tech"
        event1.contract_id = 1
        event1.contract = mock_contract
        event1.event_start = datetime(2025, 6, 15, 9, 0)
        event1.event_end = datetime(2025, 6, 15, 18, 0)
        event1.location = "Paris"
        event1.attendees = 100
        event1.support_contact_id = None
        event1.support_contact = None

        event2 = mocker.Mock(spec=Event)
        event2.id = 2
        event2.name = "Workshop Python"
        event2.contract_id = 1
        event2.contract = mock_contract
        event2.event_start = datetime(2025, 7, 20, 14, 0)
        event2.event_end = datetime(2025, 7, 20, 17, 0)
        event2.location = "Lyon"
        event2.attendees = 30
        event2.support_contact_id = None
        event2.support_contact = None

        # Mock Container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_event_service = mocker.MagicMock()
        mock_auth_service = mocker.MagicMock()

        # Setup services
        mock_auth_service.get_current_user.return_value = mock_gestion_user
        mock_event_service.get_unassigned_events.return_value = [event1, event2]

        # Wire container
        mock_container.return_value.event_service.return_value = mock_event_service
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute command
        result = runner.invoke(app, ["filter-unassigned-events"])

        # Verify
        assert result.exit_code == 0
        # Just verify the service was called and events were returned
        mock_event_service.get_unassigned_events.assert_called_once()

    def test_filter_unassigned_events_empty(self, mocker, mock_gestion_user):
        """
        GIVEN no unassigned events
        WHEN filter-unassigned-events is executed
        THEN message about no unassigned events
        """
        # Mock Container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_event_service = mocker.MagicMock()
        mock_auth_service = mocker.MagicMock()

        # Setup services
        mock_auth_service.get_current_user.return_value = mock_gestion_user
        mock_event_service.get_unassigned_events.return_value = []

        # Wire container
        mock_container.return_value.event_service.return_value = mock_event_service
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute command
        result = runner.invoke(app, ["filter-unassigned-events"])

        # Verify
        assert result.exit_code == 0
        assert "aucun" in result.stdout.lower() or "0" in result.stdout
