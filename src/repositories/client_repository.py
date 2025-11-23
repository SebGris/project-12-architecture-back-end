"""Client repository interface for Epic Events CRM.

This module defines the abstract repository interface for Client persistence,
following the Repository pattern to decouple business logic from data access.
"""

from abc import ABC, abstractmethod
from typing import Optional

from src.models.client import Client


class ClientRepository(ABC):
    """Abstract repository interface for Client persistence."""

    @abstractmethod
    def get(self, client_id: int) -> Optional[Client]:
        """Get a client by ID.

        Args:
            client_id: The client's ID

        Returns:
            Client instance or None if not found
        """

    @abstractmethod
    def add(self, client: Client) -> Client:
        """Add a new client to the repository.

        Args:
            client: Client instance to add

        Returns:
            The added Client instance (with ID populated after commit)
        """

    @abstractmethod
    def update(self, client: Client) -> Client:
        """Update an existing client.

        Args:
            client: Client instance to update

        Returns:
            The updated Client instance
        """
