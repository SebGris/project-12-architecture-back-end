from typing import List, Optional
from src.repositories.client_repository import ClientRepository
from src.models.client import Client


class InMemoryClientRepository(ClientRepository):
    """Implementation en mémoire du repository Client pour les tests."""

    def __init__(self):
        self._clients: dict[str, Client] = {}
        self._next_id = 1

    def get_by_id(self, client_id: str) -> Optional[Client]:
        """Récupère un client par son ID."""
        return self._clients.get(client_id)

    def add(self, client: Client) -> None:
        """Ajoute un nouveau client en mémoire."""
        if client.id is None:
            client.id = str(self._next_id)
            self._next_id += 1
        self._clients[client.id] = client

    def list_all(self) -> List[Client]:
        """Retourne la liste de tous les clients."""
        return list(self._clients.values())
