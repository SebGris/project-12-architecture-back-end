"""
Tests unitaires pour la logique métier CLI (business_logic.py).

Ces tests vérifient la logique pure sans dépendances Typer/CLI.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from src.cli import business_logic as bl
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event
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
        result = bl.create_user_logic(
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
        """GIVEN valid data / WHEN bl.create_client_logic() / THEN creates client"""
        # Arrange
        mock_client_service = mocker.Mock()
        mock_user_service = mocker.Mock()
        mock_container.client_service.return_value = mock_client_service
        mock_container.user_service.return_value = mock_user_service

        mock_user_service.get_user.return_value = mock_commercial_user
        mock_client_service.create_client.return_value = mock_client

        # Act
        result = bl.create_client_logic(
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
        """GIVEN invalid sales_contact_id / WHEN bl.create_client_logic() / THEN raises ValueError"""
        # Arrange
        mock_user_service = mocker.Mock()
        mock_container.user_service.return_value = mock_user_service
        mock_user_service.get_user.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="introuvable"):
            bl.create_client_logic(
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
        """GIVEN authorized user / WHEN bl.update_client_logic() / THEN updates client"""
        # Arrange
        mock_client_service = mocker.Mock()
        mock_container.client_service.return_value = mock_client_service

        mock_client_service.get_client.return_value = mock_client
        updated_client = mocker.Mock(spec=Client)
        updated_client.phone = "0999999999"
        mock_client_service.update_client.return_value = updated_client

        # Act
        result = bl.update_client_logic(
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
        """GIVEN unauthorized user / WHEN bl.update_client_logic() / THEN raises ValueError"""
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
            bl.update_client_logic(
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
        """GIVEN authorized user and client / WHEN bl.create_contract_logic() / THEN creates contract"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_client_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service
        mock_container.client_service.return_value = mock_client_service

        mock_client_service.get_client.return_value = mock_client
        mock_contract_service.create_contract.return_value = mock_contract

        # Act
        result = bl.create_contract_logic(
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
        """GIVEN invalid amounts / WHEN bl.create_contract_logic() / THEN raises ValueError"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_client_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service
        mock_container.client_service.return_value = mock_client_service

        mock_client_service.get_client.return_value = mock_client

        # Act & Assert - remaining > total
        with pytest.raises(ValueError, match="dépasser le montant total"):
            bl.create_contract_logic(
                client_id=10,
                total_amount=Decimal("10000.00"),
                remaining_amount=Decimal("15000.00"),  # More than total
                is_signed=False,
                current_user=mock_commercial_user,
                container=mock_container
            )


class TestUpdateContractLogic:
    """Test update_contract_logic function."""

    def test_update_contract_success(self, mocker, mock_container, mock_commercial_user, mock_contract):
        """GIVEN authorized user / WHEN bl.update_contract_logic() / THEN updates contract"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service

        # Ensure contract belongs to current user
        mock_contract.client.sales_contact_id = mock_commercial_user.id
        mock_contract.total_amount = Decimal("10000.00")
        mock_contract.remaining_amount = Decimal("10000.00")
        mock_contract_service.get_contract.return_value = mock_contract

        updated_contract = mocker.Mock(spec=Contract)
        updated_contract.total_amount = Decimal("15000.00")
        updated_contract.is_signed = True
        mock_contract_service.update_contract.return_value = updated_contract

        # Act
        result = bl.update_contract_logic(
            contract_id=100,
            total_amount=Decimal("15000.00"),
            remaining_amount=None,
            is_signed=True,
            current_user=mock_commercial_user,
            container=mock_container
        )

        # Assert
        mock_contract_service.get_contract.assert_called_once_with(100)
        mock_contract_service.update_contract.assert_called_once()
        assert result == updated_contract

    def test_update_contract_validates_negative_amounts(self, mocker, mock_container, mock_commercial_user, mock_contract):
        """GIVEN negative amounts / WHEN bl.update_contract_logic() / THEN raises ValueError"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service

        # Ensure contract belongs to current user
        mock_contract.client.sales_contact_id = mock_commercial_user.id
        mock_contract_service.get_contract.return_value = mock_contract

        # Act & Assert - negative total
        with pytest.raises(ValueError, match="montant total doit être positif"):
            bl.update_contract_logic(
                contract_id=100,
                total_amount=Decimal("-1000.00"),
                remaining_amount=None,
                is_signed=None,
                current_user=mock_commercial_user,
                container=mock_container
            )

    def test_update_contract_validates_remaining_exceeds_total(self, mocker, mock_container, mock_commercial_user, mock_contract):
        """GIVEN remaining > total / WHEN bl.update_contract_logic() / THEN raises ValueError"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service

        # Ensure contract belongs to current user
        mock_contract.client.sales_contact_id = mock_commercial_user.id
        # Set initial contract values
        mock_contract.total_amount = Decimal("10000.00")
        mock_contract.remaining_amount = Decimal("5000.00")
        mock_contract_service.get_contract.return_value = mock_contract

        # Act & Assert - update remaining to exceed total
        with pytest.raises(ValueError, match="dépasser le montant total"):
            bl.update_contract_logic(
                contract_id=100,
                total_amount=None,
                remaining_amount=Decimal("15000.00"),  # Exceeds current total
                is_signed=None,
                current_user=mock_commercial_user,
                container=mock_container
            )

    def test_update_contract_unauthorized(self, mocker, mock_container, mock_commercial_user, mock_contract):
        """GIVEN unauthorized user / WHEN bl.update_contract_logic() / THEN raises ValueError"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service

        # Contract belongs to another commercial
        mock_contract.client.sales_contact_id = 999
        mock_contract.client.first_name = "Other"
        mock_contract.client.last_name = "Client"
        mock_contract.client.sales_contact = mocker.Mock()
        mock_contract.client.sales_contact.first_name = "Other"
        mock_contract.client.sales_contact.last_name = "Commercial"
        mock_contract_service.get_contract.return_value = mock_contract

        # Act & Assert
        with pytest.raises(ValueError, match="propres clients"):
            bl.update_contract_logic(
                contract_id=100,
                total_amount=Decimal("20000.00"),
                remaining_amount=None,
                is_signed=None,
                current_user=mock_commercial_user,
                container=mock_container
            )


class TestUpdateContractPaymentLogic:
    """Test update_contract_payment_logic function."""

    def test_update_payment_success(self, mocker, mock_container, mock_commercial_user, mock_client, mock_contract):
        """GIVEN authorized user / WHEN bl.update_contract_payment_logic() / THEN updates payment"""
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
        result = bl.update_contract_payment_logic(
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
        """GIVEN authorized user / WHEN bl.sign_contract_logic() / THEN signs contract"""
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
        result = bl.sign_contract_logic(
            contract_id=100,
            current_user=mock_commercial_user,
            container=mock_container
        )

        # Assert
        mock_contract_service.sign_contract.assert_called_once_with(100)
        assert result.is_signed is True

    def test_sign_contract_already_signed(self, mocker, mock_container, mock_commercial_user, mock_client, mock_contract):
        """GIVEN already signed contract / WHEN bl.sign_contract_logic() / THEN raises ValueError"""
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
            bl.sign_contract_logic(
                contract_id=100,
                current_user=mock_commercial_user,
                container=mock_container
            )


class TestCreateEventLogic:
    """Test create_event_logic function."""

    def test_create_event_success(self, mocker, mock_container, mock_contract):
        """GIVEN valid event data / WHEN bl.create_event_logic() / THEN creates event"""
        # Arrange
        mock_event_service = mocker.Mock()
        mock_contract_service = mocker.Mock()
        mock_user_service = mocker.Mock()
        mock_container.event_service.return_value = mock_event_service
        mock_container.contract_service.return_value = mock_contract_service
        mock_container.user_service.return_value = mock_user_service

        mock_contract_service.get_contract.return_value = mock_contract

        mock_support_user = mocker.Mock(spec=User)
        mock_support_user.id = 5
        mock_support_user.department = Department.SUPPORT
        mock_user_service.get_user.return_value = mock_support_user

        mock_event = mocker.Mock(spec=Event)
        mock_event.id = 1
        mock_event.name = "Event Test"
        mock_event_service.create_event.return_value = mock_event

        start_dt = datetime(2025, 11, 15, 18, 0)
        end_dt = datetime(2025, 11, 15, 23, 0)

        # Act
        result = bl.create_event_logic(
            name="Event Test",
            contract_id=100,
            event_start=start_dt,
            event_end=end_dt,
            location="Test Location",
            attendees=100,
            notes="Test notes",
            support_contact_id=5,
            container=mock_container
        )

        # Assert
        mock_contract_service.get_contract.assert_called_once_with(100)
        mock_user_service.get_user.assert_called_once_with(5)
        mock_event_service.create_event.assert_called_once_with(
            name="Event Test",
            contract_id=100,
            event_start=start_dt,
            event_end=end_dt,
            location="Test Location",
            attendees=100,
            notes="Test notes",
            support_contact_id=5
        )
        assert result == mock_event

    def test_create_event_contract_not_found(self, mocker, mock_container):
        """GIVEN invalid contract_id / WHEN bl.create_event_logic() / THEN raises ValueError"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service
        mock_contract_service.get_contract.return_value = None

        start_dt = datetime(2025, 11, 15, 18, 0)
        end_dt = datetime(2025, 11, 15, 23, 0)

        # Act & Assert
        with pytest.raises(ValueError, match="n'existe pas"):
            bl.create_event_logic(
                name="Event Test",
                contract_id=999,
                event_start=start_dt,
                event_end=end_dt,
                location="Test Location",
                attendees=100,
                notes=None,
                support_contact_id=None,
                container=mock_container
            )

    def test_create_event_invalid_name(self, mocker, mock_container, mock_contract):
        """GIVEN short event name / WHEN bl.create_event_logic() / THEN raises ValueError"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service
        mock_contract_service.get_contract.return_value = mock_contract

        start_dt = datetime(2025, 11, 15, 18, 0)
        end_dt = datetime(2025, 11, 15, 23, 0)

        # Act & Assert
        with pytest.raises(ValueError, match="au moins 3 caractères"):
            bl.create_event_logic(
                name="AB",  # Too short
                contract_id=100,
                event_start=start_dt,
                event_end=end_dt,
                location="Test Location",
                attendees=100,
                notes=None,
                support_contact_id=None,
                container=mock_container
            )

    def test_create_event_invalid_dates(self, mocker, mock_container, mock_contract):
        """GIVEN end date before start / WHEN bl.create_event_logic() / THEN raises ValueError"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service
        mock_contract_service.get_contract.return_value = mock_contract

        start_dt = datetime(2025, 11, 15, 23, 0)
        end_dt = datetime(2025, 11, 15, 18, 0)  # Before start

        # Act & Assert
        with pytest.raises(ValueError, match="après la date de début"):
            bl.create_event_logic(
                name="Event Test",
                contract_id=100,
                event_start=start_dt,
                event_end=end_dt,
                location="Test Location",
                attendees=100,
                notes=None,
                support_contact_id=None,
                container=mock_container
            )

    def test_create_event_negative_attendees(self, mocker, mock_container, mock_contract):
        """GIVEN negative attendees / WHEN bl.create_event_logic() / THEN raises ValueError"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service
        mock_contract_service.get_contract.return_value = mock_contract

        start_dt = datetime(2025, 11, 15, 18, 0)
        end_dt = datetime(2025, 11, 15, 23, 0)

        # Act & Assert
        with pytest.raises(ValueError, match="ne peut pas être négatif"):
            bl.create_event_logic(
                name="Event Test",
                contract_id=100,
                event_start=start_dt,
                event_end=end_dt,
                location="Test Location",
                attendees=-10,  # Negative
                notes=None,
                support_contact_id=None,
                container=mock_container
            )

    def test_create_event_support_contact_not_found(self, mocker, mock_container, mock_contract):
        """GIVEN invalid support_contact_id / WHEN bl.create_event_logic() / THEN raises ValueError"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_user_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service
        mock_container.user_service.return_value = mock_user_service

        mock_contract_service.get_contract.return_value = mock_contract
        mock_user_service.get_user.return_value = None

        start_dt = datetime(2025, 11, 15, 18, 0)
        end_dt = datetime(2025, 11, 15, 23, 0)

        # Act & Assert
        with pytest.raises(ValueError, match="n'existe pas"):
            bl.create_event_logic(
                name="Event Test",
                contract_id=100,
                event_start=start_dt,
                event_end=end_dt,
                location="Test Location",
                attendees=100,
                notes=None,
                support_contact_id=999,
                container=mock_container
            )

    def test_create_event_support_contact_wrong_department(self, mocker, mock_container, mock_contract):
        """GIVEN support contact not in SUPPORT dept / WHEN bl.create_event_logic() / THEN raises ValueError"""
        # Arrange
        mock_contract_service = mocker.Mock()
        mock_user_service = mocker.Mock()
        mock_container.contract_service.return_value = mock_contract_service
        mock_container.user_service.return_value = mock_user_service

        mock_contract_service.get_contract.return_value = mock_contract

        mock_commercial_user = mocker.Mock(spec=User)
        mock_commercial_user.id = 5
        mock_commercial_user.first_name = "Commercial"
        mock_commercial_user.last_name = "User"
        mock_commercial_user.department = Department.COMMERCIAL  # Not SUPPORT
        mock_user_service.get_user.return_value = mock_commercial_user

        start_dt = datetime(2025, 11, 15, 18, 0)
        end_dt = datetime(2025, 11, 15, 23, 0)

        # Act & Assert
        with pytest.raises(ValueError, match="n'est pas du département SUPPORT"):
            bl.create_event_logic(
                name="Event Test",
                contract_id=100,
                event_start=start_dt,
                event_end=end_dt,
                location="Test Location",
                attendees=100,
                notes=None,
                support_contact_id=5,
                container=mock_container
            )
