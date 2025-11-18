"""
Business logic functions for CLI commands.

This module contains pure business logic extracted from CLI commands,
making it testable without Typer/CLI dependencies.
"""

from typing import Optional
from decimal import Decimal

from src.containers import Container
from src.models.client import Client
from src.models.contract import Contract
from src.models.user import Department, User


def create_user_logic(
    username: str,
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    password: str,
    department: Department,
    container: Container
) -> User:
    """Create a new user.

    Args:
        username: User's username (unique)
        first_name: User's first name
        last_name: User's last name
        email: User's email address (unique)
        phone: User's phone number
        password: User's password (will be hashed)
        department: User's department
        container: Dependency injection container

    Returns:
        Created User instance

    Raises:
        ValueError: If validation fails
    """
    user_service = container.user_service()

    # Create user (password will be hashed by the service)
    user = user_service.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        password=password,
        department=department
    )

    return user


def create_client_logic(
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    company_name: str,
    sales_contact_id: int,
    container: Container
) -> Client:
    """Create a new client.

    Args:
        first_name: Client's first name
        last_name: Client's last name
        email: Client's email address
        phone: Client's phone number
        company_name: Client's company name
        sales_contact_id: ID of the sales contact to assign
        container: Dependency injection container

    Returns:
        Created Client instance

    Raises:
        ValueError: If validation fails or user not found
    """
    client_service = container.client_service()
    user_service = container.user_service()

    # Verify sales contact exists
    sales_contact = user_service.get_user(sales_contact_id)
    if not sales_contact:
        raise ValueError(f"Commercial avec l'ID {sales_contact_id} introuvable")

    # Create client
    client = client_service.create_client(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        company_name=company_name,
        sales_contact_id=sales_contact_id
    )

    return client


def update_client_logic(
    client_id: int,
    first_name: Optional[str],
    last_name: Optional[str],
    email: Optional[str],
    phone: Optional[str],
    company_name: Optional[str],
    current_user: User,
    container: Container
) -> Client:
    """Update an existing client.

    Args:
        client_id: ID of the client to update
        first_name: New first name (optional)
        last_name: New last name (optional)
        email: New email (optional)
        phone: New phone (optional)
        company_name: New company name (optional)
        current_user: Currently authenticated user
        container: Dependency injection container

    Returns:
        Updated Client instance

    Raises:
        ValueError: If client not found or user not authorized
    """
    client_service = container.client_service()

    # Get client
    client = client_service.get_client(client_id)
    if not client:
        raise ValueError(f"Client avec l'ID {client_id} introuvable")

    # Check permissions: COMMERCIAL can only update their own clients
    # GESTION can update any client
    if current_user.department == Department.COMMERCIAL:
        if client.sales_contact_id != current_user.id:
            raise ValueError(
                f"Vous ne pouvez modifier que vos propres clients. "
                f"Ce client est assigné à {client.sales_contact.first_name} {client.sales_contact.last_name}"
            )

    # Validate fields if provided
    if first_name is not None and len(first_name) < 2:
        raise ValueError("Le prénom doit avoir au moins 2 caractères")

    if last_name is not None and len(last_name) < 2:
        raise ValueError("Le nom doit avoir au moins 2 caractères")

    # Update client
    updated_client = client_service.update_client(
        client_id=client_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        company_name=company_name
    )

    return updated_client


def create_contract_logic(
    client_id: int,
    total_amount: Decimal,
    remaining_amount: Decimal,
    is_signed: bool,
    current_user: User,
    container: Container
) -> Contract:
    """Create a new contract for a client.

    Args:
        client_id: ID of the client
        total_amount: Total contract amount
        remaining_amount: Remaining amount to pay
        is_signed: Contract signature status
        current_user: Currently authenticated user
        container: Dependency injection container

    Returns:
        Created Contract instance

    Raises:
        ValueError: If validation fails or client not found/unauthorized
    """
    contract_service = container.contract_service()
    client_service = container.client_service()

    # Get client
    client = client_service.get_client(client_id)
    if not client:
        raise ValueError(f"Client avec l'ID {client_id} introuvable")

    # Check permissions: COMMERCIAL can only create contracts for their own clients
    # GESTION can create contracts for any client
    if current_user.department == Department.COMMERCIAL:
        if client.sales_contact_id != current_user.id:
            raise ValueError("Vous n'êtes pas autorisé à créer un contrat pour ce client")

    # Validate contract amounts
    if total_amount < 0:
        raise ValueError("Le montant total doit être positif")

    if remaining_amount < 0:
        raise ValueError("Le montant restant doit être positif")

    if remaining_amount > total_amount:
        raise ValueError("Le montant restant ne peut pas dépasser le montant total")

    # Create contract
    contract = contract_service.create_contract(
        client_id=client_id,
        total_amount=total_amount,
        remaining_amount=remaining_amount,
        is_signed=is_signed
    )

    return contract


def update_contract_logic(
    contract_id: int,
    total_amount: Optional[Decimal],
    remaining_amount: Optional[Decimal],
    is_signed: Optional[bool],
    current_user: User,
    container: Container
) -> Contract:
    """Update an existing contract.

    Args:
        contract_id: ID of the contract to update
        total_amount: New total amount (optional)
        remaining_amount: New remaining amount (optional)
        is_signed: New signature status (optional)
        current_user: Currently authenticated user
        container: Dependency injection container

    Returns:
        Updated Contract instance

    Raises:
        ValueError: If validation fails or unauthorized
    """
    contract_service = container.contract_service()

    # Get contract
    contract = contract_service.get_contract(contract_id)
    if not contract:
        raise ValueError(f"Contrat avec l'ID {contract_id} introuvable")

    # Check permissions: COMMERCIAL can only update contracts of their own clients
    # GESTION can update any contract
    if current_user.department == Department.COMMERCIAL:
        if contract.client.sales_contact_id != current_user.id:
            raise ValueError(
                f"Vous ne pouvez modifier que les contrats de vos propres clients. "
                f"Ce contrat appartient au client {contract.client.first_name} {contract.client.last_name}, "
                f"assigné à {contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name}"
            )

    # Validate and update amounts if provided
    if total_amount is not None:
        if total_amount < 0:
            raise ValueError("Le montant total doit être positif")
        contract.total_amount = total_amount

    if remaining_amount is not None:
        if remaining_amount < 0:
            raise ValueError("Le montant restant doit être positif")
        contract.remaining_amount = remaining_amount

    # Update signature status if provided
    if is_signed is not None:
        contract.is_signed = is_signed

    # Final validation: remaining cannot exceed total
    if contract.remaining_amount > contract.total_amount:
        raise ValueError("Le montant restant ne peut pas dépasser le montant total")

    # Update contract
    updated_contract = contract_service.update_contract(contract)

    return updated_contract


def update_contract_payment_logic(
    contract_id: int,
    amount_paid: Decimal,
    current_user: User,
    container: Container
) -> Contract:
    """Update contract payment.

    Args:
        contract_id: ID of the contract to update
        amount_paid: Amount being paid
        current_user: Currently authenticated user
        container: Dependency injection container

    Returns:
        Updated Contract instance

    Raises:
        ValueError: If validation fails or unauthorized
    """
    contract_service = container.contract_service()
    client_service = container.client_service()

    # Get contract
    contract = contract_service.get_contract(contract_id)
    if not contract:
        raise ValueError(f"Contrat avec l'ID {contract_id} introuvable")

    # Get client to check permissions
    client = client_service.get_client(contract.client_id)
    if not client:
        raise ValueError("Client introuvable pour ce contrat")

    # Check permissions (only assigned sales contact can update payments)
    if client.sales_contact_id != current_user.id:
        raise ValueError("Vous n'êtes pas autorisé à modifier ce contrat")

    # Update payment
    updated_contract = contract_service.update_contract_payment(
        contract_id=contract_id,
        amount_paid=amount_paid
    )

    return updated_contract


def sign_contract_logic(
    contract_id: int,
    current_user: User,
    container: Container
) -> Contract:
    """Sign a contract.

    Args:
        contract_id: ID of the contract to sign
        current_user: Currently authenticated user
        container: Dependency injection container

    Returns:
        Signed Contract instance

    Raises:
        ValueError: If validation fails or unauthorized
    """
    contract_service = container.contract_service()
    client_service = container.client_service()

    # Get contract
    contract = contract_service.get_contract(contract_id)
    if not contract:
        raise ValueError(f"Contrat avec l'ID {contract_id} introuvable")

    # Check if already signed
    if contract.is_signed:
        raise ValueError("Ce contrat est déjà signé")

    # Get client to check permissions
    client = client_service.get_client(contract.client_id)
    if not client:
        raise ValueError("Client introuvable pour ce contrat")

    # Check permissions (only assigned sales contact can sign)
    if client.sales_contact_id != current_user.id:
        raise ValueError("Vous n'êtes pas autorisé à signer ce contrat")

    # Sign contract
    signed_contract = contract_service.sign_contract(contract_id)

    return signed_contract
