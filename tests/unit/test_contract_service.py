"""
Tests unitaires pour ContractService.

Tests couverts:
- create_contract() : création avec client_id
- get_contract() : récupération par ID
- update_contract() : mise à jour avec objet Contract entier
- update_contract_payment() : mise à jour du paiement avec contract_id
- sign_contract() : signature avec contract_id
- get_unsigned_contracts() : filtrage contrats non signés
- get_unpaid_contracts() : filtrage contrats non payés
"""

import pytest
from decimal import Decimal

from src.models.contract import Contract
from src.services.contract_service import ContractService


@pytest.fixture
def mock_repository(mocker):
    """Create a mock ContractRepository."""
    return mocker.Mock()


@pytest.fixture
def contract_service(mock_repository):
    """Create a ContractService instance with mock repository."""
    return ContractService(repository=mock_repository)


@pytest.fixture
def mock_contract():
    """Create a mock contract for testing."""
    return Contract(
        id=1,
        client_id=5,
        total_amount=Decimal("10000.00"),
        remaining_amount=Decimal("5000.00"),
        is_signed=False,
    )


class TestCreateContract:
    """Test create_contract method."""

    def test_create_contract_success(
        self, contract_service, mock_repository, mock_contract
    ):
        """GIVEN valid contract data / WHEN create_contract() / THEN contract created"""
        # Arrange
        mock_repository.add.return_value = mock_contract

        # Act
        result = contract_service.create_contract(
            client_id=5,
            total_amount=Decimal("10000.00"),
            remaining_amount=Decimal("5000.00"),
            is_signed=False,
        )

        # Assert
        mock_repository.add.assert_called_once()
        assert result == mock_contract
        # Vérifier que add() a été appelé avec un Contract
        call_args = mock_repository.add.call_args[0][0]
        assert isinstance(call_args, Contract)
        assert call_args.client_id == 5
        assert call_args.total_amount == Decimal("10000.00")

    def test_create_contract_signed(self, contract_service, mock_repository):
        """GIVEN is_signed=True / WHEN create_contract() / THEN contract created signed"""
        signed_contract = Contract(
            id=2,
            client_id=3,
            total_amount=Decimal("15000.00"),
            remaining_amount=Decimal("0.00"),
            is_signed=True,
        )
        mock_repository.add.return_value = signed_contract

        result = contract_service.create_contract(
            client_id=3,
            total_amount=Decimal("15000.00"),
            remaining_amount=Decimal("0.00"),
            is_signed=True,
        )

        assert result.is_signed is True

    def test_create_contract_default_unsigned(
        self, contract_service, mock_repository
    ):
        """GIVEN no is_signed parameter / WHEN create_contract() / THEN defaults to False"""
        unsigned_contract = Contract(
            id=3,
            client_id=7,
            total_amount=Decimal("8000.00"),
            remaining_amount=Decimal("8000.00"),
            is_signed=False,
        )
        mock_repository.add.return_value = unsigned_contract

        # is_signed a une valeur par défaut False
        result = contract_service.create_contract(
            client_id=7,
            total_amount=Decimal("8000.00"),
            remaining_amount=Decimal("8000.00"),
        )

        call_args = mock_repository.add.call_args[0][0]
        assert call_args.is_signed is False


class TestGetContract:
    """Test get_contract method."""

    def test_get_contract_found(
        self, contract_service, mock_repository, mock_contract
    ):
        """GIVEN existing contract_id / WHEN get_contract() / THEN returns contract"""
        mock_repository.get.return_value = mock_contract

        result = contract_service.get_contract(contract_id=1)

        mock_repository.get.assert_called_once_with(1)
        assert result == mock_contract
        assert result.id == 1

    def test_get_contract_not_found(self, contract_service, mock_repository):
        """GIVEN non-existing contract_id / WHEN get_contract() / THEN returns None"""
        mock_repository.get.return_value = None

        result = contract_service.get_contract(contract_id=999)

        mock_repository.get.assert_called_once_with(999)
        assert result is None


class TestUpdateContract:
    """Test update_contract method."""

    def test_update_contract_success(
        self, contract_service, mock_repository, mock_contract
    ):
        """GIVEN contract object / WHEN update_contract() / THEN contract updated"""
        # Arrange
        mock_contract.total_amount = Decimal("12000.00")
        mock_repository.update.return_value = mock_contract

        # Act - IMPORTANT: update_contract prend l'objet Contract entier
        result = contract_service.update_contract(contract=mock_contract)

        # Assert
        mock_repository.update.assert_called_once_with(mock_contract)
        assert result == mock_contract
        assert result.total_amount == Decimal("12000.00")


class TestUpdateContractPayment:
    """Test update_contract_payment method."""

    def test_update_contract_payment_success(
        self, contract_service, mock_repository, mock_contract
    ):
        """GIVEN contract_id and amount_paid / WHEN update_contract_payment() / THEN remaining updated"""
        # Arrange
        mock_repository.get.return_value = mock_contract
        mock_repository.update.return_value = mock_contract

        # Act - IMPORTANT: prend contract_id (int), pas objet Contract
        result = contract_service.update_contract_payment(
            contract_id=1, amount_paid=Decimal("2000.00")
        )

        # Assert
        mock_repository.get.assert_called_once_with(1)
        mock_repository.update.assert_called_once_with(mock_contract)
        assert result == mock_contract
        # remaining_amount était 5000, on paie 2000, reste 3000
        assert result.remaining_amount == Decimal("3000.00")

    def test_update_contract_payment_full_payment(
        self, contract_service, mock_repository, mock_contract
    ):
        """GIVEN full payment / WHEN update_contract_payment() / THEN remaining becomes 0"""
        mock_repository.get.return_value = mock_contract
        mock_repository.update.return_value = mock_contract

        # Payer le montant restant complet
        result = contract_service.update_contract_payment(
            contract_id=1, amount_paid=Decimal("5000.00")
        )

        assert result.remaining_amount == Decimal("0.00")

    def test_update_contract_payment_not_found(
        self, contract_service, mock_repository
    ):
        """GIVEN non-existing contract_id / WHEN update_contract_payment() / THEN returns None"""
        mock_repository.get.return_value = None

        result = contract_service.update_contract_payment(
            contract_id=999, amount_paid=Decimal("1000.00")
        )

        mock_repository.get.assert_called_once_with(999)
        mock_repository.update.assert_not_called()
        assert result is None


class TestSignContract:
    """Test sign_contract method."""

    def test_sign_contract_success(
        self, contract_service, mock_repository, mock_contract
    ):
        """GIVEN contract_id / WHEN sign_contract() / THEN is_signed becomes True"""
        # Arrange
        mock_repository.get.return_value = mock_contract
        mock_repository.update.return_value = mock_contract

        # Act - IMPORTANT: prend contract_id (int), pas objet Contract
        result = contract_service.sign_contract(contract_id=1)

        # Assert
        mock_repository.get.assert_called_once_with(1)
        mock_repository.update.assert_called_once_with(mock_contract)
        assert result == mock_contract
        assert result.is_signed is True

    def test_sign_contract_not_found(self, contract_service, mock_repository):
        """GIVEN non-existing contract_id / WHEN sign_contract() / THEN returns None"""
        mock_repository.get.return_value = None

        result = contract_service.sign_contract(contract_id=999)

        mock_repository.get.assert_called_once_with(999)
        mock_repository.update.assert_not_called()
        assert result is None


class TestGetUnsignedContracts:
    """Test get_unsigned_contracts method."""

    def test_get_unsigned_contracts(self, contract_service, mock_repository):
        """WHEN get_unsigned_contracts() / THEN returns list of unsigned contracts"""
        # Arrange
        unsigned_contracts = [
            Contract(
                id=1,
                client_id=5,
                total_amount=Decimal("10000.00"),
                remaining_amount=Decimal("5000.00"),
                is_signed=False,
            ),
            Contract(
                id=2,
                client_id=7,
                total_amount=Decimal("8000.00"),
                remaining_amount=Decimal("8000.00"),
                is_signed=False,
            ),
        ]
        mock_repository.get_unsigned_contracts.return_value = unsigned_contracts

        # Act
        result = contract_service.get_unsigned_contracts()

        # Assert
        mock_repository.get_unsigned_contracts.assert_called_once()
        assert len(result) == 2
        assert all(not contract.is_signed for contract in result)

    def test_get_unsigned_contracts_empty(self, contract_service, mock_repository):
        """GIVEN no unsigned contracts / WHEN get_unsigned_contracts() / THEN returns empty list"""
        mock_repository.get_unsigned_contracts.return_value = []

        result = contract_service.get_unsigned_contracts()

        assert result == []


class TestGetUnpaidContracts:
    """Test get_unpaid_contracts method."""

    def test_get_unpaid_contracts(self, contract_service, mock_repository):
        """WHEN get_unpaid_contracts() / THEN returns list of unpaid contracts"""
        # Arrange
        unpaid_contracts = [
            Contract(
                id=1,
                client_id=5,
                total_amount=Decimal("10000.00"),
                remaining_amount=Decimal("5000.00"),
                is_signed=True,
            ),
            Contract(
                id=3,
                client_id=9,
                total_amount=Decimal("12000.00"),
                remaining_amount=Decimal("12000.00"),
                is_signed=False,
            ),
        ]
        mock_repository.get_unpaid_contracts.return_value = unpaid_contracts

        # Act
        result = contract_service.get_unpaid_contracts()

        # Assert
        mock_repository.get_unpaid_contracts.assert_called_once()
        assert len(result) == 2
        assert all(contract.remaining_amount > 0 for contract in result)

    def test_get_unpaid_contracts_empty(self, contract_service, mock_repository):
        """GIVEN no unpaid contracts / WHEN get_unpaid_contracts() / THEN returns empty list"""
        mock_repository.get_unpaid_contracts.return_value = []

        result = contract_service.get_unpaid_contracts()

        assert result == []
