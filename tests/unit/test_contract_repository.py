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


class TestContractRepositoryFilters:
    """Test filtering methods for contracts."""

    @pytest.mark.parametrize(
        "method,check_attr,check_value",
        [
            ("get_unsigned_contracts", "is_signed", False),
            ("get_signed_contracts", "is_signed", True),
        ],
        ids=["unsigned", "signed"],
    )
    def test_get_contracts_by_signature(
        self, contract_repository, test_contracts, method, check_attr, check_value
    ):
        """Test get_unsigned_contracts and get_signed_contracts."""
        result = getattr(contract_repository, method)()

        assert len(result) >= 1
        assert all(getattr(c, check_attr) is check_value for c in result)

    def test_get_unpaid_contracts(self, contract_repository, test_contracts):
        """GIVEN contracts with remaining amount / WHEN get_unpaid_contracts() / THEN returns unpaid"""
        result = contract_repository.get_unpaid_contracts()

        assert len(result) >= 1
        assert all(c.remaining_amount > 0 for c in result)


class TestContractRepositoryExists:
    """Test exists method."""

    @pytest.mark.parametrize(
        "get_id,expected",
        [("existing", True), ("nonexistent", False)],
        ids=["existing", "nonexistent"],
    )
    def test_exists(self, contract_repository, test_contracts, get_id, expected):
        """Test exists returns correct boolean for existing/nonexistent contracts."""
        contract_id = (
            test_contracts["signed_partial"].id if get_id == "existing" else 99999
        )
        result = contract_repository.exists(contract_id)
        assert result is expected


class TestContractRepositoryPagination:
    """Test get_all and count methods."""

    @pytest.mark.parametrize(
        "offset,limit,expected_len",
        [(0, 100, None), (0, 1, 1), (1000, 10, 0)],
        ids=["default", "limit_1", "beyond_data"],
    )
    def test_get_all_pagination(
        self, contract_repository, test_contracts, offset, limit, expected_len
    ):
        """Test get_all with various pagination scenarios."""
        result = contract_repository.get_all(offset=offset, limit=limit)

        if expected_len is None:
            assert len(result) >= 1
        else:
            assert len(result) == expected_len

    def test_count_returns_total(self, contract_repository, test_contracts):
        """GIVEN contracts in database / WHEN count() / THEN returns total count"""
        result = contract_repository.count()

        assert result >= 3
