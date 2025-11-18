"""
Tests unitaires pour la logique métier CLI (business_logic.py).

Ces tests vérifient la logique pure sans dépendances Typer/CLI.
"""

import pytest
from decimal import Decimal

from src.cli.business_logic import (
    create_user_logic,
    create_client_logic,
    update_client_logic,
    create_contract_logic,
    update_contract_payment_logic,
    sign_contract_logic
)
from src.models.client import Client
from src.models.contract import Contract
from src.models.user import Department, User


@pytest.fixture
def mock_container(mocker):
    """Create a mock Container with services."""
    return mocker.Mock()


@pytest.fixture
def mock_commercial_user(mocker):
    """Create a mock commercial user."""
    user = mocker.Mock(spec=User)
    user.id = 1
    user.username = "commercial1"
    user.department = Department.COMMERCIAL
    return user


@pytest.fixture
def mock_client(mocker):
    """Create a mock client."""
    client = mocker.Mock(spec=Client)
    client.id = 10
    client.first_name = "John"
    client.last_name = "Doe"
    client.email = "john@example.com"
    client.phone = "0123456789"
    client.company_name = "ACME Corp"
    client.sales_contact_id = 1
    return client


@pytest.fixture
def mock_contract(mocker):
    """Create a mock contract."""
    contract = mocker.Mock(spec=Contract)
    contract.id = 100
    contract.client_id = 10
    contract.total_amount = Decimal("10000.00")
    contract.remaining_amount = Decimal("5000.00")
    contract.is_signed = False
    return contract


class TestCreateUserLogic:
    """Test create_user_logic function."""

    def test_create_user_success(self, mocker, mock_container):
        """GIVEN valid user data / WHEN create_user_logic() / THEN creates user"""
        # Arrange
        mock_user_service = mocker.Mock()
        mock_container.user_service.return_value = mock_user_service

        mock_user = mocker.Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "newuser"
        mock_user.department = Department.COMMERCIAL
        mock_user_service.create_user.return_value = mock_user

        # Act
        result = create_user_logic(
            username="newuser",
            first_name="New",
            last_name="User",
            email="newuser@example.com",
            phone="0123456789",
            password="SecurePass123!",
            department=Department.COMMERCIAL,
            container=mock_container
        )

        # Assert
        mock_user_service.create_user.assert_called_once_with(
            username="newuser",
            first_name="New",
            last_name="User",
            email="newuser@example.com",
            phone="0123456789",
            password="SecurePass123!",
            department=Department.COMMERCIAL
        )
        assert result == mock_user
        assert result.username == "newuser"


class TestCreateClientLogic:
    """Test create_client_logic function."""

    def test_create_client_success(self, mocker, mock_container, mock_commercial_user, mock_client):
        """GIVEN valid data / WHEN create_client_logic() / THEN creates client"""
        # Arrange
        mock_client_service = mocker.Mock()
        mock_user_service = mocker.Mock()
        mock_container.client_service.return_value = mock_client_service
        mock_container.user_service.return_value = mock_user_service

        mock_user_service.get_user.return_value = mock_commercial_user
        mock_client_service.create_client.return_value = mock_client

        # Act
        result = create_client_logic(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="0123456789",
            company_name="ACME Corp",
            sales_contact_id=1,
            container=mock_container
        )

        # Assert
        mock_user_service.get_user.assert_called_once_with(1)
        mock_client_service.create_client.assert_called_once()
        assert result == mock_client

    def test_create_client_sales_contact_not_found(self, mocker, mock_container):
        """GIVEN invalid sales_contact_id / WHEN create_client_logic() / THEN raises ValueError"""
        # Arrange
        mock_user_service = mocker.Mock()
        mock_container.user_service.return_value = mock_user_service
        mock_user_service.get_user.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="introuvable"):
            create_client_logic(
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                phone="0123456789",
                company_name="ACME Corp",
                sales_contact_id=999,
                container=mock_container
            )


class TestUpdateClientLogic:
    """Test update_client_logic function."""

    def test_update_client_success(self, mocker, mock_container, mock_commercial_user, mock_client):
        """GIVEN authorized user / WHEN update_client_logic() / THEN updates client"""
        # Arrange
        mock_client_service = mocker.Mock()
        mock_container.client_service.return_value = mock_client_service

        mock_client_service.get_client.return_value = mock_client
        updated_client = mocker.Mock(spec=Client)
        updated_client.phone = "0999999999"
        mock_client_service.update_client.return_value = updated_client

        # Act
        result = update_client_logic(
            client_id=10,
            first_name=None,
            last_name=None,
            email=None,
            phone="0999999999",
            company_name=None,
            current_user=mock_commercial_user,
            container=mock_container
        )

        # Assert
        mock_client_service.get_client.assert_called_once_with(10)
        mock_client_service.update_client.assert_called_once()
        assert result.phone == "0999999999"

    def test_update_client_not_authorized(self, mocker, mock_container, mock_commercial_user, mock_client):
        """GIVEN unauthorized user / WHEN update_client_logic() / THEN raises ValueError"""
        # Arrange
        mock_client_service = mocker.Mock()
        mock_container.client_service.return_value = mock_client_service

        # Client belongs to another commercial
        mock_client.sales_contact_id = 999
        mock_client.sales_contact = mocker.Mock()
        mock_client.sales_contact.first_name = "Other"
        mock_client.sales_contact.last_name = "Commercial"
        mock_client_service.get_client.return_value = mock_client

        # Act & Assert
        with pytest.raises(ValueError, match="propres clients"):
            update_client_logic(
                client_id=10,
                first_name=None,
                last_name=None,
                email=None,
                phone="0999999999",
                company_name=None,
                current_user=mock_commercial_user,
                container=mock_container
            )


class TestCreateContractLogic:
    """Test create_contract_logic function."""

    def test_create_contract_success(self, mocker, mock_container, mock_commercial_user, mock_client, mock_contract):
        """GIVEN authorized user and client / WHEN create_contract_logic() / THEN creates contract"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_client_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service
        mock_container.client_service.return_value = mock_client_service

        mock_client_service.get_client.return_value = mock_client
        mock_contract_service.create_contract.return_value = mock_contract

        # Act
        result = create_contract_logic(
            client_id=10,
            total_amount=Decimal("10000.00"),
            remaining_amount=Decimal("10000.00"),
            is_signed=False,
            current_user=mock_commercial_user,
            container=mock_container
        )

        # Assert
        mock_client_service.get_client.assert_called_once_with(10)
        mock_contract_service.create_contract.assert_called_once_with(
            client_id=10,
            total_amount=Decimal("10000.00"),
            remaining_amount=Decimal("10000.00"),
            is_signed=False
        )
        assert result == mock_contract

    def test_create_contract_validates_amounts(self, mocker, mock_container, mock_commercial_user, mock_client):
        """GIVEN invalid amounts / WHEN create_contract_logic() / THEN raises ValueError"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_client_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service
        mock_container.client_service.return_value = mock_client_service

        mock_client_service.get_client.return_value = mock_client

        # Act & Assert - remaining > total
        with pytest.raises(ValueError, match="dépasser le montant total"):
            create_contract_logic(
                client_id=10,
                total_amount=Decimal("10000.00"),
                remaining_amount=Decimal("15000.00"),  # More than total
                is_signed=False,
                current_user=mock_commercial_user,
                container=mock_container
            )


class TestUpdateContractPaymentLogic:
    """Test update_contract_payment_logic function."""

    def test_update_payment_success(self, mocker, mock_container, mock_commercial_user, mock_client, mock_contract):
        """GIVEN authorized user / WHEN update_contract_payment_logic() / THEN updates payment"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_client_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service
        mock_container.client_service.return_value = mock_client_service

        mock_contract_service.get_contract.return_value = mock_contract
        mock_client_service.get_client.return_value = mock_client

        updated_contract = mocker.Mock(spec=Contract)
        updated_contract.remaining_amount = Decimal("2000.00")
        mock_contract_service.update_contract_payment.return_value = updated_contract

        # Act
        result = update_contract_payment_logic(
            contract_id=100,
            amount_paid=Decimal("3000.00"),
            current_user=mock_commercial_user,
            container=mock_container
        )

        # Assert
        mock_contract_service.update_contract_payment.assert_called_once()
        assert result.remaining_amount == Decimal("2000.00")


class TestSignContractLogic:
    """Test sign_contract_logic function."""

    def test_sign_contract_success(self, mocker, mock_container, mock_commercial_user, mock_client, mock_contract):
        """GIVEN authorized user / WHEN sign_contract_logic() / THEN signs contract"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_client_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service
        mock_container.client_service.return_value = mock_client_service

        mock_contract_service.get_contract.return_value = mock_contract
        mock_client_service.get_client.return_value = mock_client

        signed_contract = mocker.Mock(spec=Contract)
        signed_contract.is_signed = True
        mock_contract_service.sign_contract.return_value = signed_contract

        # Act
        result = sign_contract_logic(
            contract_id=100,
            current_user=mock_commercial_user,
            container=mock_container
        )

        # Assert
        mock_contract_service.sign_contract.assert_called_once_with(100)
        assert result.is_signed is True

    def test_sign_contract_already_signed(self, mocker, mock_container, mock_commercial_user, mock_client, mock_contract):
        """GIVEN already signed contract / WHEN sign_contract_logic() / THEN raises ValueError"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_client_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service
        mock_container.client_service.return_value = mock_client_service

        mock_contract.is_signed = True
        mock_contract_service.get_contract.return_value = mock_contract
        mock_client_service.get_client.return_value = mock_client

        # Act & Assert
        with pytest.raises(ValueError, match="déjà signé"):
            sign_contract_logic(
                contract_id=100,
                current_user=mock_commercial_user,
                container=mock_container
            )
