from typing import List, Optional
from src.models.client import Client
from src.repositories.client_repository import ClientRepository


class ClientService:
    def __init__(self, repository: ClientRepository):
        self.repository = repository

    def get_client(self, client_id: str) -> Optional[Client]:
        return self.repository.get_by_id(client_id)

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
