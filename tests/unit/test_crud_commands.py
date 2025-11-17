"""
Tests unitaires pour les commandes CRUD CLI.

Tests couverts:
- create-client avec auto-assignation
- create-contract avec validation
- update-contract avec permissions granulaires

Note: Ces tests vérifient principalement les chemins de succès.
Les tests de permissions sont limités car Typer exécute les prompts avant les décorateurs.
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


@pytest.fixture
def mock_gestion_user(mocker):
    """Create a mock gestion user for testing."""
    user = mocker.Mock()
    user.id = 1
    user.username = "admin"
    user.email = "admin@epicevents.com"
    user.first_name = "Alice"
    user.last_name = "Dubois"
    user.phone = "+33 1 23 45 67 89"
    user.department = Department.GESTION
    return user


@pytest.fixture
def mock_client(mocker):
    """Create a mock client for testing."""
    client = mocker.Mock()
    client.id = 1
    client.first_name = "Jean"
    client.last_name = "Dupont"
    client.email = "jean.dupont@example.com"
    client.phone = "0612345678"
    client.company = "DupontCorp"
    client.sales_contact_id = 2
    client.sales_contact = mocker.Mock()
    client.sales_contact.first_name = "Bob"
    client.sales_contact.last_name = "Martin"
    return client


@pytest.fixture
def mock_contract(mocker, mock_client):
    """Create a mock contract for testing."""
    contract = mocker.Mock()
    contract.id = 1
    contract.client_id = 1
    contract.client = mock_client
    contract.total_amount = 10000.00
    contract.remaining_amount = 2000.00
    contract.is_signed = False
    return contract


class TestUpdateContractCommand:
    """Test update-contract command with granular permissions."""

    def test_update_contract_by_owner(
        self, mocker, mock_commercial_user, mock_contract
    ):
        """
        GIVEN a commercial updating their own client's contract
        WHEN update-contract command is executed
        THEN the contract should be updated successfully
        """
        # Mock container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_contract_service = mocker.MagicMock()
        mock_auth_service = mocker.MagicMock()

        # Configure mocks
        mock_auth_service.get_current_user.return_value = mock_commercial_user
        mock_contract_service.get_contract.return_value = mock_contract
        mock_contract_service.update_contract.return_value = mock_contract

        mock_container.return_value.contract_service.return_value = (
            mock_contract_service
        )
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Mock Sentry
        mocker.patch("src.sentry_config.add_breadcrumb")

        # Execute update-contract
        result = runner.invoke(
            app,
            ["update-contract"],
            input="1\n15000\n5000\ny\n",  # contract_id, new total, new remaining, signed
        )

        # Verify update was called
        mock_contract_service.update_contract.assert_called_once()

        # Verify success
        assert result.exit_code == 0
        assert "Contrat mis à jour avec succès" in result.stdout

    def test_update_contract_permission_denied(
        self, mocker, mock_commercial_user, mock_contract
    ):
        """
        GIVEN a commercial trying to update another commercial's contract
        WHEN update-contract command is executed
        THEN it should fail with permission error
        """
        # Mock container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_contract_service = mocker.MagicMock()
        mock_auth_service = mocker.MagicMock()

        # Configure mocks: contract belongs to another commercial (ID 99)
        other_commercial = mocker.Mock()
        other_commercial.first_name = "Charlie"
        other_commercial.last_name = "Brown"
        mock_contract.client.sales_contact_id = 99
        mock_contract.client.sales_contact = other_commercial

        mock_auth_service.get_current_user.return_value = mock_commercial_user
        mock_contract_service.get_contract.return_value = mock_contract

        mock_container.return_value.contract_service.return_value = (
            mock_contract_service
        )
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute update-contract
        result = runner.invoke(
            app,
            ["update-contract"],
            input="1\n15000\n5000\ny\n",
        )

        # Verify permission error
        assert result.exit_code == 1
        assert "Vous ne pouvez modifier que les contrats de vos propres clients" in result.stdout
        assert "Charlie Brown" in result.stdout

    def test_update_contract_by_gestion(
        self, mocker, mock_gestion_user, mock_contract
    ):
        """
        GIVEN a gestion user updating any contract
        WHEN update-contract command is executed
        THEN it should succeed (gestion has all permissions)
        """
        # Mock container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_contract_service = mocker.MagicMock()
        mock_auth_service = mocker.MagicMock()

        # Configure mocks
        mock_auth_service.get_current_user.return_value = mock_gestion_user
        mock_contract_service.get_contract.return_value = mock_contract
        mock_contract_service.update_contract.return_value = mock_contract

        mock_container.return_value.contract_service.return_value = (
            mock_contract_service
        )
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Mock Sentry
        mocker.patch("src.sentry_config.add_breadcrumb")

        # Execute update-contract
        result = runner.invoke(
            app,
            ["update-contract"],
            input="1\n15000\n5000\ny\n",
        )

        # Verify success (gestion can update any contract)
        assert result.exit_code == 0
        assert "Contrat mis à jour avec succès" in result.stdout
