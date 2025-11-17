"""
Integration tests for SqlAlchemyClientRepository.
"""

import pytest

from src.models.client import Client
from src.repositories.sqlalchemy_client_repository import SqlAlchemyClientRepository


@pytest.fixture
def client_repository(db_session):
    """Create a ClientRepository with the test database session."""
    return SqlAlchemyClientRepository(session=db_session)


class TestClientRepositoryGet:
    """Test get method."""

    def test_get_existing_client(self, client_repository, test_clients):
        """GIVEN existing client / WHEN get(client_id) / THEN returns client"""
        kevin = test_clients["kevin"]

        result = client_repository.get(kevin.id)

        assert result is not None
        assert result.id == kevin.id
        assert result.first_name == "Kevin"
        assert result.company_name == "Cool Startup LLC"

    def test_get_nonexistent_client(self, client_repository):
        """GIVEN nonexistent client_id / WHEN get() / THEN returns None"""
        result = client_repository.get(99999)

        assert result is None


class TestClientRepositoryAdd:
    """Test add method."""

    def test_add_new_client(self, client_repository, test_users, db_session):
        """GIVEN new client / WHEN add() / THEN client saved with ID"""
        new_client = Client(
            first_name="Alice",
            last_name="Wonder",
            email="alice@wonderland.com",
            phone="0111111111",
            company_name="Wonderland Inc",
            sales_contact_id=test_users["commercial1"].id,
        )

        result = client_repository.add(new_client)

        assert result.id is not None
        assert result.first_name == "Alice"

        # Verify it's in database
        db_client = db_session.query(Client).filter_by(email="alice@wonderland.com").first()
        assert db_client is not None
        assert db_client.id == result.id


class TestClientRepositoryUpdate:
    """Test update method."""

    def test_update_client(self, client_repository, test_clients, db_session):
        """GIVEN existing client with changes / WHEN update() / THEN changes persisted"""
        client = test_clients["kevin"]
        client.phone = "0888888888"
        client.company_name = "Cool Startup 2.0"

        result = client_repository.update(client)

        assert result.phone == "0888888888"
        assert result.company_name == "Cool Startup 2.0"

        # Verify changes persisted
        db_session.expire_all()
        db_client = db_session.query(Client).filter_by(id=client.id).first()
        assert db_client.phone == "0888888888"
