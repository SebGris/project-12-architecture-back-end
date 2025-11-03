"""Contract service module for Epic Events CRM.

This module contains the business logic for managing contracts.
"""

from decimal import Decimal
from typing import List, Optional

from src.models.contract import Contract
from src.repositories.contract_repository import ContractRepository


class ContractService:
    """Service for managing contract-related business logic.

    This service handles all contract operations including creation,
    retrieval, and validation of contract data.
    """

    def __init__(self, repository: ContractRepository) -> None:
        self.repository = repository

    def get_contract(self, contract_id: int) -> Optional[Contract]:
        """Get a contract by ID.

        Args:
            contract_id: The contract's ID

        Returns:
            Contract instance or None if not found
        """
        return self.repository.get(contract_id)

    def create_contract(
        self,
        client_id: int,
        total_amount: Decimal,
        remaining_amount: Decimal,
        is_signed: bool = False,
    ) -> Contract:
        """Create a new contract in the database.

        Args:
            client_id: ID of the client for this contract
            total_amount: Total amount of the contract
            remaining_amount: Remaining amount to be paid
            is_signed: Whether the contract is signed (default: False)

        Returns:
            The created Contract instance

        Raises:
            ValueError: If remaining_amount > total_amount or amounts are negative
        """
        contract = Contract(
            client_id=client_id,
            total_amount=total_amount,
            remaining_amount=remaining_amount,
            is_signed=is_signed,
        )
        return self.repository.add(contract)

    def get_contracts_by_client(self, client_id: int) -> List[Contract]:
        """Get all contracts for a specific client.

        Args:
            client_id: The client's ID

        Returns:
            List of Contract instances for the client
        """
        return self.repository.get_by_client_id(client_id)

    def get_unsigned_contracts(self) -> List[Contract]:
        """Get all unsigned contracts.

        Returns:
            List of unsigned Contract instances
        """
        return self.repository.get_unsigned_contracts()

    def get_unpaid_contracts(self) -> List[Contract]:
        """Get all contracts with remaining amount > 0.

        Returns:
            List of Contract instances with unpaid balance
        """
        return self.repository.get_unpaid_contracts()

    def update_contract_payment(
        self, contract_id: int, amount_paid: Decimal
    ) -> Optional[Contract]:
        """Update a contract with a payment.

        Args:
            contract_id: The contract's ID
            amount_paid: Amount being paid

        Returns:
            Updated Contract instance or None if not found

        Raises:
            ValueError: If payment amount is invalid
        """
        contract = self.repository.get(contract_id)
        if not contract:
            return None

        contract.remaining_amount -= amount_paid
        return self.repository.update(contract)

    def sign_contract(self, contract_id: int) -> Optional[Contract]:
        """Sign a contract.

        Args:
            contract_id: The contract's ID

        Returns:
            Updated Contract instance or None if not found
        """
        contract = self.repository.get(contract_id)
        if not contract:
            return None  # verifier les retours None

        contract.is_signed = True
        return self.repository.update(contract)
