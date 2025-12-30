from decimal import Decimal

import typer

from src.cli import console
from src.cli import validators
from src.cli import constants as c
from src.cli.business_validator import BusinessValidator
from src.cli.pagination import paginate_display
from src.models.user import Department
from src.containers import Container
from src.cli.permissions import require_department

app = typer.Typer()

# Contract-specific constants
LABEL_MONTANT_TOTAL = "Montant total"
LABEL_MONTANT_RESTANT = "Montant restant à payer"
LABEL_CLIENT = "Client"
LABEL_STATUT = "Statut"
LABEL_ID_CONTRAT = "ID du contrat"
PROMPT_ID_CONTRAT = "ID du contrat"

# Status messages
STATUS_SIGNED = "Signé ✓"
STATUS_UNSIGNED = "Non signé ✗"


@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def create_contract(
    client_id: int = typer.Option(
        ...,
        prompt="ID du client",
        callback=validators.validate_client_id_callback,
    ),
    total_amount: str = typer.Option(
        ...,
        prompt="Montant total",
        callback=validators.validate_amount_callback,
    ),
    remaining_amount: str = typer.Option(
        ...,
        prompt="Montant restant",
        callback=validators.validate_amount_callback,
    ),
    is_signed: bool = typer.Option(False, prompt="Contrat signé ?"),
):
    """Create a new contract in the CRM system.

    This command registers a new contract associated with an existing client,
    with amounts and signature status.

    Args:
        client_id: Client ID (must exist in database)
        total_amount: Total contract amount (must be >= 0)
        remaining_amount: Remaining amount to pay (must be >= 0 and <= total_amount)
        is_signed: Contract signature status (True/False)

    Returns:
        None. Displays success message with created contract details.

    Raises:
        typer.Exit: On error (non-existent client, invalid amounts, etc.)

    Examples:
        epicevents create-contract
        # Follow interactive prompts to enter information
    """
    container = Container()
    contract_service = container.contract_service()
    client_service = container.client_service()

    console.print_command_header("Création d'un nouveau contrat")

    # Business validation: check if client exists
    client = client_service.get_client(client_id)

    if not client:
        console.print_error(f"Client avec l'ID {client_id} n'existe pas")
        raise typer.Exit(code=1)

    try:
        total_decimal = Decimal(total_amount)
        remaining_decimal = Decimal(remaining_amount)
    except Exception:
        console.print_error("Erreur de conversion des montants")
        raise typer.Exit(code=1)

    # Business validation: validate contract amounts
    try:
        BusinessValidator.validate_contract_amounts(total_decimal, remaining_decimal)
    except ValueError as e:
        console.print_error(str(e))
        raise typer.Exit(code=1)

    try:
        contract = contract_service.create_contract(
            client_id=client_id,
            total_amount=total_decimal,
            remaining_amount=remaining_decimal,
            is_signed=is_signed,
        )

    except Exception as e:
        console.print_error(c.ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    console.print_separator()
    console.print_success(
        f"Contrat créé avec succès pour le client {client.first_name} {client.last_name}!"
    )
    console.print_field(LABEL_ID_CONTRAT, str(contract.id))
    console.print_field(
        LABEL_CLIENT,
        f"{client.first_name} {client.last_name} ({client.company_name})",
    )
    console.print_field(
        c.LABEL_CONTACT_COMMERCIAL,
        f"{client.sales_contact.first_name} {client.sales_contact.last_name} (ID: {client.sales_contact_id})",
    )
    console.print_field(LABEL_MONTANT_TOTAL, f"{contract.total_amount} €")
    console.print_field(
        LABEL_MONTANT_RESTANT, f"{contract.remaining_amount} €"
    )
    console.print_field(
        LABEL_STATUT, STATUS_SIGNED if contract.is_signed else STATUS_UNSIGNED
    )
    console.print_field(
        c.LABEL_DATE_CREATION, contract.created_at.strftime(c.FORMAT_DATETIME)
    )
    console.print_separator()


@app.command()
@require_department(Department.COMMERCIAL)
def sign_contract(
    contract_id: int = typer.Option(
        ...,
        prompt="ID du contrat à signer",
        callback=validators.validate_contract_id_callback,
    ),
    current_user=None,
):
    """Sign an existing contract.

    This command allows a sales representative to sign a contract for one of their clients.
    Only the sales contact assigned to the client can sign the contract.

    Args:
        contract_id: ID of the contract to sign

    Returns:
        None. Displays success message with signed contract details.

    Raises:
        typer.Exit: On error (non-existent contract, already signed, unauthorized, etc.)

    Examples:
        epicevents sign-contract --contract-id 1
        # or interactively
        epicevents sign-contract
    """
    container = Container()
    contract_service = container.contract_service()
    client_service = container.client_service()

    console.print_command_header("Signature d'un contrat")

    contract = contract_service.get_contract(contract_id)
    if not contract:
        console.print_error(f"Contrat avec l'ID {contract_id} n'existe pas")
        raise typer.Exit(code=1)

    if contract.is_signed:
        console.print_error("Ce contrat est déjà signé")
        raise typer.Exit(code=1)

        client = client_service.get_client(contract.client_id)
    if not client:
        console.print_error(f"Client avec l'ID {contract.client_id} n'existe pas")
        raise typer.Exit(code=1)

    if client.sales_contact_id != current_user.id:
        console.print_error(
            f"Seul le commercial assigné au client peut signer ce contrat. "
            f"Ce client est assigné à {client.sales_contact.first_name} {client.sales_contact.last_name}"
        )
        raise typer.Exit(code=1)

    try:
        contract = contract_service.sign_contract(contract_id)
    except Exception as e:
        console.print_error(c.ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    console.print_separator()
    console.print_success(
        f"Contrat #{contract.id} signé avec succès pour {client.first_name} {client.last_name}!"
    )
    console.print_field(LABEL_ID_CONTRAT, str(contract.id))
    console.print_field(
        LABEL_CLIENT,
        f"{client.first_name} {client.last_name} ({client.company_name})",
    )
    console.print_field(LABEL_MONTANT_TOTAL, f"{contract.total_amount} €")
    console.print_field(
        LABEL_MONTANT_RESTANT, f"{contract.remaining_amount} €"
    )
    console.print_field(LABEL_STATUT, STATUS_SIGNED)
    console.print_field(
        c.LABEL_DATE_CREATION, contract.created_at.strftime(c.FORMAT_DATETIME)
    )
    console.print_separator()


@app.command()
@require_department(Department.COMMERCIAL)
def update_contract_payment(
    contract_id: int = typer.Option(
        ...,
        prompt="ID du contrat",
        callback=validators.validate_contract_id_callback,
    ),
    amount_paid: str = typer.Option(
        ...,
        prompt="Montant payé",
        callback=validators.validate_amount_callback,
    ),
    current_user=None,
):
    """Record a payment for a contract.

    This command allows a sales representative to record a payment made by a client.
    The contract's remaining amount will be automatically updated.

    Args:
        contract_id: Contract ID
        amount_paid: Payment amount made

    Returns:
        None. Displays success message with updated amounts.

    Raises:
        typer.Exit: On error (non-existent contract, invalid amount, unauthorized, etc.)

    Examples:
        epicevents update-contract-payment --contract-id 1 --amount-paid 5000
        # or interactively
        epicevents update-contract-payment
    """
    container = Container()
    contract_service = container.contract_service()
    client_service = container.client_service()

    console.print_command_header("Enregistrement d'un paiement")

    try:
        amount_decimal = Decimal(amount_paid)
    except Exception:
        console.print_error("Erreur de conversion du montant")
        raise typer.Exit(code=1)

    contract = contract_service.get_contract(contract_id)
    if not contract:
        console.print_error(f"Contrat avec l'ID {contract_id} n'existe pas")
        raise typer.Exit(code=1)

    client = client_service.get_client(contract.client_id)
    if not client:
        console.print_error(f"Client avec l'ID {contract.client_id} n'existe pas")
        raise typer.Exit(code=1)

    if client.sales_contact_id != current_user.id:
        console.print_error(
            f"Seul le commercial assigné au client peut enregistrer un paiement. "
            f"Ce client est assigné à {client.sales_contact.first_name} {client.sales_contact.last_name}"
        )
        raise typer.Exit(code=1)

    try:
        BusinessValidator.validate_payment_amount(amount_decimal, contract.remaining_amount)
    except ValueError as e:
        console.print_error(str(e))
        raise typer.Exit(code=1)

    try:
        contract = contract_service.update_contract_payment(contract_id, amount_decimal)
    except Exception as e:
        console.print_error(c.ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    console.print_separator()
    console.print_success(
        f"Paiement de {amount_decimal} € enregistré avec succès!"
    )
    console.print_field(LABEL_ID_CONTRAT, str(contract.id))
    console.print_field(
        LABEL_CLIENT,
        f"{client.first_name} {client.last_name} ({client.company_name})",
    )
    console.print_field(LABEL_MONTANT_TOTAL, f"{contract.total_amount} €")
    console.print_field(
        LABEL_MONTANT_RESTANT, f"{contract.remaining_amount} €"
    )
    console.print_field(
        "Montant payé",
        f"{contract.total_amount - contract.remaining_amount} €",
    )
    console.print_field(
        LABEL_STATUT, STATUS_SIGNED if contract.is_signed else STATUS_UNSIGNED
    )
    console.print_separator()


@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def update_contract(
    contract_id: int = typer.Option(
        ...,
        prompt=PROMPT_ID_CONTRAT,
        callback=validators.validate_contract_id_callback,
    ),
    total_amount: str = typer.Option(
        "",
        prompt="Nouveau montant total (laisser vide pour ne pas modifier)",
    ),
    remaining_amount: str = typer.Option(
        "",
        prompt="Nouveau montant restant (laisser vide pour ne pas modifier)",
    ),
    is_signed: bool = typer.Option(None, prompt="Marquer comme signé ?"),
    current_user=None,
):
    """Update contract information.

    This command modifies information for an existing contract.
    Fields left empty will not be modified.

    Args:
        contract_id: ID of the contract to modify
        total_amount: New total amount (optional)
        remaining_amount: New remaining amount (optional)
        is_signed: Mark as signed (optional)

    Returns:
        None. Displays success message with details.

    Raises:
        typer.Exit: On error (non-existent contract, invalid amounts, etc.)

    Examples:
        epicevents update-contract
    """
    container = Container()
    contract_service = container.contract_service()

    console.print_command_header("Mise à jour d'un contrat")

    # Vérifier que le contrat existe
    contract = contract_service.get_contract(contract_id)
    if not contract:
        console.print_error(f"Contrat avec l'ID {contract_id} n'existe pas")
        raise typer.Exit(code=1)

    # Permission check: COMMERCIAL can only update contracts of their own clients
    if current_user.department == Department.COMMERCIAL:
        if contract.client.sales_contact_id != current_user.id:
            console.print_error(
                "Vous ne pouvez modifier que les contrats de vos propres clients"
            )
            console.print_error(
                f"Ce contrat appartient au client {contract.client.first_name} {contract.client.last_name}, "
                f"assigné à {contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name}"
            )
            raise typer.Exit(code=1)

    # Nettoyer et convertir les montants
    total_decimal = None
    remaining_decimal = None

    if total_amount:
        total_amount = total_amount.strip()
        try:
            total_decimal = Decimal(total_amount)
        except Exception:
            console.print_error("Montant total invalide")
            raise typer.Exit(code=1)

    if remaining_amount:
        remaining_amount = remaining_amount.strip()
        try:
            remaining_decimal = Decimal(remaining_amount)
        except Exception:
            console.print_error("Montant restant invalide")
            raise typer.Exit(code=1)

    # Validation des montants
    if total_decimal is not None and total_decimal < 0:
        console.print_error("Le montant total doit être positif")
        raise typer.Exit(code=1)

    if remaining_decimal is not None and remaining_decimal < 0:
        console.print_error("Le montant restant doit être positif")
        raise typer.Exit(code=1)

    # Mettre à jour les valeurs
    if total_decimal is not None:
        contract.total_amount = total_decimal
    if remaining_decimal is not None:
        contract.remaining_amount = remaining_decimal
    if is_signed is not None:
        contract.is_signed = is_signed

    # Validation finale
    if contract.remaining_amount > contract.total_amount:
        console.print_error(
            "Le montant restant ne peut pas dépasser le montant total"
        )
        raise typer.Exit(code=1)

    try:
        updated_contract = contract_service.update_contract(contract)
    except Exception as e:
        console.print_error(f"Erreur lors de la mise à jour: {e}")
        raise typer.Exit(code=1)

    console.print_separator()
    console.print_success("Contrat mis à jour avec succès!")
    console.print_field(c.LABEL_ID, str(updated_contract.id))
    console.print_field(
        LABEL_CLIENT,
        f"{updated_contract.client.first_name} {updated_contract.client.last_name} ({updated_contract.client.company_name})",
    )
    console.print_field(
        c.LABEL_CONTACT_COMMERCIAL,
        f"{updated_contract.client.sales_contact.first_name} {updated_contract.client.sales_contact.last_name} (ID: {updated_contract.client.sales_contact_id})",
    )
    console.print_field(
        LABEL_MONTANT_TOTAL, f"{updated_contract.total_amount} €"
    )
    console.print_field(
        "Montant restant à payer", f"{updated_contract.remaining_amount} €"
    )
    console.print_field(
        "Statut",
        STATUS_SIGNED if updated_contract.is_signed else STATUS_UNSIGNED,
    )
    console.print_field(
        c.LABEL_DATE_CREATION,
        updated_contract.created_at.strftime(c.FORMAT_DATETIME),
    )
    console.print_field(
        "Dernière mise à jour",
        updated_contract.updated_at.strftime(c.FORMAT_DATETIME),
    )
    console.print_separator()


@app.command()
@require_department()
def filter_unsigned_contracts():
    """Display all unsigned contracts.

    This command lists all contracts that have not yet been signed.

    Returns:
        None. Displays the list of unsigned contracts.

    Examples:
        epicevents filter-unsigned-contracts
    """
    container = Container()
    contract_service = container.contract_service()

    console.print_command_header("Contrats non signés")

    contracts = contract_service.get_unsigned_contracts()

    if not contracts:
        console.print_success("Aucun contrat non signé")
        return

    for contract in contracts:
        console.print_field(c.LABEL_ID, str(contract.id))
        console.print_field(
            LABEL_CLIENT,
            f"{contract.client.first_name} {contract.client.last_name} ({contract.client.company_name})",
        )
        console.print_field(
            c.LABEL_CONTACT_COMMERCIAL,
            f"{contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name} (ID: {contract.client.sales_contact_id})",
        )
        console.print_field(LABEL_MONTANT_TOTAL, f"{contract.total_amount} €")
        console.print_field(
            LABEL_MONTANT_RESTANT, f"{contract.remaining_amount} €"
        )
        console.print_field(
            c.LABEL_DATE_CREATION, contract.created_at.strftime(c.FORMAT_DATE)
        )
        console.print_separator()

    console.print_success(f"Total: {len(contracts)} contrat(s) non signé(s)")


@app.command()
@require_department()
def filter_unpaid_contracts():
    """Display all unpaid contracts (remaining amount > 0).

    This command lists all contracts that have a remaining amount to pay.

    Returns:
        None. Displays the list of unpaid contracts.

    Examples:
        epicevents filter-unpaid-contracts
    """
    container = Container()
    contract_service = container.contract_service()

    console.print_command_header("Contrats non soldés")

    contracts = contract_service.get_unpaid_contracts()

    if not contracts:
        console.print_success("Aucun contrat non soldé")
        return

    for contract in contracts:
        console.print_field(c.LABEL_ID, str(contract.id))
        console.print_field(
            LABEL_CLIENT,
            f"{contract.client.first_name} {contract.client.last_name} ({contract.client.company_name})",
        )
        console.print_field(
            c.LABEL_CONTACT_COMMERCIAL,
            f"{contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name} (ID: {contract.client.sales_contact_id})",
        )
        console.print_field(LABEL_MONTANT_TOTAL, f"{contract.total_amount} €")
        console.print_field(
            LABEL_MONTANT_RESTANT, f"{contract.remaining_amount} €"
        )
        console.print_field(
            LABEL_STATUT,
            STATUS_SIGNED if contract.is_signed else STATUS_UNSIGNED,
        )
        console.print_field(
            c.LABEL_DATE_CREATION, contract.created_at.strftime(c.FORMAT_DATE)
        )
        console.print_separator()

    console.print_success(f"Total: {len(contracts)} contrat(s) non soldé(s)")


@app.command()
@require_department()
def filter_signed_contracts():
    """Display all signed contracts.

    This command lists all contracts that have been signed.

    Returns:
        None. Displays the list of signed contracts.

    Examples:
        epicevents filter-signed-contracts
    """
    container = Container()
    contract_service = container.contract_service()

    console.print_command_header("Contrats signés")

    contracts = contract_service.get_signed_contracts()

    if not contracts:
        console.print_success("Aucun contrat signé")
        return

    for contract in contracts:
        console.print_field(c.LABEL_ID, str(contract.id))
        console.print_field(
            LABEL_CLIENT,
            f"{contract.client.first_name} {contract.client.last_name} ({contract.client.company_name})",
        )
        console.print_field(
            c.LABEL_CONTACT_COMMERCIAL,
            f"{contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name} (ID: {contract.client.sales_contact_id})",
        )
        console.print_field(LABEL_MONTANT_TOTAL, f"{contract.total_amount} €")
        console.print_field(
            LABEL_MONTANT_RESTANT, f"{contract.remaining_amount} €"
        )
        console.print_field(
            c.LABEL_DATE_CREATION, contract.created_at.strftime(c.FORMAT_DATE)
        )
        console.print_separator()

    console.print_success(f"Total: {len(contracts)} contrat(s) signé(s)")


@app.command()
@require_department()
def list_contracts():
    """List all contracts in the system (read-only).

    This command displays all contracts registered in the CRM system.
    Available to all authenticated users (all departments) in read-only mode.
    Results are paginated with interactive navigation.

    Returns:
        None. Displays a paginated list of all contracts or a message if none found.

    Examples:
        epicevents list-contracts
    """
    container = Container()
    contract_service = container.contract_service()

    console.print_command_header("Liste des contrats")

    def display_contract(contract):
        console.print_field(c.LABEL_ID, str(contract.id))
        console.print_field(
            LABEL_CLIENT,
            f"{contract.client.first_name} {contract.client.last_name} ({contract.client.company_name})",
        )
        console.print_field(
            c.LABEL_CONTACT_COMMERCIAL,
            f"{contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name}",
        )
        console.print_field(LABEL_MONTANT_TOTAL, f"{contract.total_amount} €")
        console.print_field(
            LABEL_MONTANT_RESTANT, f"{contract.remaining_amount} €"
        )
        console.print_field(
            LABEL_STATUT,
            STATUS_SIGNED if contract.is_signed else STATUS_UNSIGNED,
        )
        console.print_field(
            c.LABEL_DATE_CREATION, contract.created_at.strftime(c.FORMAT_DATE)
        )

    paginate_display(
        fetch_page=contract_service.get_all_contracts,
        count_total=contract_service.count_contracts,
        display_item=display_contract,
        item_name="contrat",
    )
