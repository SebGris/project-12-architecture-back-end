"""
Tests unitaires pour ContractService.

Tests couverts:
- create_contract() : création avec validation
- update_contract() : mise à jour
- get_contract() : récupération par ID
- get_unpaid_contracts() : filtre contrats non soldés
- get_unsigned_contracts() : filtre contrats non signés
"""

import pytest
from decimal import Decimal
from src.services.contract_service import ContractService


@pytest.fixture
def mock_contract_repository(mocker):
    """Create a mock contract repository."""
    return mocker.Mock()


@pytest.fixture
def contract_service(mock_contract_repository):
    """Create a ContractService instance with mocked repository."""
    return ContractService(mock_contract_repository)


@pytest.fixture
def sample_contract(mocker):
    """Create a sample contract for testing."""
    contract = mocker.Mock()
    contract.id = 1
    contract.client_id = 1
    contract.total_amount = Decimal("10000.00")
    contract.remaining_amount = Decimal("2000.00")
    contract.is_signed = False
    return contract


class TestCreateContract:
    """Test create_contract method."""

    def test_create_contract_success(
        self, contract_service, mock_contract_repository, sample_contract
    ):
        """
        GIVEN valid contract data
        WHEN create_contract is called
        THEN contract should be created
        """
        # Configure mock
        mock_contract_repository.create.return_value = sample_contract

        # Call service
        result = contract_service.create_contract(
            client_id=1,
            total_amount=Decimal("10000.00"),
            remaining_amount=Decimal("2000.00"),
            is_signed=False,
        )

        # Verify repository was called
        mock_contract_repository.create.assert_called_once_with(
            client_id=1,
            total_amount=Decimal("10000.00"),
            remaining_amount=Decimal("2000.00"),
            is_signed=False,
        )

        # Verify result
        assert result == sample_contract


class TestUpdateContract:
    """Test update_contract method."""

    def test_update_contract_success(
        self, contract_service, mock_contract_repository, sample_contract
    ):
        """
        GIVEN an existing contract and update data
        WHEN update_contract is called
        THEN contract should be updated
        """
        # Configure mock
        updated_contract = sample_contract
        updated_contract.total_amount = Decimal("15000.00")
        updated_contract.remaining_amount = Decimal("5000.00")
        updated_contract.is_signed = True
        mock_contract_repository.update.return_value = updated_contract

        # Call service
        result = contract_service.update_contract(
            contract_id=1,
            total_amount=Decimal("15000.00"),
            remaining_amount=Decimal("5000.00"),
            is_signed=True,
        )

        # Verify repository was called
        mock_contract_repository.update.assert_called_once_with(
            contract_id=1,
            total_amount=Decimal("15000.00"),
            remaining_amount=Decimal("5000.00"),
            is_signed=True,
        )

        # Verify result
        assert result == updated_contract
        assert result.is_signed is True


class TestGetContract:
    """Test get_contract method."""

    def test_get_contract_found(
        self, contract_service, mock_contract_repository, sample_contract
    ):
        """
        GIVEN a contract ID that exists
        WHEN get_contract is called
        THEN the contract should be returned
        """
        # Configure mock
        mock_contract_repository.get_by_id.return_value = sample_contract

        # Call service
        result = contract_service.get_contract(1)

        # Verify
        mock_contract_repository.get_by_id.assert_called_once_with(1)
        assert result == sample_contract

    def test_get_contract_not_found(
        self, contract_service, mock_contract_repository
    ):
        """
        GIVEN a contract ID that does not exist
        WHEN get_contract is called
        THEN None should be returned
        """
        # Configure mock
        mock_contract_repository.get_by_id.return_value = None

        # Call service
        result = contract_service.get_contract(999)

        # Verify
        mock_contract_repository.get_by_id.assert_called_once_with(999)
        assert result is None


class TestGetUnpaidContracts:
    """Test get_unpaid_contracts method."""

    def test_get_unpaid_contracts(
        self, contract_service, mock_contract_repository, sample_contract
    ):
        """
        GIVEN contracts with remaining amounts > 0
        WHEN get_unpaid_contracts is called
        THEN unpaid contracts should be returned
        """
        # Configure mock
        unpaid_contracts = [sample_contract]
        mock_contract_repository.get_unpaid.return_value = unpaid_contracts

        # Call service
        result = contract_service.get_unpaid_contracts()

        # Verify
        mock_contract_repository.get_unpaid.assert_called_once()
        assert result == unpaid_contracts
        assert len(result) == 1

    def test_get_unpaid_contracts_empty(
        self, contract_service, mock_contract_repository
    ):
        """
        GIVEN no unpaid contracts
        WHEN get_unpaid_contracts is called
        THEN an empty list should be returned
        """
        # Configure mock
        mock_contract_repository.get_unpaid.return_value = []

        # Call service
        result = contract_service.get_unpaid_contracts()

        # Verify
        mock_contract_repository.get_unpaid.assert_called_once()
        assert result == []


class TestGetUnsignedContracts:
    """Test get_unsigned_contracts method."""

    def test_get_unsigned_contracts(
        self, contract_service, mock_contract_repository, sample_contract
    ):
        """
        GIVEN contracts with is_signed = False
        WHEN get_unsigned_contracts is called
        THEN unsigned contracts should be returned
        """
        # Configure mock
        unsigned_contracts = [sample_contract]
        mock_contract_repository.get_unsigned.return_value = unsigned_contracts

        # Call service
        result = contract_service.get_unsigned_contracts()

        # Verify
        mock_contract_repository.get_unsigned.assert_called_once()
        assert result == unsigned_contracts
        assert len(result) == 1
        assert result[0].is_signed is False

    def test_get_unsigned_contracts_empty(
        self, contract_service, mock_contract_repository
    ):
        """
        GIVEN no unsigned contracts
        WHEN get_unsigned_contracts is called
        THEN an empty list should be returned
        """
        # Configure mock
        mock_contract_repository.get_unsigned.return_value = []

        # Call service
        result = contract_service.get_unsigned_contracts()

        # Verify
        mock_contract_repository.get_unsigned.assert_called_once()
        assert result == []
