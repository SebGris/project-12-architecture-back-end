from typing import List, Optional
from src.repositories.client_repository import ClientRepository
from src.models.client import Client


class InMemoryClientRepository(ClientRepository):
    """In-memory implementation of ClientRepository for testing."""

    def __init__(self):
        self._clients: dict[int, Client] = {}
        self._next_id = 1

    def get(self, client_id: int) -> Optional[Client]:
        """Get a client by ID.

        Args:
            client_id: The client's ID

        Returns:
            Client instance or None if not found
        """
        return self._clients.get(client_id)

    def add(self, client: Client) -> Client:
        """Add a new client to the repository.

        Args:
            client: Client instance to add

        Returns:
            The added Client instance (with ID populated after commit)
        """
        if client.id is None:
            client.id = self._next_id
            self._next_id += 1
        self._clients[client.id] = client
        return client

    def list_all(self) -> List[Client]:
        """List all clients.

        Returns:
            List of all Client instances
        """
        return list(self._clients.values())
