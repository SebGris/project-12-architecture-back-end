"""
Tests unitaires pour ClientService.

Tests couverts:
- create_client() : création avec sales_contact_id
- get_client() : récupération par ID
- update_client() : mise à jour avec client_id (pas objet Client)
"""

import pytest

from src.models.client import Client
from src.services.client_service import ClientService


@pytest.fixture
def mock_repository(mocker):
    """Create a mock ClientRepository."""
    return mocker.Mock()


@pytest.fixture
def client_service(mock_repository):
    """Create a ClientService instance with mock repository."""
    return ClientService(repository=mock_repository)


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    return Client(
        id=1,
        first_name="Jean",
        last_name="Dupont",
        email="jean.dupont@example.com",
        phone="0612345678",
        company_name="DupontCorp",
        sales_contact_id=2,
    )


class TestCreateClient:
    """Test create_client method."""

    def test_create_client_success(self, client_service, mock_repository, mock_client):
        """GIVEN valid client data / WHEN create_client() / THEN client created"""
        # Arrange - le repository retourne ce qui lui est passé
        mock_repository.add.side_effect = lambda client: client

        # Act
        result = client_service.create_client(
            first_name="Jean",
            last_name="Dupont",
            email="jean.dupont@example.com",
            phone="0612345678",
            company_name="DupontCorp",
            sales_contact_id=2,
        )

        # Assert
        mock_repository.add.assert_called_once()
        assert isinstance(result, Client)
        assert result.first_name == "Jean"
        assert result.last_name == "Dupont"
        assert result.email == "jean.dupont@example.com"
        assert result.sales_contact_id == 2

    def test_create_client_with_different_sales_contact(
        self, client_service, mock_repository
    ):
        """GIVEN different sales_contact_id / WHEN create_client() / THEN client created"""
        mock_client = Client(
            id=2,
            first_name="Marie",
            last_name="Martin",
            email="marie.martin@example.com",
            phone="0123456789",
            company_name="MartinSA",
            sales_contact_id=5,
        )
        mock_repository.add.return_value = mock_client

        result = client_service.create_client(
            first_name="Marie",
            last_name="Martin",
            email="marie.martin@example.com",
            phone="0123456789",
            company_name="MartinSA",
            sales_contact_id=5,
        )

        assert result.sales_contact_id == 5


class TestGetClient:
    """Test get_client method."""

    def test_get_client_found(self, client_service, mock_repository, mock_client):
        """GIVEN existing client_id / WHEN get_client() / THEN returns client"""
        mock_repository.get.return_value = mock_client

        result = client_service.get_client(client_id=1)

        mock_repository.get.assert_called_once_with(1)
        assert result == mock_client
        assert result.id == 1

    def test_get_client_not_found(self, client_service, mock_repository):
        """GIVEN non-existing client_id / WHEN get_client() / THEN returns None"""
        mock_repository.get.return_value = None

        result = client_service.get_client(client_id=999)

        mock_repository.get.assert_called_once_with(999)
        assert result is None


class TestUpdateClient:
    """Test update_client method."""

    def test_update_client_all_fields(
        self, client_service, mock_repository, mock_client
    ):
        """GIVEN client_id and all fields / WHEN update_client() / THEN client updated"""
        # Arrange
        mock_repository.get.return_value = mock_client
        mock_repository.update.return_value = mock_client

        # Act - IMPORTANT: update_client prend client_id, pas un objet Client
        result = client_service.update_client(
            client_id=1,
            first_name="Jean-Updated",
            last_name="Dupont-Updated",
            email="jean.new@example.com",
            phone="0698765432",
            company_name="NewCorp",
        )

        # Assert
        mock_repository.get.assert_called_once_with(1)
        mock_repository.update.assert_called_once_with(mock_client)
        assert result == mock_client
        assert result.first_name == "Jean-Updated"
        assert result.last_name == "Dupont-Updated"

    def test_update_client_partial_fields(
        self, client_service, mock_repository, mock_client
    ):
        """GIVEN client_id and some fields / WHEN update_client() / THEN only those fields updated"""
        mock_repository.get.return_value = mock_client
        mock_repository.update.return_value = mock_client

        # Update seulement email et phone
        result = client_service.update_client(
            client_id=1, email="new.email@example.com", phone="0611111111"
        )

        mock_repository.get.assert_called_once_with(1)
        mock_repository.update.assert_called_once_with(mock_client)
        assert result.email == "new.email@example.com"
        assert result.phone == "0611111111"

    def test_update_client_not_found(self, client_service, mock_repository):
        """GIVEN non-existing client_id / WHEN update_client() / THEN returns None"""
        mock_repository.get.return_value = None

        result = client_service.update_client(
            client_id=999, first_name="NewName"
        )

        mock_repository.get.assert_called_once_with(999)
        mock_repository.update.assert_not_called()
        assert result is None

    def test_update_client_only_company_name(
        self, client_service, mock_repository, mock_client
    ):
        """GIVEN client_id and company_name / WHEN update_client() / THEN only company updated"""
        mock_repository.get.return_value = mock_client
        mock_repository.update.return_value = mock_client

        result = client_service.update_client(
            client_id=1, company_name="RenamedCompany"
        )

        assert result.company_name == "RenamedCompany"
        mock_repository.update.assert_called_once()
