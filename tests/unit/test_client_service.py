"""
Tests unitaires pour ClientService.

Tests couverts:
- create_client() : création avec auto-assignation
- update_client() : mise à jour
- get_client() : récupération par ID
- get_all_clients() : liste complète
"""

import pytest
from src.services.client_service import ClientService


@pytest.fixture
def mock_client_repository(mocker):
    """Create a mock client repository."""
    return mocker.Mock()


@pytest.fixture
def client_service(mock_client_repository):
    """Create a ClientService instance with mocked repository."""
    return ClientService(mock_client_repository)


@pytest.fixture
def sample_client(mocker):
    """Create a sample client for testing."""
    client = mocker.Mock()
    client.id = 1
    client.first_name = "Jean"
    client.last_name = "Dupont"
    client.email = "jean.dupont@example.com"
    client.phone = "0612345678"
    client.company_name = "DupontCorp"
    client.sales_contact_id = 2
    return client


class TestCreateClient:
    """Test create_client method."""

    def test_create_client_success(
        self, client_service, mock_client_repository, sample_client
    ):
        """
        GIVEN valid client data
        WHEN create_client is called
        THEN client should be created
        """
        # Configure mock
        mock_client_repository.create.return_value = sample_client

        # Call service
        result = client_service.create_client(
            first_name="Jean",
            last_name="Dupont",
            email="jean.dupont@example.com",
            phone="0612345678",
            company_name="DupontCorp",
            sales_contact_id=2,
        )

        # Verify repository was called
        mock_client_repository.create.assert_called_once_with(
            first_name="Jean",
            last_name="Dupont",
            email="jean.dupont@example.com",
            phone="0612345678",
            company_name="DupontCorp",
            sales_contact_id=2,
        )

        # Verify result
        assert result == sample_client


class TestUpdateClient:
    """Test update_client method."""

    def test_update_client_success(
        self, client_service, mock_client_repository, sample_client
    ):
        """
        GIVEN an existing client and update data
        WHEN update_client is called
        THEN client should be updated
        """
        # Configure mock
        mock_client_repository.update.return_value = sample_client

        # Call service
        result = client_service.update_client(
            client_id=1,
            first_name="Jean",
            last_name="Dupont-Martin",
            email="jean.dupont@example.com",
            phone="0612345678",
            company_name="DupontCorp International",
        )

        # Verify repository was called
        mock_client_repository.update.assert_called_once_with(
            client_id=1,
            first_name="Jean",
            last_name="Dupont-Martin",
            email="jean.dupont@example.com",
            phone="0612345678",
            company_name="DupontCorp International",
        )

        # Verify result
        assert result == sample_client


class TestGetClient:
    """Test get_client method."""

    def test_get_client_found(
        self, client_service, mock_client_repository, sample_client
    ):
        """
        GIVEN a client ID that exists
        WHEN get_client is called
        THEN the client should be returned
        """
        # Configure mock
        mock_client_repository.get_by_id.return_value = sample_client

        # Call service
        result = client_service.get_client(1)

        # Verify
        mock_client_repository.get_by_id.assert_called_once_with(1)
        assert result == sample_client

    def test_get_client_not_found(self, client_service, mock_client_repository):
        """
        GIVEN a client ID that does not exist
        WHEN get_client is called
        THEN None should be returned
        """
        # Configure mock
        mock_client_repository.get_by_id.return_value = None

        # Call service
        result = client_service.get_client(999)

        # Verify
        mock_client_repository.get_by_id.assert_called_once_with(999)
        assert result is None


class TestGetAllClients:
    """Test get_all_clients method."""

    def test_get_all_clients(
        self, client_service, mock_client_repository, sample_client
    ):
        """
        GIVEN multiple clients in the system
        WHEN get_all_clients is called
        THEN all clients should be returned
        """
        # Configure mock
        clients = [sample_client, sample_client]
        mock_client_repository.get_all.return_value = clients

        # Call service
        result = client_service.get_all_clients()

        # Verify
        mock_client_repository.get_all.assert_called_once()
        assert result == clients
        assert len(result) == 2

    def test_get_all_clients_empty(self, client_service, mock_client_repository):
        """
        GIVEN no clients in the system
        WHEN get_all_clients is called
        THEN an empty list should be returned
        """
        # Configure mock
        mock_client_repository.get_all.return_value = []

        # Call service
        result = client_service.get_all_clients()

        # Verify
        mock_client_repository.get_all.assert_called_once()
        assert result == []
