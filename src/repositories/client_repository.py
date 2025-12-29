"""Client repository interface for Epic Events CRM.

This module defines the abstract repository interface for Client persistence,
following the Repository pattern to decouple business logic from data access.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

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

    @abstractmethod
    def exists(self, client_id: int) -> bool:
        """Check if a client exists by ID.

        Args:
            client_id: The client's ID

        Returns:
            True if the client exists, False otherwise
        """

    @abstractmethod
    def email_exists(self, email: str, exclude_id: int = None) -> bool:
        """Check if an email is already in use by a client.

        Args:
            email: The email to check
            exclude_id: Optional client ID to exclude from the check (for updates)

        Returns:
            True if the email is already used, False otherwise
        """

    @abstractmethod
    def get_by_sales_contact(self, sales_contact_id: int) -> List[Client]:
        """Get all clients assigned to a specific sales contact.

        Args:
            sales_contact_id: The ID of the sales contact (commercial)

        Returns:
            List of Client instances assigned to this sales contact
        """
