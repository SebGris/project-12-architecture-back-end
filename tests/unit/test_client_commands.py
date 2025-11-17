"""
Tests unitaires pour les commandes CLI de gestion des clients.

Tests couverts:
- create-client : création avec auto-assignation COMMERCIAL
- create-client : erreurs (email dupliqué, sales_contact invalide)

Note: Les tests update-client sont dans test_crud_commands.py
"""

import pytest
from decimal import Decimal
from typer.testing import CliRunner
from sqlalchemy.exc import IntegrityError

from src.cli.commands import app
from src.models.user import Department, User
from src.models.client import Client

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
    user.phone = "+33 1 23 45 67 90"
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


class TestCreateClientCommand:
    """Test create-client command."""

    def test_create_client_with_commercial_auto_assign(
        self, mocker, mock_commercial_user, mock_client
    ):
        """
        GIVEN commercial user and client data with sales_contact_id=0
        WHEN create-client is executed
        THEN client created with auto-assigned commercial
        """
        # Mock Container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_client_service = mocker.MagicMock()
        mock_user_service = mocker.MagicMock()
        mock_auth_service = mocker.MagicMock()

        # Setup auth service to return commercial user
        mock_auth_service.get_current_user.return_value = mock_commercial_user

        # Setup user service to return commercial user for validation
        mock_user_service.get_user.return_value = mock_commercial_user

        # Setup client service to return created client
        mock_client_service.create_client.return_value = mock_client

        # Wire container
        mock_container.return_value.client_service.return_value = (
            mock_client_service
        )
        mock_container.return_value.user_service.return_value = mock_user_service
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute command with input (sales_contact_id=0 triggers auto-assign)
        result = runner.invoke(
            app,
            ["create-client"],
            input="Jean\nDupont\njean.dupont@example.com\n0612345678\nDupontCorp\n0\n",
        )

        # Verify
        assert result.exit_code == 0
        assert "créé avec succès" in result.stdout
        assert "Jean Dupont" in result.stdout
        mock_client_service.create_client.assert_called_once_with(
            first_name="Jean",
            last_name="Dupont",
            email="jean.dupont@example.com",
            phone="0612345678",
            company_name="DupontCorp",
            sales_contact_id=2,  # Auto-assigned from current user
        )

    def test_create_client_with_gestion_explicit_sales_contact(
        self, mocker, mock_gestion_user, mock_commercial_user, mock_client
    ):
        """
        GIVEN gestion user and explicit sales_contact_id
        WHEN create-client is executed
        THEN client created with specified commercial
        """
        # Mock Container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_client_service = mocker.MagicMock()
        mock_user_service = mocker.MagicMock()
        mock_auth_service = mocker.MagicMock()

        # Setup auth service to return gestion user
        mock_auth_service.get_current_user.return_value = mock_gestion_user

        # Setup user service to return commercial user for validation
        mock_user_service.get_user.return_value = mock_commercial_user

        # Setup client service
        mock_client_service.create_client.return_value = mock_client

        # Wire container
        mock_container.return_value.client_service.return_value = (
            mock_client_service
        )
        mock_container.return_value.user_service.return_value = mock_user_service
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute command with explicit sales_contact_id=2
        result = runner.invoke(
            app,
            ["create-client"],
            input="Jean\nDupont\njean.dupont@example.com\n0612345678\nDupontCorp\n2\n",
        )

        # Verify
        assert result.exit_code == 0
        assert "créé avec succès" in result.stdout
        mock_client_service.create_client.assert_called_once_with(
            first_name="Jean",
            last_name="Dupont",
            email="jean.dupont@example.com",
            phone="0612345678",
            company_name="DupontCorp",
            sales_contact_id=2,
        )

    def test_create_client_duplicate_email_error(
        self, mocker, mock_commercial_user
    ):
        """
        GIVEN client data with duplicate email
        WHEN create-client is executed
        THEN error displayed about duplicate email
        """
        # Mock Container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_client_service = mocker.MagicMock()
        mock_user_service = mocker.MagicMock()
        mock_auth_service = mocker.MagicMock()

        # Setup services
        mock_auth_service.get_current_user.return_value = mock_commercial_user
        mock_user_service.get_user.return_value = mock_commercial_user

        # Simulate IntegrityError for duplicate email
        mock_orig = mocker.Mock()
        mock_orig.__str__ = lambda self: "UNIQUE constraint failed: client.email"
        integrity_error = IntegrityError("statement", "params", mock_orig)
        mock_client_service.create_client.side_effect = integrity_error

        # Wire container
        mock_container.return_value.client_service.return_value = (
            mock_client_service
        )
        mock_container.return_value.user_service.return_value = mock_user_service
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute command
        result = runner.invoke(
            app,
            ["create-client"],
            input="Jean\nDupont\njean.dupont@example.com\n0612345678\nDupontCorp\n0\n",
        )

        # Verify
        assert result.exit_code == 1
        assert "existe déjà" in result.stdout

    def test_create_client_invalid_sales_contact_not_found(
        self, mocker, mock_gestion_user
    ):
        """
        GIVEN sales_contact_id that doesn't exist
        WHEN create-client is executed
        THEN error displayed about invalid user
        """
        # Mock Container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_client_service = mocker.MagicMock()
        mock_user_service = mocker.MagicMock()
        mock_auth_service = mocker.MagicMock()

        # Setup services
        mock_auth_service.get_current_user.return_value = mock_gestion_user
        mock_user_service.get_user.return_value = None  # User not found

        # Wire container
        mock_container.return_value.client_service.return_value = (
            mock_client_service
        )
        mock_container.return_value.user_service.return_value = mock_user_service
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute command with invalid sales_contact_id=999
        result = runner.invoke(
            app,
            ["create-client"],
            input="Jean\nDupont\njean.dupont@example.com\n0612345678\nDupontCorp\n999\n",
        )

        # Verify
        assert result.exit_code == 1
        assert "n'existe pas" in result.stdout

    def test_create_client_gestion_without_sales_contact_error(
        self, mocker, mock_gestion_user
    ):
        """
        GIVEN gestion user with sales_contact_id=0
        WHEN create-client is executed
        THEN error displayed (GESTION cannot auto-assign)
        """
        # Mock Container and services
        mock_container = mocker.patch("src.cli.commands.Container")
        mock_client_service = mocker.MagicMock()
        mock_user_service = mocker.MagicMock()
        mock_auth_service = mocker.MagicMock()

        # Setup auth service to return gestion user
        mock_auth_service.get_current_user.return_value = mock_gestion_user

        # Wire container
        mock_container.return_value.client_service.return_value = (
            mock_client_service
        )
        mock_container.return_value.user_service.return_value = mock_user_service
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute command with sales_contact_id=0 (should fail for GESTION)
        result = runner.invoke(
            app,
            ["create-client"],
            input="Jean\nDupont\njean.dupont@example.com\n0612345678\nDupontCorp\n0\n",
        )

        # Verify
        assert result.exit_code == 1
        assert "spécifier un ID" in result.stdout or "contact commercial" in result.stdout
