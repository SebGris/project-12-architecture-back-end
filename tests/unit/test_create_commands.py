"""
Tests unitaires pour les commandes CLI de création.

Tests couverts:
- create-contract : création avec validation client
- create-contract : erreurs (client inexistant)
- create-contract : contrat signé vs non signé

Note: Tests create-event nécessitent ajustements format date/validators
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
def mock_client(mocker, mock_commercial_user):
    """Create a mock client for testing."""
    client = mocker.Mock(spec=Client)
    client.id = 1
    client.first_name = "Jean"
    client.last_name = "Dupont"
    client.email = "jean.dupont@example.com"
    client.phone = "0612345678"
    client.company_name = "DupontCorp"
    client.sales_contact_id = 2
    client.sales_contact = mock_commercial_user
    return client


@pytest.fixture
def mock_contract(mocker, mock_client):
    """Create a mock contract for testing."""
    contract = mocker.Mock(spec=Contract)
    contract.id = 1
    contract.client_id = 1
    contract.client = mock_client
    contract.total_amount = Decimal("10000.00")
    contract.remaining_amount = Decimal("5000.00")
    contract.is_signed = True
    return contract


class TestCreateContractCommand:
    """Test create-contract command."""

    def test_create_contract_success(
        self, mocker, mock_commercial_user, mock_client
    ):
        """
        GIVEN valid contract data and existing client
        WHEN create-contract is executed
        THEN contract created successfully
        """
        # Create mock contract
        mock_contract = mocker.Mock(spec=Contract)
        mock_contract.id = 1
        mock_contract.client_id = 1
        mock_contract.client = mock_client
        mock_contract.total_amount = Decimal("10000.00")
        mock_contract.remaining_amount = Decimal("5000.00")
        mock_contract.is_signed = False

        # Mock Container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_contract_service = mocker.MagicMock()
        mock_client_service = mocker.MagicMock()

        # Setup services
        mock_client_service.get_client.return_value = mock_client
        mock_contract_service.create_contract.return_value = mock_contract

        # Wire container
        mock_container.return_value.contract_service.return_value = (
            mock_contract_service
        )
        mock_container.return_value.client_service.return_value = (
            mock_client_service
        )

        # Execute command
        result = runner.invoke(
            app,
            ["create-contract"],
            input="1\n10000.00\n5000.00\nn\n",  # client_id, total, remaining, not signed
        )

        # Verify
        assert result.exit_code == 0
        assert "créé avec succès" in result.stdout
        mock_contract_service.create_contract.assert_called_once()

    def test_create_contract_client_not_found(self, mocker):
        """
        GIVEN non-existing client_id
        WHEN create-contract is executed
        THEN error displayed about client not found
        """
        # Mock Container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_contract_service = mocker.MagicMock()
        mock_client_service = mocker.MagicMock()

        # Setup services - client not found
        mock_client_service.get_client.return_value = None

        # Wire container
        mock_container.return_value.contract_service.return_value = (
            mock_contract_service
        )
        mock_container.return_value.client_service.return_value = (
            mock_client_service
        )

        # Execute command
        result = runner.invoke(
            app,
            ["create-contract"],
            input="999\n10000.00\n5000.00\nn\n",
        )

        # Verify
        assert result.exit_code == 1
        assert "n'existe pas" in result.stdout
        mock_contract_service.create_contract.assert_not_called()

    def test_create_contract_signed(self, mocker, mock_commercial_user, mock_client):
        """
        GIVEN contract with is_signed=True
        WHEN create-contract is executed
        THEN signed contract created
        """
        # Create mock signed contract
        mock_contract = mocker.Mock(spec=Contract)
        mock_contract.id = 1
        mock_contract.client_id = 1
        mock_contract.client = mock_client
        mock_contract.total_amount = Decimal("15000.00")
        mock_contract.remaining_amount = Decimal("0.00")
        mock_contract.is_signed = True

        # Mock Container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_contract_service = mocker.MagicMock()
        mock_client_service = mocker.MagicMock()

        # Setup services
        mock_client_service.get_client.return_value = mock_client
        mock_contract_service.create_contract.return_value = mock_contract

        # Wire container
        mock_container.return_value.contract_service.return_value = (
            mock_contract_service
        )
        mock_container.return_value.client_service.return_value = (
            mock_client_service
        )

        # Execute command with is_signed=True
        result = runner.invoke(
            app,
            ["create-contract"],
            input="1\n15000.00\n0.00\ny\n",  # signed=yes
        )

        # Verify
        assert result.exit_code == 0
        assert "créé avec succès" in result.stdout
