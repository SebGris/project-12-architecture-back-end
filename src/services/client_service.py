"""Client service module for Epic Events CRM.

This module contains the business logic for managing clients.
"""

from typing import List, Optional

from src.models.client import Client
from src.repositories.client_repository import ClientRepository


class ClientService:
    """Service for managing client-related business logic.

    This service handles all client operations including creation,
    retrieval, and validation of client data.
    """

    def __init__(self, repository: ClientRepository) -> None:
        self.repository = repository

    def get_client(self, client_id: int) -> Optional[Client]:
        """Get a client by ID.

        Args:
            client_id: The client's ID

        Returns:
            Client instance or None if not found
        """
        return self.repository.get(client_id)

    def create_client(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        company_name: str,
        sales_contact_id: int,
    ) -> Client:
        """Create a new client in the database.

        Args:
            first_name: Client's first name
            last_name: Client's last name
            email: Client's email address (must be unique)
            phone: Client's phone number
            company_name: Client's company name
            sales_contact_id: ID of the sales contact (Commercial user)

        Returns:
            The created Client instance
        """
        client = Client(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company_name=company_name,
            sales_contact_id=sales_contact_id,
        )
        self.repository.add(client)
        return client

    def update_client(
        self,
        client_id: int,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        phone: str = None,
        company_name: str = None,
    ) -> Optional[Client]:
        """Update a client's information.

        Args:
            client_id: The client's ID
            first_name: New first name (optional)
            last_name: New last name (optional)
            email: New email (optional)
            phone: New phone (optional)
            company_name: New company name (optional)

        Returns:
            Updated Client instance or None if not found
        """
        client = self.repository.get(client_id)
        if not client:
            return None

        if first_name:
            client.first_name = first_name
        if last_name:
            client.last_name = last_name
        if email:
            client.email = email
        if phone:
            client.phone = phone
        if company_name:
            client.company_name = company_name

        return self.repository.update(client)
