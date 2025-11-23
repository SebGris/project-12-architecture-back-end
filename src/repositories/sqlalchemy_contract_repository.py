"""SQLAlchemy implementation of ContractRepository.

This module provides the concrete implementation of the ContractRepository
interface using SQLAlchemy ORM.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.contract import Contract
from src.repositories.contract_repository import ContractRepository


class SqlAlchemyContractRepository(ContractRepository):
    """SQLAlchemy implementation of ContractRepository."""

    def __init__(self, session: Session):
        self.session = session

    def get(self, contract_id: int) -> Optional[Contract]:
        """Get a contract by ID.

        Args:
            contract_id: The contract's ID

        Returns:
            Contract instance or None if not found
        """
        return self.session.query(Contract).filter_by(id=contract_id).first()

    def add(self, contract: Contract) -> Contract:
        """Add a new contract to the repository.

        Args:
            contract: Contract instance to add

        Returns:
            The added Contract instance (with ID populated after commit)
        """
        self.session.add(contract)
        self.session.commit()
        self.session.refresh(contract)
        return contract

    def update(self, contract: Contract) -> Contract:
        """Update an existing contract in the repository.

        Args:
            contract: Contract instance to update (must have an ID)

        Returns:
            The updated Contract instance
        """
        contract = self.session.merge(contract)
        self.session.commit()
        self.session.refresh(contract)
        return contract

    def get_by_client_id(self, client_id: int) -> List[Contract]:
        """Get all contracts for a specific client.

        Args:
            client_id: The client's ID

        Returns:
            List of Contract instances for the client
        """
        return (
            self.session.query(Contract).filter_by(client_id=client_id).all()
        )

    def get_unsigned_contracts(self) -> List[Contract]:
        """Get all unsigned contracts.

        Returns:
            List of unsigned Contract instances
        """
        return self.session.query(Contract).filter_by(is_signed=False).all()

    def get_unpaid_contracts(self) -> List[Contract]:
        """Get all contracts with remaining amount > 0.

        Returns:
            List of Contract instances with unpaid balance
        """
        return (
            self.session.query(Contract)
            .filter(Contract.remaining_amount > 0)
            .all()
        )
