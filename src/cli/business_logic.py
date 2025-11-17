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
from src.models.user import User


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

    # Check permissions (only assigned sales contact can update)
    if client.sales_contact_id != current_user.id:
        raise ValueError("Vous n'êtes pas autorisé à modifier ce client")

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
    remaining_amount: Optional[Decimal],
    current_user: User,
    container: Container
) -> Contract:
    """Create a new contract for a client.

    Args:
        client_id: ID of the client
        total_amount: Total contract amount
        remaining_amount: Remaining amount to pay (defaults to total_amount)
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

    # Check permissions (only assigned sales contact can create contracts)
    if client.sales_contact_id != current_user.id:
        raise ValueError("Vous n'êtes pas autorisé à créer un contrat pour ce client")

    # Default remaining_amount to total_amount
    if remaining_amount is None:
        remaining_amount = total_amount

    # Create contract
    contract = contract_service.create_contract(
        client_id=client_id,
        total_amount=total_amount,
        remaining_amount=remaining_amount,
        is_signed=False
    )

    return contract


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
