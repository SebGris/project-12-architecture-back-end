"""
Integration tests for SqlAlchemyClientRepository.
"""

import pytest

from src.models.client import Client
from src.repositories.sqlalchemy_client_repository import (
    SqlAlchemyClientRepository,
)


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
        db_client = (
            db_session.query(Client)
            .filter_by(email="alice@wonderland.com")
            .first()
        )
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


class TestClientRepositoryExists:
    """Test exists method."""

    def test_exists_returns_true_for_existing_client(
        self, client_repository, test_clients
    ):
        """GIVEN existing client / WHEN exists() / THEN returns True"""
        kevin = test_clients["kevin"]

        result = client_repository.exists(kevin.id)

        assert result is True

    def test_exists_returns_false_for_nonexistent_client(self, client_repository):
        """GIVEN nonexistent client_id / WHEN exists() / THEN returns False"""
        result = client_repository.exists(99999)

        assert result is False


class TestClientRepositoryEmailExists:
    """Test email_exists method."""

    def test_email_exists_returns_true(self, client_repository, test_clients):
        """GIVEN existing email / WHEN email_exists() / THEN returns True"""
        result = client_repository.email_exists("kevin@startup.io")

        assert result is True

    def test_email_exists_returns_false(self, client_repository):
        """GIVEN nonexistent email / WHEN email_exists() / THEN returns False"""
        result = client_repository.email_exists("nonexistent@email.com")

        assert result is False

    def test_email_exists_excludes_id(self, client_repository, test_clients):
        """GIVEN existing email with exclude_id / WHEN email_exists() / THEN returns False"""
        kevin = test_clients["kevin"]

        # Email exists but we exclude Kevin's ID (for update scenario)
        result = client_repository.email_exists(
            "kevin@startup.io", exclude_id=kevin.id
        )

        assert result is False


class TestClientRepositoryGetBySalesContact:
    """Test get_by_sales_contact method."""

    def test_get_by_sales_contact(self, client_repository, test_users, test_clients):
        """GIVEN commercial with clients / WHEN get_by_sales_contact() / THEN returns their clients"""
        commercial1 = test_users["commercial1"]

        result = client_repository.get_by_sales_contact(commercial1.id)

        assert len(result) >= 1
        assert all(c.sales_contact_id == commercial1.id for c in result)

    def test_get_by_sales_contact_no_clients(self, client_repository, test_users):
        """GIVEN commercial with no clients / WHEN get_by_sales_contact() / THEN returns empty list"""
        # Use a user ID that has no clients
        result = client_repository.get_by_sales_contact(99999)

        assert result == []


class TestClientRepositoryGetAll:
    """Test get_all method with pagination."""

    def test_get_all_default_pagination(self, client_repository, test_clients):
        """GIVEN clients in database / WHEN get_all() / THEN returns paginated list"""
        result = client_repository.get_all()

        assert len(result) >= 1
        assert isinstance(result, list)

    def test_get_all_with_offset_and_limit(self, client_repository, test_clients):
        """GIVEN clients in database / WHEN get_all(offset, limit) / THEN returns correct slice"""
        result = client_repository.get_all(offset=0, limit=1)

        assert len(result) == 1

    def test_get_all_offset_beyond_data(self, client_repository, test_clients):
        """GIVEN offset beyond data / WHEN get_all() / THEN returns empty list"""
        result = client_repository.get_all(offset=1000, limit=10)

        assert result == []


class TestClientRepositoryCount:
    """Test count method."""

    def test_count_returns_total(self, client_repository, test_clients):
        """GIVEN clients in database / WHEN count() / THEN returns total count"""
        result = client_repository.count()

        assert result >= 2  # At least kevin and sarah from test_clients
