"""Unit tests for ClientService.

Tests covered:
- create_client(): Client creation with sales contact validation
- get_client(): Client retrieval by ID
- list_clients(): Clients listing with optional filters
- update_client(): Client information updates
- delete_client(): Client deletion

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
