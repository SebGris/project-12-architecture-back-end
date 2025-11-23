"""Contract repository interface for Epic Events CRM.

This module defines the abstract repository interface for Contract persistence.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.models.contract import Contract


class ContractRepository(ABC):
    """Abstract repository interface for Contract persistence."""

    @abstractmethod
    def get(self, contract_id: int) -> Optional[Contract]:
        """Get a contract by ID.

        Args:
            contract_id: The contract's ID

        Returns:
            Contract instance or None if not found
        """

    @abstractmethod
    def add(self, contract: Contract) -> Contract:
        """Add a new contract to the repository.

        Args:
            contract: Contract instance to add

        Returns:
            The added Contract instance (with ID populated after commit)
        """

    @abstractmethod
    def update(self, contract: Contract) -> Contract:
        """Update an existing contract in the repository.

        Args:
            contract: Contract instance to update (must have an ID)

        Returns:
            The updated Contract instance
        """

    @abstractmethod
    def get_by_client_id(self, client_id: int) -> List[Contract]:
        """Get all contracts for a specific client.

        Args:
            client_id: The client's ID

        Returns:
            List of Contract instances for the client
        """

    @abstractmethod
    def get_unsigned_contracts(self) -> List[Contract]:
        """Get all unsigned contracts.

        Returns:
            List of unsigned Contract instances
        """

    @abstractmethod
    def get_unpaid_contracts(self) -> List[Contract]:
        """Get all contracts with remaining amount > 0.

        Returns:
            List of Contract instances with unpaid balance
        """
