"""SQLAlchemy implementation of ClientRepository.

This module provides the concrete implementation of the ClientRepository
interface using SQLAlchemy ORM for database persistence.
"""

from typing import Optional

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

