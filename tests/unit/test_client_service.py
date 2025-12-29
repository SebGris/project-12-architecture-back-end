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

    def test_get_client_found(self, client_service, test_clients):
        """GIVEN existing client_id / WHEN get_client() / THEN returns client"""
        kevin = test_clients["kevin"]

        result = client_service.get_client(client_id=kevin.id)

        assert result is not None
        assert result.id == kevin.id
        assert result.first_name == "Kevin"
        assert result.company_name == "Cool Startup LLC"

    def test_get_client_not_found(self, client_service):
        """GIVEN non-existing client_id / WHEN get_client() / THEN returns None"""
        result = client_service.get_client(client_id=99999)

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
        assert result.last_name == "Casey-Updated"
        assert result.email == "kevin.new@example.com"
        assert result.phone == "0698765432"
        assert result.company_name == "NewCorp"

        # Verify changes persisted
        db_session.expire_all()
        db_client = db_session.query(Client).filter_by(id=kevin.id).first()
        assert db_client.first_name == "Kevin-Updated"
        assert db_client.company_name == "NewCorp"

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
        assert result.phone == "0611111111"
        # First name should be unchanged
        assert result.first_name == original_first_name

    def test_update_client_not_found(self, client_service):
        """GIVEN non-existing client_id / WHEN update_client() / THEN returns None"""
        result = client_service.update_client(
            client_id=99999, first_name="NewName"
        )

        assert result is None

    def test_update_client_only_company_name(
        self, client_service, test_clients, db_session
    ):
        """GIVEN client_id and company_name / WHEN update_client() / THEN only company updated"""
        lou = test_clients["lou"]

        result = client_service.update_client(
            client_id=lou.id, company_name="RenamedCompany"
        )

        assert result.company_name == "RenamedCompany"

        # Verify persistence
        db_session.expire_all()
        db_client = db_session.query(Client).filter_by(id=lou.id).first()
        assert db_client.company_name == "RenamedCompany"


class TestClientServiceExists:
    """Test exists method."""

    def test_exists_returns_true_for_existing_client(
        self, client_service, test_clients
    ):
        """GIVEN existing client / WHEN exists() / THEN returns True"""
        kevin = test_clients["kevin"]

        result = client_service.exists(kevin.id)

        assert result is True

    def test_exists_returns_false_for_nonexistent_client(self, client_service):
        """GIVEN nonexistent client_id / WHEN exists() / THEN returns False"""
        result = client_service.exists(99999)

        assert result is False


class TestClientServiceEmailExists:
    """Test email_exists method."""

    def test_email_exists_returns_true(self, client_service, test_clients):
        """GIVEN existing email / WHEN email_exists() / THEN returns True"""
        result = client_service.email_exists("kevin@startup.io")

        assert result is True

    def test_email_exists_returns_false(self, client_service):
        """GIVEN nonexistent email / WHEN email_exists() / THEN returns False"""
        result = client_service.email_exists("nonexistent@email.com")

        assert result is False

    def test_email_exists_excludes_id(self, client_service, test_clients):
        """GIVEN existing email with exclude_id / WHEN email_exists() / THEN returns False"""
        kevin = test_clients["kevin"]

        result = client_service.email_exists("kevin@startup.io", exclude_id=kevin.id)

        assert result is False


class TestGetMyClients:
    """Test get_my_clients method."""

    def test_get_my_clients_returns_assigned_clients(
        self, client_service, test_clients, test_users
    ):
        """GIVEN sales_contact_id / WHEN get_my_clients() / THEN returns assigned clients"""
        commercial1 = test_users["commercial1"]

        result = client_service.get_my_clients(sales_contact_id=commercial1.id)

        # Should return clients assigned to commercial1
        assert len(result) >= 1
        assert all(client.sales_contact_id == commercial1.id for client in result)

    def test_get_my_clients_returns_empty_for_no_assignments(self, client_service):
        """GIVEN sales_contact_id with no clients / WHEN get_my_clients() / THEN returns empty list"""
        result = client_service.get_my_clients(sales_contact_id=99999)

        assert result == []


class TestGetAllClients:
    """Test get_all_clients method with pagination."""

    def test_get_all_clients_default_pagination(self, client_service, test_clients):
        """GIVEN clients in database / WHEN get_all_clients() / THEN returns paginated list"""
        result = client_service.get_all_clients()

        assert len(result) >= 1
        assert isinstance(result, list)

    def test_get_all_clients_with_offset_and_limit(
        self, client_service, test_clients
    ):
        """GIVEN clients in database / WHEN get_all_clients(offset, limit) / THEN returns correct slice"""
        result = client_service.get_all_clients(offset=0, limit=1)

        assert len(result) == 1

    def test_get_all_clients_offset_beyond_data(self, client_service, test_clients):
        """GIVEN offset beyond data / WHEN get_all_clients() / THEN returns empty list"""
        result = client_service.get_all_clients(offset=1000, limit=10)

        assert result == []


class TestCountClients:
    """Test count_clients method."""

    def test_count_clients_returns_total(self, client_service, test_clients):
        """GIVEN clients in database / WHEN count_clients() / THEN returns total count"""
        result = client_service.count_clients()

        assert result >= 2  # At least kevin and lou from test_clients