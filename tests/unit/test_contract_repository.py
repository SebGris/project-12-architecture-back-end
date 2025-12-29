"""
Integration tests for SqlAlchemyContractRepository.
"""

import pytest
from decimal import Decimal

from src.models.contract import Contract
from src.repositories.sqlalchemy_contract_repository import (
    SqlAlchemyContractRepository,
)


@pytest.fixture
def contract_repository(db_session):
    """Create a ContractRepository with the test database session."""
    return SqlAlchemyContractRepository(session=db_session)


class TestContractRepositoryGet:
    """Test get method."""

    def test_get_existing_contract(self, contract_repository, test_contracts):
        """GIVEN existing contract / WHEN get(contract_id) / THEN returns contract"""
        contract = test_contracts["signed_partial"]

        result = contract_repository.get(contract.id)

        assert result is not None
        assert result.id == contract.id
        assert result.total_amount == Decimal("50000.00")

    def test_get_nonexistent_contract(self, contract_repository):
        """GIVEN nonexistent contract_id / WHEN get() / THEN returns None"""
        result = contract_repository.get(99999)

        assert result is None


class TestContractRepositoryAdd:
    """Test add method."""

    def test_add_new_contract(
        self, contract_repository, test_clients, db_session
    ):
        """GIVEN new contract / WHEN add() / THEN contract saved with ID"""
        new_contract = Contract(
            client_id=test_clients["kevin"].id,
            total_amount=Decimal("60000.00"),
            remaining_amount=Decimal("60000.00"),
            is_signed=False,
        )

        result = contract_repository.add(new_contract)

        assert result.id is not None
        assert result.total_amount == Decimal("60000.00")

        # Verify it's in database
        db_contract = (
            db_session.query(Contract).filter_by(id=result.id).first()
        )
        assert db_contract is not None


class TestContractRepositoryUpdate:
    """Test update method."""

    def test_update_contract(
        self, contract_repository, test_contracts, db_session
    ):
        """GIVEN existing contract with changes / WHEN update() / THEN changes persisted"""
        contract = test_contracts["unsigned"]
        contract.is_signed = True
        contract.remaining_amount = Decimal("15000.00")

        result = contract_repository.update(contract)

        assert result.is_signed is True
        assert result.remaining_amount == Decimal("15000.00")

        # Verify changes persisted
        db_session.expire_all()
        db_contract = (
            db_session.query(Contract).filter_by(id=contract.id).first()
        )
        assert db_contract.is_signed is True


class TestContractRepositoryGetByClientId:
    """Test get_by_client_id method."""

    def test_get_by_client_id(
        self, contract_repository, test_contracts, test_clients
    ):
        """GIVEN client with contracts / WHEN get_by_client_id() / THEN returns client's contracts"""
        kevin = test_clients["kevin"]

        result = contract_repository.get_by_client_id(kevin.id)

        assert len(result) == 2
        assert all(c.client_id == kevin.id for c in result)


class TestContractRepositoryGetUnsignedContracts:
    """Test get_unsigned_contracts method."""

    def test_get_unsigned_contracts(self, contract_repository, test_contracts):
        """GIVEN unsigned contracts / WHEN get_unsigned_contracts() / THEN returns only unsigned"""
        result = contract_repository.get_unsigned_contracts()

        assert len(result) >= 1
        assert all(c.is_signed is False for c in result)


class TestContractRepositoryGetUnpaidContracts:
    """Test get_unpaid_contracts method."""

    def test_get_unpaid_contracts(self, contract_repository, test_contracts):
        """GIVEN contracts with remaining amount / WHEN get_unpaid_contracts() / THEN returns unpaid"""
        result = contract_repository.get_unpaid_contracts()

        assert len(result) >= 1
        assert all(c.remaining_amount > 0 for c in result)


class TestContractRepositoryGetSignedContracts:
    """Test get_signed_contracts method."""

    def test_get_signed_contracts(self, contract_repository, test_contracts):
        """GIVEN signed contracts / WHEN get_signed_contracts() / THEN returns only signed"""
        result = contract_repository.get_signed_contracts()

        assert len(result) >= 1
        assert all(c.is_signed is True for c in result)


class TestContractRepositoryExists:
    """Test exists method."""

    def test_exists_returns_true_for_existing_contract(
        self, contract_repository, test_contracts
    ):
        """GIVEN existing contract / WHEN exists() / THEN returns True"""
        contract = test_contracts["signed_partial"]

        result = contract_repository.exists(contract.id)

        assert result is True

    def test_exists_returns_false_for_nonexistent_contract(self, contract_repository):
        """GIVEN nonexistent contract_id / WHEN exists() / THEN returns False"""
        result = contract_repository.exists(99999)

        assert result is False


class TestContractRepositoryGetAll:
    """Test get_all method with pagination."""

    def test_get_all_default_pagination(self, contract_repository, test_contracts):
        """GIVEN contracts in database / WHEN get_all() / THEN returns paginated list"""
        result = contract_repository.get_all()

        assert len(result) >= 1
        assert isinstance(result, list)

    def test_get_all_with_offset_and_limit(self, contract_repository, test_contracts):
        """GIVEN contracts in database / WHEN get_all(offset, limit) / THEN returns correct slice"""
        result = contract_repository.get_all(offset=0, limit=1)

        assert len(result) == 1

    def test_get_all_offset_beyond_data(self, contract_repository, test_contracts):
        """GIVEN offset beyond data / WHEN get_all() / THEN returns empty list"""
        result = contract_repository.get_all(offset=1000, limit=10)

        assert result == []


class TestContractRepositoryCount:
    """Test count method."""

    def test_count_returns_total(self, contract_repository, test_contracts):
        """GIVEN contracts in database / WHEN count() / THEN returns total count"""
        result = contract_repository.count()

        assert result >= 3  # At least signed_partial, unsigned, signed_paid from test_contracts
