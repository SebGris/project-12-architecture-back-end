"""Unit tests for ClientService.

Tests covered:
- create_client(): Client creation with sales contact validation
- get_client(): Client retrieval by ID
- update_client(): Client information updates
- exists(): Client existence check by ID
- email_exists(): Email uniqueness check with exclusion support
- get_my_clients(): Clients by sales contact
- get_all_clients(): Clients listing with pagination
- count_clients(): Total clients count

Implementation notes:
- Uses real SQLite in-memory database
- Zero mocks - uses real SqlAlchemyClientRepository
- Tests business logic with real database relationships
"""

import pytest

from src.models.client import Client
from src.repositories.sqlalchemy_client_repository import (
    SqlAlchemyClientRepository,
)
from src.services.client_service import ClientService


@pytest.fixture
def client_service(db_session):
    """Create a ClientService instance with real repository and SQLite DB."""
    repository = SqlAlchemyClientRepository(session=db_session)
    return ClientService(repository=repository)


class TestCreateClient:
    """Test create_client method."""

    def test_create_client_success(
        self, client_service, test_users, db_session
    ):
        """GIVEN valid client data / WHEN create_client() / THEN client created"""
        result = client_service.create_client(
            first_name="Jean",
            last_name="Dupont",
            email="jean.dupont@example.com",
            phone="0612345678",
            company_name="DupontCorp",
            sales_contact_id=test_users["commercial1"].id,
        )

        # Verify client was created
        assert isinstance(result, Client)
        assert result.id is not None
        assert result.first_name == "Jean"
        assert result.last_name == "Dupont"
        assert result.email == "jean.dupont@example.com"
        assert result.sales_contact_id == test_users["commercial1"].id

        # Verify it's persisted in database
        db_client = (
            db_session.query(Client)
            .filter_by(email="jean.dupont@example.com")
            .first()
        )
        assert db_client is not None
        assert db_client.id == result.id


class TestGetClient:
    """Test get_client method."""

    @pytest.mark.parametrize(
        "get_id,expected_found",
        [("existing", True), ("nonexistent", False)],
        ids=["found", "not_found"],
    )
    def test_get_client(self, client_service, test_clients, get_id, expected_found):
        """Test get_client with existing and nonexistent IDs."""
        client_id = test_clients["kevin"].id if get_id == "existing" else 99999
        result = client_service.get_client(client_id=client_id)

        if expected_found:
            assert result is not None
            assert result.first_name == "Kevin"
        else:
            assert result is None


class TestUpdateClient:
    """Test update_client method."""

    def test_update_client_all_fields(
        self, client_service, test_clients, db_session
    ):
        """GIVEN client_id and all fields / WHEN update_client() / THEN client updated"""
        kevin = test_clients["kevin"]

        result = client_service.update_client(
            client_id=kevin.id,
            first_name="Kevin-Updated",
            last_name="Casey-Updated",
            email="kevin.new@example.com",
            phone="0698765432",
            company_name="NewCorp",
        )

        # Verify updates
        assert result is not None
        assert result.first_name == "Kevin-Updated"
        assert result.company_name == "NewCorp"

        # Verify changes persisted
        db_session.expire_all()
        db_client = db_session.query(Client).filter_by(id=kevin.id).first()
        assert db_client.first_name == "Kevin-Updated"

    def test_update_client_partial_fields(self, client_service, test_clients):
        """GIVEN client_id and some fields / WHEN update_client() / THEN only those fields updated"""
        kevin = test_clients["kevin"]
        original_first_name = kevin.first_name

        result = client_service.update_client(
            client_id=kevin.id,
            email="new.email@example.com",
            phone="0611111111",
        )

        # Verify partial update
        assert result.email == "new.email@example.com"
        assert result.first_name == original_first_name

    def test_update_client_not_found(self, client_service):
        """GIVEN non-existing client_id / WHEN update_client() / THEN returns None"""
        result = client_service.update_client(
            client_id=99999, first_name="NewName"
        )

        assert result is None


class TestClientServiceExists:
    """Test exists method."""

    @pytest.mark.parametrize(
        "get_id,expected",
        [("existing", True), ("nonexistent", False)],
        ids=["existing", "nonexistent"],
    )
    def test_exists(self, client_service, test_clients, get_id, expected):
        """Test exists returns correct boolean."""
        client_id = test_clients["kevin"].id if get_id == "existing" else 99999
        result = client_service.exists(client_id)
        assert result is expected


class TestClientServiceEmailExists:
    """Test email_exists method."""

    @pytest.mark.parametrize(
        "email,exclude_id,expected",
        [
            ("kevin@startup.io", None, True),
            ("nonexistent@email.com", None, False),
            ("kevin@startup.io", "kevin", False),
        ],
        ids=["exists", "not_exists", "excluded"],
    )
    def test_email_exists(
        self, client_service, test_clients, email, exclude_id, expected
    ):
        """Test email_exists with various scenarios."""
        exclude = test_clients["kevin"].id if exclude_id == "kevin" else None
        result = client_service.email_exists(email, exclude_id=exclude)
        assert result is expected


class TestGetMyClients:
    """Test get_my_clients method."""

    def test_get_my_clients_returns_assigned_clients(
        self, client_service, test_clients, test_users
    ):
        """GIVEN sales_contact_id / WHEN get_my_clients() / THEN returns assigned clients"""
        commercial1 = test_users["commercial1"]

        result = client_service.get_my_clients(sales_contact_id=commercial1.id)

        assert len(result) >= 1
        assert all(client.sales_contact_id == commercial1.id for client in result)

    def test_get_my_clients_returns_empty_for_no_assignments(self, client_service):
        """GIVEN sales_contact_id with no clients / WHEN get_my_clients() / THEN returns empty list"""
        result = client_service.get_my_clients(sales_contact_id=99999)

        assert result == []


class TestClientServicePagination:
    """Test get_all_clients and count_clients methods."""

    @pytest.mark.parametrize(
        "offset,limit,expected_len",
        [(0, 100, None), (0, 1, 1), (1000, 10, 0)],
        ids=["default", "limit_1", "beyond_data"],
    )
    def test_get_all_clients_pagination(
        self, client_service, test_clients, offset, limit, expected_len
    ):
        """Test get_all_clients with various pagination scenarios."""
        result = client_service.get_all_clients(offset=offset, limit=limit)

        if expected_len is None:
            assert len(result) >= 1
        else:
            assert len(result) == expected_len

    def test_count_clients_returns_total(self, client_service, test_clients):
        """GIVEN clients in database / WHEN count_clients() / THEN returns total count"""
        result = client_service.count_clients()

        assert result >= 2
