"""
Test unitaire pour la création des clients avec InMemoryClientRepository.

Ce test vérifie que :
- Les clients peuvent être créés via ClientService
- Le repository en mémoire fonctionne correctement
- Les données sont correctement persistées
"""
import pytest
from src.models.client import Client
from src.repositories.in_memory_client_repository import InMemoryClientRepository
from src.services.client_service import ClientService


@pytest.fixture
def client_repository():
    """Fixture qui fournit un repository en mémoire vide."""
    return InMemoryClientRepository()


@pytest.fixture
def client_service(client_repository):
    """Fixture qui fournit un service client avec repository en mémoire."""
    return ClientService(client_repository)


def test_create_client(client_service, client_repository):
    """
    GIVEN des données client valides
    WHEN un client est créé via le service
    THEN il est sauvegardé correctement dans le repository
    """
    # Act - Créer le client
    client = client_service.create_client(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+33123456789",
        company_name="Acme Corp",
        sales_contact_id=1
    )

    # Assert - Vérifier que le client a été créé
    assert client is not None
    assert client.id is not None
    assert client.first_name == "John"
    assert client.last_name == "Doe"
    assert client.email == "john.doe@example.com"
    assert client.phone == "+33123456789"
    assert client.company_name == "Acme Corp"
    assert client.sales_contact_id == 1

    # Assert - Vérifier qu'il est dans le repository
    saved_client = client_repository.get_by_id(client.id)
    assert saved_client is not None
    assert saved_client.email == "john.doe@example.com"


def test_get_client_by_id(client_service, client_repository):
    """
    GIVEN un client existant dans le repository
    WHEN on récupère le client par son ID
    THEN les bonnes données sont retournées
    """
    # Arrange - Créer un client directement dans le repository
    client = Client(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        phone="+33987654321",
        company_name="Tech Inc",
        sales_contact_id=2
    )
    client_repository.add(client)

    # Act - Récupérer le client via le service
    retrieved_client = client_service.get_client(client.id)

    # Assert
    assert retrieved_client is not None
    assert retrieved_client.id == client.id
    assert retrieved_client.first_name == "Jane"
    assert retrieved_client.last_name == "Smith"
    assert retrieved_client.email == "jane.smith@example.com"


def test_get_nonexistent_client(client_service):
    """
    GIVEN un ID de client qui n'existe pas
    WHEN on essaie de récupérer ce client
    THEN None est retourné
    """
    # Act
    client = client_service.get_client("999")

    # Assert
    assert client is None


def test_create_multiple_clients(client_service, client_repository):
    """
    GIVEN plusieurs clients à créer
    WHEN ils sont créés via le service
    THEN tous sont présents dans le repository
    """
    # Arrange
    clients_data = [
        ("Alice", "Martin", "alice@example.com", "Startup A", 1),
        ("Bob", "Durant", "bob@example.com", "Startup B", 1),
        ("Charlie", "Bernard", "charlie@example.com", "Startup C", 2),
    ]

    # Act - Créer tous les clients
    created_clients = []
    for first_name, last_name, email, company, sales_id in clients_data:
        client = client_service.create_client(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone="+33111111111",
            company_name=company,
            sales_contact_id=sales_id
        )
        created_clients.append(client)

    # Assert - Vérifier que tous sont dans le repository
    all_clients = client_repository.list_all()
    assert len(all_clients) == 3

    # Vérifier que chaque client créé est récupérable
    for client in created_clients:
        retrieved = client_repository.get_by_id(client.id)
        assert retrieved is not None
        assert retrieved.id == client.id


def test_client_id_auto_increment(client_service):
    """
    GIVEN plusieurs clients créés
    WHEN ils sont ajoutés au repository
    THEN les IDs sont auto-incrémentés
    """
    # Act
    client1 = client_service.create_client(
        first_name="Client",
        last_name="One",
        email="client1@example.com",
        phone="+33111111111",
        company_name="Company 1",
        sales_contact_id=1
    )

    client2 = client_service.create_client(
        first_name="Client",
        last_name="Two",
        email="client2@example.com",
        phone="+33222222222",
        company_name="Company 2",
        sales_contact_id=1
    )

    # Assert
    assert client1.id == "1"
    assert client2.id == "2"
