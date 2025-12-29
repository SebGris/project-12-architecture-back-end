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

    @pytest.mark.parametrize(
        "get_id,expected",
        [("existing", True), ("nonexistent", False)],
        ids=["existing", "nonexistent"],
    )
    def test_exists(self, client_repository, test_clients, get_id, expected):
        """Test exists returns correct boolean for existing/nonexistent clients."""
        client_id = test_clients["kevin"].id if get_id == "existing" else 99999
        result = client_repository.exists(client_id)
        assert result is expected


class TestClientRepositoryEmailExists:
    """Test email_exists method."""

    @pytest.mark.parametrize(
        "email,exclude_id,expected",
        [
            ("kevin@startup.io", None, True),
            ("nonexistent@email.com", None, False),
            ("kevin@startup.io", "kevin", False),  # exclude_id scenario
        ],
        ids=["exists", "not_exists", "excluded"],
    )
    def test_email_exists(
        self, client_repository, test_clients, email, exclude_id, expected
    ):
        """Test email_exists with various scenarios."""
        exclude = test_clients["kevin"].id if exclude_id == "kevin" else None
        result = client_repository.email_exists(email, exclude_id=exclude)
        assert result is expected


class TestClientRepositoryGetBySalesContact:
    """Test get_by_sales_contact method."""

    def test_get_by_sales_contact(self, client_repository, test_users, test_clients):
        """GIVEN commercial with clients / WHEN get_by_sales_contact() / THEN returns their clients"""
        commercial1 = test_users["commercial1"]

        result = client_repository.get_by_sales_contact(commercial1.id)

        assert len(result) >= 1
        assert all(c.sales_contact_id == commercial1.id for c in result)

    def test_get_by_sales_contact_no_clients(self, client_repository):
        """GIVEN commercial with no clients / WHEN get_by_sales_contact() / THEN returns empty list"""
        result = client_repository.get_by_sales_contact(99999)

        assert result == []


class TestClientRepositoryPagination:
    """Test get_all and count methods."""

    @pytest.mark.parametrize(
        "offset,limit,expected_len",
        [(0, 100, None), (0, 1, 1), (1000, 10, 0)],
        ids=["default", "limit_1", "beyond_data"],
    )
    def test_get_all_pagination(
        self, client_repository, test_clients, offset, limit, expected_len
    ):
        """Test get_all with various pagination scenarios."""
        result = client_repository.get_all(offset=offset, limit=limit)

        if expected_len is None:
            assert len(result) >= 1
        else:
            assert len(result) == expected_len

    def test_count_returns_total(self, client_repository, test_clients):
        """GIVEN clients in database / WHEN count() / THEN returns total count"""
        result = client_repository.count()

        assert result >= 2
