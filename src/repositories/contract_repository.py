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

    @abstractmethod
    def get_signed_contracts(self) -> List[Contract]:
        """Get all signed contracts.

        Returns:
            List of signed Contract instances
        """

    @abstractmethod
    def exists(self, contract_id: int) -> bool:
        """Check if a contract exists by ID.

        Args:
            contract_id: The contract's ID

        Returns:
            True if the contract exists, False otherwise
        """

    @abstractmethod
    def get_all(
        self, offset: int = 0, limit: int = 10
    ) -> List[Contract]:
        """Get contracts with pagination (read-only access for all departments).

        Args:
            offset: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 10)

        Returns:
            List of Contract instances
        """

    @abstractmethod
    def count(self) -> int:
        """Count total number of contracts.

        Returns:
            Total number of contracts in the repository
        """
