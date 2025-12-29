"""SQLAlchemy implementation of ClientRepository.

This module provides the concrete implementation of the ClientRepository
interface using SQLAlchemy ORM for database persistence.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.client import Client
from src.repositories.client_repository import ClientRepository


class SqlAlchemyClientRepository(ClientRepository):
    """SQLAlchemy implementation of ClientRepository."""

    def __init__(self, session: Session):
        self.session = session

    def get(self, client_id: int) -> Optional[Client]:
        """Get a client by ID.

        Args:
            client_id: The client's ID

        Returns:
            Client instance or None if not found
        """
        return self.session.query(Client).filter_by(id=client_id).first()

    def add(self, client: Client) -> Client:
        """Add a new client to the repository.

        Args:
            client: Client instance to add

        Returns:
            The added Client instance (with ID populated after commit)
        """
        self.session.add(client)
        self.session.commit()
        self.session.refresh(client)
        return client

    def update(self, client: Client) -> Client:
        """Update an existing client.

        Args:
            client: Client instance to update

        Returns:
            The updated Client instance
        """
        self.session.commit()
        self.session.refresh(client)
        return client

    def exists(self, client_id: int) -> bool:
        """Check if a client exists by ID.

        Args:
            client_id: The client's ID

        Returns:
            True if the client exists, False otherwise
        """
        return self.session.query(Client).filter_by(id=client_id).first() is not None

    def email_exists(self, email: str, exclude_id: int = None) -> bool:
        """Check if an email is already in use by a client.

        Args:
            email: The email to check
            exclude_id: Optional client ID to exclude from the check (for updates)

        Returns:
            True if the email is already used, False otherwise
        """
        query = self.session.query(Client).filter_by(email=email)
        if exclude_id is not None:
            query = query.filter(Client.id != exclude_id)
        return query.first() is not None

    def get_by_sales_contact(self, sales_contact_id: int) -> List[Client]:
        """Get all clients assigned to a specific sales contact.

        Args:
            sales_contact_id: The ID of the sales contact (commercial)

        Returns:
            List of Client instances assigned to this sales contact
        """
        return (
            self.session.query(Client)
            .filter_by(sales_contact_id=sales_contact_id)
            .all()
        )
