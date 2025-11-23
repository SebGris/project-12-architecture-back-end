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
