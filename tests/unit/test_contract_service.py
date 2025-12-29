"""Unit tests for ContractService.

Tests covered:
- create_contract(): Contract creation with validation
- get_contract(): Contract retrieval by ID
- update_contract(): Contract updates (amount, signature status)
- update_contract_payment(): Payment recording with remaining amount calculation
- sign_contract(): Contract signature
- get_unsigned_contracts(): Unsigned contracts filtering
- get_unpaid_contracts(): Unpaid contracts filtering
- get_signed_contracts(): Signed contracts filtering
- get_contracts_by_client(): Contracts by client ID
- get_all_contracts(): Contracts listing with pagination
- count_contracts(): Total contracts count

Implementation notes:
- Uses real SQLite in-memory database
- Zero mocks - uses real SqlAlchemyContractRepository
- Tests business logic including payment calculations
"""

import pytest
from decimal import Decimal

from src.models.contract import Contract
from src.repositories.sqlalchemy_contract_repository import (
    SqlAlchemyContractRepository,
)
from src.services.contract_service import ContractService


@pytest.fixture
def contract_service(db_session):
    """Create a ContractService instance with real repository and SQLite DB."""
    repository = SqlAlchemyContractRepository(session=db_session)
    return ContractService(repository=repository)


class TestCreateContract:
    """Test create_contract method."""

    def test_create_contract_success(
        self, contract_service, test_clients, db_session
    ):
        """GIVEN valid contract data / WHEN create_contract() / THEN contract created"""
        # Arrange
        client = test_clients["kevin"]

        # Act
        result = contract_service.create_contract(
            client_id=client.id,
            total_amount=Decimal("10000.00"),
            remaining_amount=Decimal("5000.00"),
            is_signed=False,
        )

        # Assert
        assert result is not None
        assert isinstance(result, Contract)
        assert result.id is not None
        assert result.client_id == client.id
        assert result.total_amount == Decimal("10000.00")
        assert result.remaining_amount == Decimal("5000.00")
        assert result.is_signed is False

        # Verify it's persisted in database
        db_contract = (
            db_session.query(Contract).filter_by(id=result.id).first()
        )
        assert db_contract is not None
        assert db_contract.client_id == client.id

    def test_create_contract_signed(
        self, contract_service, test_clients, db_session
    ):
        """GIVEN is_signed=True / WHEN create_contract() / THEN contract created signed"""
        client = test_clients["lou"]

        result = contract_service.create_contract(
            client_id=client.id,
            total_amount=Decimal("15000.00"),
            remaining_amount=Decimal("0.00"),
            is_signed=True,
        )

        assert result.is_signed is True

        # Verify persistence
        db_contract = (
            db_session.query(Contract).filter_by(id=result.id).first()
        )
        assert db_contract.is_signed is True

    def test_create_contract_default_unsigned(
        self, contract_service, test_clients, db_session
    ):
        """GIVEN no is_signed parameter / WHEN create_contract() / THEN defaults to False"""
        client = test_clients["jane"]

        # is_signed a une valeur par défaut False
        result = contract_service.create_contract(
            client_id=client.id,
            total_amount=Decimal("8000.00"),
            remaining_amount=Decimal("8000.00"),
        )

        assert result.is_signed is False

        # Verify persistence
        db_contract = (
            db_session.query(Contract).filter_by(id=result.id).first()
        )
        assert db_contract.is_signed is False


class TestGetContract:
    """Test get_contract method."""

    def test_get_contract_found(self, contract_service, test_contracts):
        """GIVEN existing contract_id / WHEN get_contract() / THEN returns contract"""
        existing_contract = test_contracts["signed_partial"]

        result = contract_service.get_contract(
            contract_id=existing_contract.id
        )

        assert result is not None
        assert result.id == existing_contract.id
        assert result.client_id == existing_contract.client_id

    def test_get_contract_not_found(self, contract_service):
        """GIVEN non-existing contract_id / WHEN get_contract() / THEN returns None"""
        result = contract_service.get_contract(contract_id=99999)

        assert result is None


class TestUpdateContract:
    """Test update_contract method."""

    def test_update_contract_success(
        self, contract_service, test_contracts, db_session
    ):
        """GIVEN contract object / WHEN update_contract() / THEN contract updated"""
        # Arrange
        contract = test_contracts["unsigned"]
        contract.total_amount = Decimal("35000.00")

        # Act - IMPORTANT: update_contract prend l'objet Contract entier
        result = contract_service.update_contract(contract=contract)

        # Assert
        assert result is not None
        assert result.total_amount == Decimal("35000.00")

        # Verify persistence
        db_session.expire_all()
        db_contract = (
            db_session.query(Contract).filter_by(id=contract.id).first()
        )
        assert db_contract.total_amount == Decimal("35000.00")


class TestUpdateContractPayment:
    """Test update_contract_payment method."""

    def test_update_contract_payment_success(
        self, contract_service, test_contracts, db_session
    ):
        """GIVEN contract_id and amount_paid / WHEN update_contract_payment() / THEN remaining updated"""
        # Arrange - use signed_partial with 10000 remaining
        contract = test_contracts["signed_partial"]
        initial_remaining = contract.remaining_amount
        assert initial_remaining == Decimal("10000.00")

        # Act - IMPORTANT: prend contract_id (int), pas objet Contract
        result = contract_service.update_contract_payment(
            contract_id=contract.id, amount_paid=Decimal("3000.00")
        )

        # Assert
        assert result is not None
        # remaining_amount était 10000, on paie 3000, reste 7000
        assert result.remaining_amount == Decimal("7000.00")

        # Verify persistence
        db_session.expire_all()
        db_contract = (
            db_session.query(Contract).filter_by(id=contract.id).first()
        )
        assert db_contract.remaining_amount == Decimal("7000.00")

    def test_update_contract_payment_full_payment(
        self, contract_service, test_contracts, db_session
    ):
        """GIVEN full payment / WHEN update_contract_payment() / THEN remaining becomes 0"""
        contract = test_contracts["signed_unpaid"]

        # Payer le montant restant complet
        result = contract_service.update_contract_payment(
            contract_id=contract.id, amount_paid=contract.remaining_amount
        )

        assert result.remaining_amount == Decimal("0.00")

        # Verify persistence
        db_session.expire_all()
        db_contract = (
            db_session.query(Contract).filter_by(id=contract.id).first()
        )
        assert db_contract.remaining_amount == Decimal("0.00")

    def test_update_contract_payment_not_found(self, contract_service):
        """GIVEN non-existing contract_id / WHEN update_contract_payment() / THEN returns None"""
        result = contract_service.update_contract_payment(
            contract_id=99999, amount_paid=Decimal("1000.00")
        )

        assert result is None


class TestSignContract:
    """Test sign_contract method."""

    def test_sign_contract_success(
        self, contract_service, test_contracts, db_session
    ):
        """GIVEN contract_id / WHEN sign_contract() / THEN is_signed becomes True"""
        # Arrange - use unsigned
        contract = test_contracts["unsigned"]
        assert contract.is_signed is False

        # Act - IMPORTANT: prend contract_id (int), pas objet Contract
        result = contract_service.sign_contract(contract_id=contract.id)

        # Assert
        assert result is not None
        assert result.is_signed is True

        # Verify persistence
        db_session.expire_all()
        db_contract = (
            db_session.query(Contract).filter_by(id=contract.id).first()
        )
        assert db_contract.is_signed is True

    def test_sign_contract_not_found(self, contract_service):
        """GIVEN non-existing contract_id / WHEN sign_contract() / THEN returns None"""
        result = contract_service.sign_contract(contract_id=99999)

        assert result is None


class TestGetUnsignedContracts:
    """Test get_unsigned_contracts method."""

    def test_get_unsigned_contracts(self, contract_service, test_contracts):
        """WHEN get_unsigned_contracts() / THEN returns list of unsigned contracts"""
        # Act
        result = contract_service.get_unsigned_contracts()

        # Assert - should include unsigned contract
        assert len(result) >= 1
        assert all(not contract.is_signed for contract in result)

        # Verify specific test contract is present
        contract_ids = [c.id for c in result]
        assert test_contracts["unsigned"].id in contract_ids

    def test_get_unsigned_contracts_excludes_signed(
        self, contract_service, test_contracts
    ):
        """GIVEN signed contracts exist / WHEN get_unsigned_contracts() / THEN excludes signed ones"""
        result = contract_service.get_unsigned_contracts()

        # Assert - should NOT include signed contracts
        contract_ids = [c.id for c in result]
        assert test_contracts["signed_partial"].id not in contract_ids
        assert test_contracts["signed_paid"].id not in contract_ids


class TestGetUnpaidContracts:
    """Test get_unpaid_contracts method."""

    def test_get_unpaid_contracts(self, contract_service, test_contracts):
        """WHEN get_unpaid_contracts() / THEN returns list of unpaid contracts"""
        # Act
        result = contract_service.get_unpaid_contracts()

        # Assert - should include contracts with remaining_amount > 0
        assert len(result) >= 3
        assert all(contract.remaining_amount > 0 for contract in result)

        # Verify specific test contracts are present
        contract_ids = [c.id for c in result]
        assert test_contracts["signed_partial"].id in contract_ids
        assert test_contracts["unsigned"].id in contract_ids
        assert test_contracts["signed_unpaid"].id in contract_ids

    def test_get_unpaid_contracts_excludes_paid(
        self, contract_service, test_contracts
    ):
        """GIVEN fully paid contract exists / WHEN get_unpaid_contracts() / THEN excludes it"""
        result = contract_service.get_unpaid_contracts()

        # Assert - should NOT include fully paid contract
        contract_ids = [c.id for c in result]
        assert test_contracts["signed_paid"].id not in contract_ids


class TestGetContractsByClient:
    """Test get_contracts_by_client method."""

    def test_get_contracts_by_client_success(
        self, contract_service, test_clients, test_contracts
    ):
        """GIVEN client with contracts / WHEN get_contracts_by_client() / THEN returns list"""
        # Arrange - Kevin has multiple contracts (signed_partial and unsigned)
        kevin = test_clients["kevin"]

        # Act
        result = contract_service.get_contracts_by_client(client_id=kevin.id)

        # Assert
        assert len(result) >= 2
        assert all(contract.client_id == kevin.id for contract in result)

        # Verify specific contracts are present
        contract_ids = [c.id for c in result]
        assert test_contracts["signed_partial"].id in contract_ids
        assert test_contracts["unsigned"].id in contract_ids

    def test_get_contracts_by_client_empty(
        self, contract_service, test_clients
    ):
        """GIVEN client with no contracts / WHEN get_contracts_by_client() / THEN returns empty list"""
        # Jane has only signed_unpaid contract, so we need a client with no contracts
        # Create a new client with no contracts
        result = contract_service.get_contracts_by_client(client_id=99999)

        assert result == []


class TestGetSignedContracts:
    """Test get_signed_contracts method."""

    def test_get_signed_contracts(self, contract_service, test_contracts):
        """WHEN get_signed_contracts() / THEN returns list of signed contracts"""
        result = contract_service.get_signed_contracts()

        # Assert - should include signed contracts
        assert len(result) >= 1
        assert all(contract.is_signed for contract in result)

        # Verify specific test contracts are present
        contract_ids = [c.id for c in result]
        assert test_contracts["signed_partial"].id in contract_ids
        assert test_contracts["signed_paid"].id in contract_ids

    def test_get_signed_contracts_excludes_unsigned(
        self, contract_service, test_contracts
    ):
        """GIVEN unsigned contracts exist / WHEN get_signed_contracts() / THEN excludes unsigned ones"""
        result = contract_service.get_signed_contracts()

        # Assert - should NOT include unsigned contracts
        contract_ids = [c.id for c in result]
        assert test_contracts["unsigned"].id not in contract_ids


class TestGetAllContracts:
    """Test get_all_contracts method with pagination."""

    def test_get_all_contracts_default_pagination(
        self, contract_service, test_contracts
    ):
        """GIVEN contracts in database / WHEN get_all_contracts() / THEN returns paginated list"""
        result = contract_service.get_all_contracts()

        assert len(result) >= 1
        assert isinstance(result, list)

    def test_get_all_contracts_with_offset_and_limit(
        self, contract_service, test_contracts
    ):
        """GIVEN contracts in database / WHEN get_all_contracts(offset, limit) / THEN returns correct slice"""
        result = contract_service.get_all_contracts(offset=0, limit=1)

        assert len(result) == 1

    def test_get_all_contracts_offset_beyond_data(
        self, contract_service, test_contracts
    ):
        """GIVEN offset beyond data / WHEN get_all_contracts() / THEN returns empty list"""
        result = contract_service.get_all_contracts(offset=1000, limit=10)

        assert result == []


class TestCountContracts:
    """Test count_contracts method."""

    def test_count_contracts_returns_total(self, contract_service, test_contracts):
        """GIVEN contracts in database / WHEN count_contracts() / THEN returns total count"""
        result = contract_service.count_contracts()

        assert result >= 4  # At least 4 contracts from test_contracts fixture
