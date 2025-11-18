import typer
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from datetime import datetime

from src.cli import console
from src.cli import validators
from src.models.user import Department
from src.containers import Container
from src.cli.permissions import require_department
from src.cli.business_logic import (
    create_client_logic,
    create_contract_logic,
    create_event_logic,
    create_user_logic,
    sign_contract_logic,
    update_client_logic,
    update_contract_logic,
    update_contract_payment_logic,
)

app = typer.Typer()

# Constants for field labels to avoid string duplication (SonarQube python:S1192)
LABEL_USERNAME = "Nom d'utilisateur"
LABEL_DEPARTMENT = "Département"
LABEL_ID = "ID"
LABEL_EMAIL = "Email"
LABEL_PHONE = "Téléphone"
LABEL_CONTACT_COMMERCIAL = "Contact commercial"
LABEL_SUPPORT_CONTACT = "Support contact"
LABEL_DATE_CREATION = "Date de création"
LABEL_MONTANT_TOTAL = "Montant total"
LABEL_MONTANT_RESTANT = "Montant restant à payer"
LABEL_CLIENT = "Client"
LABEL_EVENT_ID = "Event ID"
LABEL_CONTRACT_ID = "Contract ID"
LABEL_CLIENT_NAME = "Client name"
LABEL_CLIENT_CONTACT = "Client contact"
LABEL_EVENT_DATE_START = "Event date start"
LABEL_EVENT_DATE_END = "Event date end"
LABEL_LOCATION = "Location"
LABEL_ATTENDEES = "Attendees"
LABEL_NOTES = "Notes"
LABEL_STATUT = "Statut"
LABEL_NON_ASSIGNE = "Non assigné"

# Constants for formats
FORMAT_DATETIME = "%Y-%m-%d %H:%M:%S"
FORMAT_DATE = "%Y-%m-%d"

# Constants for status messages
STATUS_SIGNED = "Signé ✓"
STATUS_UNSIGNED = "Non signé ✗"

# Constants for error messages
ERROR_UNEXPECTED = "Erreur inattendue: {e}"
ERROR_INTEGRITY = "Erreur d'intégrité de la base de données: {error_msg}"

# Additional constants for prompts and error checks
LABEL_ID_CONTRAT = "ID du contrat"
PROMPT_TELEPHONE = "Téléphone"
PROMPT_ID_CONTRAT = "ID du contrat"
ERROR_FOREIGN_KEY = "foreign key"


def format_event_datetime(dt: datetime) -> str:
    """Format datetime for event display (e.g., '4 Jun 2023 @ 1PM')."""
    # Get hour in 12-hour format and remove leading zero
    hour_12 = dt.strftime("%I").lstrip("0") or "12"
    # Get AM/PM
    am_pm = dt.strftime("%p")
    # Get date part
    date_part = dt.strftime("%d %b %Y")
    # Remove leading zero from day if present
    if date_part.startswith("0"):
        date_part = date_part[1:]
    return f"{date_part} @ {hour_12}{am_pm}"


@app.command()
def login(
    username: str = typer.Option(..., prompt=LABEL_USERNAME),
    password: str = typer.Option(..., prompt="Mot de passe", hide_input=True),
):
    """
    Se connecter à l'application Epic Events CRM.

    Cette commande permet de s'authentifier avec un nom d'utilisateur et un mot de passe.
    Un jeton JWT est généré et stocké localement pour une authentification persistante.

    Args:
        username: Nom d'utilisateur
        password: Mot de passe (masqué lors de la saisie)

    Returns:
        None. Affiche un message de succès ou d'erreur.

    Examples:
        epicevents login
    """
    # Manually get auth_service from container
    container = Container()
    auth_service = container.auth_service()

    console.print_separator()
    console.print_header("Authentification")
    console.print_separator()

    # Authenticate user
    user = auth_service.authenticate(username, password)

    if not user:
        console.print_error("Nom d'utilisateur ou mot de passe incorrect")
        raise typer.Exit(code=1)

    # Generate JWT token
    token = auth_service.generate_token(user)

    # Save token to disk
    auth_service.save_token(token)

    # Set Sentry user context
    from src.sentry_config import set_user_context

    set_user_context(user.id, user.username, user.department.value)

    # Success message
    console.print_separator()
    console.print_success(f"Bienvenue {user.first_name} {user.last_name} !")
    console.print_field(LABEL_DEPARTMENT, user.department.value)
    console.print_field("Session", "Valide pour 24 heures")
    console.print_separator()


@app.command()
def logout():
    """
    Se déconnecter de l'application Epic Events CRM.

    Cette commande supprime le jeton JWT stocké localement.

    Returns:
        None. Affiche un message de confirmation.

    Examples:
        epicevents logout
    """
    # Manually get auth_service from container
    container = Container()
    auth_service = container.auth_service()

    console.print_separator()
    console.print_header("Déconnexion")
    console.print_separator()

    # Check if user is authenticated
    user = auth_service.get_current_user()

    if not user:
        console.print_error("Vous n'êtes pas connecté")
        raise typer.Exit(code=1)

    # Delete token
    auth_service.delete_token()

    # Clear Sentry user context
    from src.sentry_config import clear_user_context, add_breadcrumb

    add_breadcrumb(
        f"Déconnexion de l'utilisateur: {user.username}",
        category="auth",
        level="info",
    )
    clear_user_context()

    # Success message
    console.print_success(f"Au revoir {user.first_name} {user.last_name} !")
    console.print_separator()


@app.command()
def whoami():
    """
    Afficher les informations de l'utilisateur actuellement connecté.

    Cette commande affiche les détails de l'utilisateur authentifié.

    Returns:
        None. Affiche les informations de l'utilisateur ou un message d'erreur.

    Examples:
        epicevents whoami
    """
    # Manually get auth_service from container
    container = Container()
    auth_service = container.auth_service()

    console.print_separator()
    console.print_header("Utilisateur actuel")
    console.print_separator()

    # Get current user
    user = auth_service.get_current_user()

    if not user:
        console.print_error(
            "Vous n'êtes pas connecté. Utilisez 'epicevents login' pour vous connecter."
        )
        raise typer.Exit(code=1)

    # Display user info
    console.print_field(LABEL_ID, str(user.id))
    console.print_field(LABEL_USERNAME, user.username)
    console.print_field("Nom complet", f"{user.first_name} {user.last_name}")
    console.print_field(LABEL_EMAIL, user.email)
    console.print_field(LABEL_PHONE, user.phone)
    console.print_field(LABEL_DEPARTMENT, user.department.value)
    console.print_separator()


@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def create_client(
    first_name: str = typer.Option(
        ..., prompt="Prénom", callback=validators.validate_first_name_callback
    ),
    last_name: str = typer.Option(
        ..., prompt="Nom", callback=validators.validate_last_name_callback
    ),
    email: str = typer.Option(
        ..., prompt="Email", callback=validators.validate_email_callback
    ),
    phone: str = typer.Option(
        ...,
        prompt=PROMPT_TELEPHONE,
        callback=validators.validate_phone_callback,
    ),
    company_name: str = typer.Option(
        ...,
        prompt="Nom de l'entreprise",
        callback=validators.validate_company_name_callback,
    ),
    sales_contact_id: int = typer.Option(
        0,
        prompt="ID du contact commercial, ENTRER pour auto-assignation (valeur par défaut: 0)",
        callback=validators.validate_sales_contact_id_callback,
    ),
):
    """
    Créer un nouveau client dans le système CRM.

    Cette commande permet d'enregistrer un nouveau client avec ses informations
    de contact et de l'associer à un contact commercial du département COMMERCIAL.

    Args:
        first_name: Prénom du client (minimum 2 caractères)
        last_name: Nom du client (minimum 2 caractères)
        email: Adresse email valide du client
        phone: Numéro de téléphone (minimum 10 chiffres)
        company_name: Nom de l'entreprise du client
        sales_contact_id: ID d'un utilisateur du département COMMERCIAL (auto-assigné si vide pour COMMERCIAL)

    Returns:
        None. Affiche un message de succès avec les détails du client créé.

    Raises:
        typer.Exit: En cas d'erreur (données invalides, contact inexistant, etc.)

    Examples:
        epicevents create-client
        # Suit les prompts interactifs pour saisir les informations
    """

    # Get container and current user
    container = Container()
    auth_service = container.auth_service()
    current_user = auth_service.get_current_user()

    # Show header
    console.print_separator()
    console.print_header("Création d'un nouveau client")
    console.print_separator()

    # Auto-assign for COMMERCIAL users if no sales_contact_id provided
    if sales_contact_id == 0:
        if current_user.department == Department.COMMERCIAL:
            sales_contact_id = current_user.id
            console.print_field(
                LABEL_CONTACT_COMMERCIAL,
                f"Auto-assigné à {current_user.username}",
            )
        else:
            console.print_error(
                "Vous devez spécifier un ID de contact commercial"
            )
            raise typer.Exit(code=1)

    try:
        # Call business logic
        client = create_client_logic(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company_name=company_name,
            sales_contact_id=sales_contact_id,
            container=container,
        )

    except ValueError as e:
        # Business logic errors (validation, authorization, etc.)
        console.print_separator()
        console.print_error(str(e))
        console.print_separator()
        raise typer.Exit(code=1)

    except IntegrityError as e:
        # Database constraint errors
        error_msg = (
            str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()
        )

        console.print_separator()
        if "unique" in error_msg or "duplicate" in error_msg:
            if "email" in error_msg:
                console.print_error(
                    f"Un client avec l'email '{email}' existe déjà dans le système"
                )
            else:
                console.print_error(
                    "Erreur: Un client avec ces informations existe déjà"
                )
        elif ERROR_FOREIGN_KEY in error_msg:
            console.print_error(
                f"Le contact commercial (ID: {sales_contact_id}) n'existe pas"
            )
        else:
            console.print_error(ERROR_INTEGRITY.format(error_msg=error_msg))
        console.print_separator()
        raise typer.Exit(code=1)

    except Exception as e:
        # Unexpected errors
        console.print_separator()
        console.print_error(ERROR_UNEXPECTED.format(e=e))
        console.print_separator()
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success(
        f"Client {client.first_name} {client.last_name} créé avec succès!"
    )
    console.print_field(LABEL_ID, str(client.id))
    console.print_field(LABEL_EMAIL, client.email)
    console.print_field(LABEL_PHONE, client.phone)
    console.print_field("Entreprise", client.company_name)
    console.print_field(
        LABEL_CONTACT_COMMERCIAL,
        f"{client.sales_contact.first_name} {client.sales_contact.last_name} (ID: {client.sales_contact_id})",
    )
    console.print_field(
        LABEL_DATE_CREATION, client.created_at.strftime(FORMAT_DATETIME)
    )
    console.print_separator()


@app.command()
@require_department(Department.GESTION)
def create_user(
    username: str = typer.Option(
        ...,
        prompt=LABEL_USERNAME,
        callback=validators.validate_username_callback,
    ),
    first_name: str = typer.Option(
        ..., prompt="Prénom", callback=validators.validate_first_name_callback
    ),
    last_name: str = typer.Option(
        ..., prompt="Nom", callback=validators.validate_last_name_callback
    ),
    email: str = typer.Option(
        ..., prompt="Email", callback=validators.validate_email_callback
    ),
    phone: str = typer.Option(
        ...,
        prompt=PROMPT_TELEPHONE,
        callback=validators.validate_phone_callback,
    ),
    password: str = typer.Option(
        ...,
        prompt="Mot de passe",
        hide_input=True,
        callback=validators.validate_password_callback,
    ),
    department_choice: int = typer.Option(
        ...,
        prompt=f"\nDépartements disponibles:\n1. {Department.COMMERCIAL.value}\n2. {Department.GESTION.value}\n3. {Department.SUPPORT.value}\n\nChoisir un département (numéro)",
        callback=validators.validate_department_callback,
    ),
):
    """
    Créer un nouvel utilisateur dans le système CRM.

    Cette commande permet d'enregistrer un nouvel utilisateur avec ses informations
    personnelles et professionnelles. Le mot de passe est automatiquement hashé
    avant d'être stocké en base de données.

    Args:
        username: Nom d'utilisateur unique (4-50 caractères, lettres/chiffres/_/-)
        first_name: Prénom de l'utilisateur (minimum 2 caractères)
        last_name: Nom de l'utilisateur (minimum 2 caractères)
        email: Adresse email valide et unique
        phone: Numéro de téléphone (minimum 10 chiffres)
        password: Mot de passe (minimum 8 caractères, sera hashé)
        department_choice: Choix du département (1=COMMERCIAL, 2=GESTION, 3=SUPPORT)

    Returns:
        None. Affiche un message de succès avec les détails de l'utilisateur créé.

    Raises:
        typer.Exit: En cas d'erreur (username/email déjà utilisé, données invalides, etc.)

    Examples:
        epicevents create-user
        # Suit les prompts interactifs pour saisir les informations
    """

    # Get container
    container = Container()

    # Show header
    console.print_separator()
    console.print_header("Création d'un nouvel utilisateur")
    console.print_separator()

    # Convert department choice (int) to Department enum
    departments = list(Department)
    department = departments[department_choice - 1]

    try:
        # Call business logic
        user = create_user_logic(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password=password,
            department=department,
            container=container,
        )

    except ValueError as e:
        # Business logic errors
        console.print_separator()
        console.print_error(str(e))
        console.print_separator()
        raise typer.Exit(code=1)

    except IntegrityError as e:
        # Database constraint errors
        error_msg = (
            str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()
        )

        console.print_separator()
        if "unique" in error_msg or "duplicate" in error_msg:
            if "username" in error_msg:
                console.print_error(
                    f"Le nom d'utilisateur '{username}' est déjà utilisé"
                )
            elif "email" in error_msg:
                console.print_error(
                    f"L'email '{email}' est déjà utilisé par un autre utilisateur"
                )
            else:
                console.print_error(
                    "Erreur: Un utilisateur avec ces informations existe déjà"
                )
        else:
            console.print_error(ERROR_INTEGRITY.format(error_msg=error_msg))
        console.print_separator()
        raise typer.Exit(code=1)

    except Exception as e:
        # Unexpected errors
        console.print_separator()
        console.print_error(ERROR_UNEXPECTED.format(e=e))
        console.print_separator()
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success(f"Utilisateur {user.username} créé avec succès!")
    console.print_field(LABEL_ID, str(user.id))
    console.print_field("Nom complet", f"{user.first_name} {user.last_name}")
    console.print_field(LABEL_EMAIL, user.email)
    console.print_field(LABEL_DEPARTMENT, user.department.value)
    console.print_separator()


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
    """
    Créer un nouveau contrat dans le système CRM.

    Cette commande permet d'enregistrer un nouveau contrat associé à un client
    existant, avec des montants et un statut de signature.

    Args:
        client_id: ID du client (doit exister dans la base)
        total_amount: Montant total du contrat (doit être >= 0)
        remaining_amount: Montant restant à payer (doit être >= 0 et <= total_amount)
        is_signed: Statut de signature du contrat (True/False)

    Returns:
        None. Affiche un message de succès avec les détails du contrat créé.

    Raises:
        typer.Exit: En cas d'erreur (client inexistant, montants invalides, etc.)

    Examples:
        epicevents create-contract
        # Suit les prompts interactifs pour saisir les informations
    """
    from decimal import Decimal

    # Get container and current user
    container = Container()
    auth_service = container.auth_service()
    current_user = auth_service.get_current_user()

    # Show header
    console.print_separator()
    console.print_header("Création d'un nouveau contrat")
    console.print_separator()

    # Convert amounts to Decimal
    try:
        total_decimal = Decimal(total_amount)
        remaining_decimal = Decimal(remaining_amount)
    except Exception:
        console.print_error("Erreur de conversion des montants")
        raise typer.Exit(code=1)

    try:
        # Call business logic
        contract = create_contract_logic(
            client_id=client_id,
            total_amount=total_decimal,
            remaining_amount=remaining_decimal,
            is_signed=is_signed,
            current_user=current_user,
            container=container,
        )

        # Get client for success message
        client_service = container.client_service()
        client = client_service.get_client(client_id)

    except ValueError as e:
        # Business logic errors (validation, authorization, etc.)
        console.print_separator()
        console.print_error(str(e))
        console.print_separator()
        raise typer.Exit(code=1)

    except IntegrityError as e:
        error_msg = (
            str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()
        )

        if ERROR_FOREIGN_KEY in error_msg:
            console.print_error(f"Le client (ID: {client_id}) n'existe pas")
        else:
            console.print_error(ERROR_INTEGRITY.format(error_msg=error_msg))
        raise typer.Exit(code=1)

    except Exception as e:
        console.print_error(ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    # Success message
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
        LABEL_CONTACT_COMMERCIAL,
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
        LABEL_DATE_CREATION, contract.created_at.strftime(FORMAT_DATETIME)
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
):
    """
    Signer un contrat existant.

    Cette commande permet à un commercial de signer un contrat pour l'un de ses clients.
    Seul le commercial assigné au client peut signer le contrat.

    Args:
        contract_id: ID du contrat à signer

    Returns:
        None. Affiche un message de succès avec les détails du contrat signé.

    Raises:
        typer.Exit: En cas d'erreur (contrat inexistant, déjà signé, non autorisé, etc.)

    Examples:
        epicevents sign-contract --contract-id 1
        # ou de manière interactive
        epicevents sign-contract
    """
    # Get container and current user
    container = Container()
    auth_service = container.auth_service()
    current_user = auth_service.get_current_user()

    # Show header
    console.print_separator()
    console.print_header("Signature d'un contrat")
    console.print_separator()

    try:
        # Call business logic
        contract = sign_contract_logic(
            contract_id=contract_id,
            current_user=current_user,
            container=container,
        )

        # Get client for success message
        client_service = container.client_service()
        client = client_service.get_client(contract.client_id)

    except ValueError as e:
        # Business logic errors (validation, authorization, etc.)
        console.print_separator()
        console.print_error(str(e))
        console.print_separator()
        raise typer.Exit(code=1)

    except Exception as e:
        console.print_error(ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    # Success message
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
        LABEL_DATE_CREATION, contract.created_at.strftime(FORMAT_DATETIME)
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
):
    """
    Enregistrer un paiement pour un contrat.

    Cette commande permet à un commercial d'enregistrer un paiement effectué par un client.
    Le montant restant du contrat sera automatiquement mis à jour.

    Args:
        contract_id: ID du contrat
        amount_paid: Montant du paiement effectué

    Returns:
        None. Affiche un message de succès avec les nouveaux montants.

    Raises:
        typer.Exit: En cas d'erreur (contrat inexistant, montant invalide, non autorisé, etc.)

    Examples:
        epicevents update-contract-payment --contract-id 1 --amount-paid 5000
        # ou de manière interactive
        epicevents update-contract-payment
    """
    from decimal import Decimal

    # Get container and current user
    container = Container()
    auth_service = container.auth_service()
    current_user = auth_service.get_current_user()

    # Show header
    console.print_separator()
    console.print_header("Enregistrement d'un paiement")
    console.print_separator()

    # Convert amount to Decimal
    try:
        amount_decimal = Decimal(amount_paid)
    except Exception:
        console.print_error("Erreur de conversion du montant")
        raise typer.Exit(code=1)

    try:
        # Call business logic
        contract = update_contract_payment_logic(
            contract_id=contract_id,
            amount_paid=amount_decimal,
            current_user=current_user,
            container=container,
        )

        # Get client for success message
        client_service = container.client_service()
        client = client_service.get_client(contract.client_id)

    except ValueError as e:
        # Business logic errors (validation, authorization, etc.)
        console.print_separator()
        console.print_error(str(e))
        console.print_separator()
        raise typer.Exit(code=1)

    except Exception as e:
        console.print_error(ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    # Success message
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
def create_event(
    name: str = typer.Option(
        ...,
        prompt="Nom de l'événement",
        callback=validators.validate_event_name_callback,
    ),
    contract_id: int = typer.Option(
        ...,
        prompt=PROMPT_ID_CONTRAT,
        callback=validators.validate_contract_id_callback,
    ),
    event_start: str = typer.Option(
        ..., prompt="Date et heure de début (YYYY-MM-DD HH:MM)"
    ),
    event_end: str = typer.Option(
        ..., prompt="Date et heure de fin (YYYY-MM-DD HH:MM)"
    ),
    location: str = typer.Option(
        ..., prompt="Lieu", callback=validators.validate_location_callback
    ),
    attendees: int = typer.Option(
        ...,
        prompt="Nombre de participants",
        callback=validators.validate_attendees_callback,
    ),
    notes: str = typer.Option("", prompt="Notes (optionnel)"),
    support_contact_id: int = typer.Option(
        0, prompt="ID du contact support (0 si aucun)"
    ),
):
    """
    Créer un nouvel événement dans le système CRM.

    Cette commande permet d'enregistrer un nouvel événement associé à un contrat
    existant, avec des détails sur la date, le lieu et le nombre de participants.

    Args:
        name: Nom de l'événement (minimum 3 caractères)
        contract_id: ID du contrat associé (doit exister dans la base)
        event_start: Date et heure de début (format: YYYY-MM-DD HH:MM)
        event_end: Date et heure de fin (format: YYYY-MM-DD HH:MM)
        location: Lieu de l'événement
        attendees: Nombre de participants attendus (>= 0)
        notes: Notes optionnelles sur l'événement
        support_contact_id: ID optionnel du contact support (utilisateur SUPPORT)

    Returns:
        None. Affiche un message de succès avec les détails de l'événement créé.

    Raises:
        typer.Exit: En cas d'erreur (contrat inexistant, dates invalides, etc.)

    Examples:
        epicevents create-event
        # Suit les prompts interactifs pour saisir les informations
    """

    # Get container
    container = Container()
    contract_service = container.contract_service()

    # Show header at the beginning
    console.print_separator()
    console.print_header("Création d'un nouvel événement")
    console.print_separator()

    # Parse datetime strings (UI concern)
    try:
        start_dt = datetime.strptime(event_start, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(event_end, "%Y-%m-%d %H:%M")
    except ValueError:
        console.print_error(
            "Format de date invalide. Utilisez le format: YYYY-MM-DD HH:MM"
        )
        raise typer.Exit(code=1)

    # Clean support contact ID (UI concern)
    support_id = support_contact_id if support_contact_id > 0 else None

    # Call business logic
    try:
        event = create_event_logic(
            name=name,
            contract_id=contract_id,
            event_start=start_dt,
            event_end=end_dt,
            location=location,
            attendees=attendees,
            notes=notes if notes else None,
            support_contact_id=support_id,
            container=container,
        )
    except ValueError as e:
        console.print_error(str(e))
        raise typer.Exit(code=1)
    except IntegrityError as e:
        error_msg = (
            str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()
        )
        if ERROR_FOREIGN_KEY in error_msg:
            if "contract" in error_msg:
                console.print_error(
                    f"Le contrat (ID: {contract_id}) n'existe pas"
                )
            elif "support" in error_msg:
                console.print_error(
                    f"Le contact support (ID: {support_id}) n'existe pas"
                )
        else:
            console.print_error(ERROR_INTEGRITY.format(error_msg=error_msg))
        raise typer.Exit(code=1)
    except Exception as e:
        console.print_error(ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    # Get contract for display
    contract = contract_service.get_contract(contract_id)

    # Success message
    console.print_separator()
    console.print_success(f"Événement '{event.name}' créé avec succès!")
    console.print_field(LABEL_EVENT_ID, str(event.id))
    console.print_field(LABEL_CONTRACT_ID, str(contract.id))
    console.print_field(
        LABEL_CLIENT_NAME,
        f"{contract.client.first_name} {contract.client.last_name}",
    )
    console.print_field(
        LABEL_CLIENT_CONTACT,
        f"{contract.client.email}\n{contract.client.phone}",
    )
    console.print_field(
        LABEL_EVENT_DATE_START, format_event_datetime(event.event_start)
    )
    console.print_field(
        LABEL_EVENT_DATE_END, format_event_datetime(event.event_end)
    )
    if event.support_contact:
        console.print_field(
            LABEL_SUPPORT_CONTACT,
            f"{event.support_contact.first_name} {event.support_contact.last_name} (ID: {event.support_contact_id})",
        )
    else:
        console.print_field(LABEL_SUPPORT_CONTACT, LABEL_NON_ASSIGNE)
    console.print_field(LABEL_LOCATION, event.location)
    console.print_field(LABEL_ATTENDEES, str(event.attendees))
    if event.notes:
        console.print_field(LABEL_NOTES, event.notes)
    console.print_separator()


@app.command()
@require_department(Department.GESTION)
def assign_support(
    event_id: int = typer.Option(
        ...,
        prompt="ID de l'événement",
        callback=validators.validate_event_id_callback,
    ),
    support_contact_id: int = typer.Option(
        ...,
        prompt="ID du contact support",
        callback=validators.validate_user_id_callback,
    ),
):
    """
    Assigner un contact support à un événement.

    Cette commande permet d'assigner ou de réassigner un utilisateur du département
    SUPPORT à un événement existant.

    Args:
        event_id: ID de l'événement
        support_contact_id: ID de l'utilisateur SUPPORT à assigner

    Returns:
        None. Affiche un message de succès avec les détails.

    Raises:
        typer.Exit: En cas d'erreur (événement inexistant, utilisateur non SUPPORT, etc.)

    Examples:
        epicevents assign-support
    """
    # Manually get services from container
    container = Container()
    event_service = container.event_service()
    user_service = container.user_service()

    console.print_separator()
    console.print_header("Assignation d'un contact support")
    console.print_separator()

    # Vérifier que l'événement existe
    event = event_service.get_event(event_id)
    if not event:
        console.print_error(f"Événement avec l'ID {event_id} n'existe pas")
        raise typer.Exit(code=1)

    # Vérifier que l'utilisateur existe et est du département SUPPORT
    user = user_service.get_user(support_contact_id)
    if not user:
        console.print_error(
            f"Utilisateur avec l'ID {support_contact_id} n'existe pas"
        )
        raise typer.Exit(code=1)

    try:
        validators.validate_user_is_support(user)
    except ValueError as e:
        console.print_error(str(e))
        raise typer.Exit(code=1)

    # Assigner le contact support
    try:
        updated_event = event_service.assign_support_contact(
            event_id, support_contact_id
        )
    except Exception as e:
        console.print_error(f"Erreur lors de l'assignation: {e}")
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success(
        f"Contact support assigné avec succès à l'événement '{updated_event.name}'!"
    )
    console.print_field(LABEL_EVENT_ID, str(updated_event.id))
    console.print_field(LABEL_CONTRACT_ID, str(updated_event.contract_id))
    console.print_field(
        LABEL_CLIENT_NAME,
        f"{updated_event.contract.client.first_name} {updated_event.contract.client.last_name}",
    )
    console.print_field(
        LABEL_CLIENT_CONTACT,
        f"{updated_event.contract.client.email}\n{updated_event.contract.client.phone}",
    )
    console.print_field(
        "Event date start", format_event_datetime(updated_event.event_start)
    )
    console.print_field(
        LABEL_EVENT_DATE_END, format_event_datetime(updated_event.event_end)
    )
    console.print_field(
        "Support contact",
        f"{user.first_name} {user.last_name} (ID: {user.id})",
    )
    console.print_field(LABEL_LOCATION, updated_event.location)
    console.print_field(LABEL_ATTENDEES, str(updated_event.attendees))
    if updated_event.notes:
        console.print_field(LABEL_NOTES, updated_event.notes)
    console.print_separator()


@app.command()
@require_department()
def filter_unsigned_contracts():
    """
    Afficher tous les contrats non signés.

    Cette commande liste tous les contrats qui n'ont pas encore été signés.

    Returns:
        None. Affiche la liste des contrats non signés.

    Examples:
        epicevents filter-unsigned-contracts
    """
    # Manually get services from container
    container = Container()
    contract_service = container.contract_service()

    console.print_separator()
    console.print_header("Contrats non signés")
    console.print_separator()

    contracts = contract_service.get_unsigned_contracts()

    if not contracts:
        console.print_success("Aucun contrat non signé")
        return

    for contract in contracts:
        console.print_field(LABEL_ID, str(contract.id))
        console.print_field(
            LABEL_CLIENT,
            f"{contract.client.first_name} {contract.client.last_name} ({contract.client.company_name})",
        )
        console.print_field(
            LABEL_CONTACT_COMMERCIAL,
            f"{contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name} (ID: {contract.client.sales_contact_id})",
        )
        console.print_field(LABEL_MONTANT_TOTAL, f"{contract.total_amount} €")
        console.print_field(
            LABEL_MONTANT_RESTANT, f"{contract.remaining_amount} €"
        )
        console.print_field(
            LABEL_DATE_CREATION, contract.created_at.strftime(FORMAT_DATE)
        )
        console.print_separator()

    console.print_success(f"Total: {len(contracts)} contrat(s) non signé(s)")


@app.command()
@require_department()
def filter_unpaid_contracts():
    """
    Afficher tous les contrats non soldés (montant restant > 0).

    Cette commande liste tous les contrats qui ont un montant restant à payer.

    Returns:
        None. Affiche la liste des contrats non soldés.

    Examples:
        epicevents filter-unpaid-contracts
    """
    # Manually get services from container
    container = Container()
    contract_service = container.contract_service()

    console.print_separator()
    console.print_header("Contrats non soldés")
    console.print_separator()

    contracts = contract_service.get_unpaid_contracts()

    if not contracts:
        console.print_success("Aucun contrat non soldé")
        return

    for contract in contracts:
        console.print_field(LABEL_ID, str(contract.id))
        console.print_field(
            LABEL_CLIENT,
            f"{contract.client.first_name} {contract.client.last_name} ({contract.client.company_name})",
        )
        console.print_field(
            LABEL_CONTACT_COMMERCIAL,
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
            LABEL_DATE_CREATION, contract.created_at.strftime(FORMAT_DATE)
        )
        console.print_separator()

    console.print_success(f"Total: {len(contracts)} contrat(s) non soldé(s)")


@app.command()
@require_department()
def filter_unassigned_events():
    """
    Afficher tous les événements sans contact support assigné.

    Cette commande liste tous les événements qui n'ont pas encore de contact support.

    Returns:
        None. Affiche la liste des événements non assignés.

    Examples:
        epicevents filter-unassigned-events
    """
    # Manually get services from container
    container = Container()
    event_service = container.event_service()

    console.print_separator()
    console.print_header("Événements sans contact support")
    console.print_separator()

    events = event_service.get_unassigned_events()

    if not events:
        console.print_success("Aucun événement sans contact support")
        return

    for event in events:
        console.print_field(LABEL_EVENT_ID, str(event.id))
        console.print_field(LABEL_CONTRACT_ID, str(event.contract_id))
        console.print_field(
            LABEL_CLIENT_NAME,
            f"{event.contract.client.first_name} {event.contract.client.last_name}",
        )
        console.print_field(
            LABEL_CLIENT_CONTACT,
            f"{event.contract.client.email}\n{event.contract.client.phone}",
        )
        console.print_field(
            LABEL_EVENT_DATE_START, format_event_datetime(event.event_start)
        )
        console.print_field(
            LABEL_EVENT_DATE_END, format_event_datetime(event.event_end)
        )
        console.print_field(LABEL_SUPPORT_CONTACT, LABEL_NON_ASSIGNE)
        console.print_field(LABEL_LOCATION, event.location)
        console.print_field(LABEL_ATTENDEES, str(event.attendees))
        if event.notes:
            console.print_field(LABEL_NOTES, event.notes)
        console.print_separator()

    console.print_success(
        f"Total: {len(events)} événement(s) sans contact support"
    )


@app.command()
@require_department(Department.SUPPORT)
def filter_my_events():
    """
    Afficher mes événements assignés.

    Cette commande liste tous les événements assignés à l'utilisateur SUPPORT connecté.
    Aucun paramètre n'est nécessaire, l'utilisateur est automatiquement détecté.

    Returns:
        None. Affiche la liste des événements assignés à l'utilisateur connecté.

    Examples:
        epicevents filter-my-events
    """
    # Manually get services from container
    container = Container()
    event_service = container.event_service()
    auth_service = container.auth_service()

    console.print_separator()
    console.print_header("Mes événements")
    console.print_separator()

    # Get current user (already validated as SUPPORT by decorator)
    user = auth_service.get_current_user()

    events = event_service.get_events_by_support_contact(user.id)

    if not events:
        console.print_error(
            f"Aucun événement assigné à {user.first_name} {user.last_name}"
        )
        return

    for event in events:
        console.print_field(LABEL_EVENT_ID, str(event.id))
        console.print_field(LABEL_CONTRACT_ID, str(event.contract_id))
        console.print_field(
            LABEL_CLIENT_NAME,
            f"{event.contract.client.first_name} {event.contract.client.last_name}",
        )
        console.print_field(
            LABEL_CLIENT_CONTACT,
            f"{event.contract.client.email}\n{event.contract.client.phone}",
        )
        console.print_field(
            LABEL_EVENT_DATE_START, format_event_datetime(event.event_start)
        )
        console.print_field(
            LABEL_EVENT_DATE_END, format_event_datetime(event.event_end)
        )
        console.print_field(
            LABEL_SUPPORT_CONTACT,
            f"{user.first_name} {user.last_name} (ID: {user.id})",
        )
        console.print_field(LABEL_LOCATION, event.location)
        console.print_field(LABEL_ATTENDEES, str(event.attendees))
        if event.notes:
            console.print_field(LABEL_NOTES, event.notes)
        console.print_separator()

    console.print_success(
        f"Total: {len(events)} événement(s) assigné(s) à {user.first_name} {user.last_name}"
    )


@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def update_client(
    client_id: int = typer.Option(
        ...,
        prompt="ID du client",
        callback=validators.validate_client_id_callback,
    ),
    first_name: str = typer.Option(
        None, prompt="Nouveau prénom (laisser vide pour ne pas modifier)"
    ),
    last_name: str = typer.Option(
        None, prompt="Nouveau nom (laisser vide pour ne pas modifier)"
    ),
    email: str = typer.Option(
        None, prompt="Nouvel email (laisser vide pour ne pas modifier)"
    ),
    phone: str = typer.Option(
        None, prompt="Nouveau téléphone (laisser vide pour ne pas modifier)"
    ),
    company_name: str = typer.Option(
        None,
        prompt="Nouveau nom d'entreprise (laisser vide pour ne pas modifier)",
    ),
):
    """
    Mettre à jour les informations d'un client.

    Cette commande permet de modifier les informations d'un client existant.
    Les champs laissés vides ne seront pas modifiés.

    Args:
        client_id: ID du client à modifier
        first_name: Nouveau prénom (optionnel)
        last_name: Nouveau nom (optionnel)
        email: Nouvel email (optionnel)
        phone: Nouveau téléphone (optionnel)
        company_name: Nouveau nom d'entreprise (optionnel)

    Returns:
        None. Affiche un message de succès avec les détails.

    Raises:
        typer.Exit: En cas d'erreur (client inexistant, données invalides, etc.)

    Examples:
        epicevents update-client
    """
    # Get container and current user
    container = Container()
    auth_service = container.auth_service()
    current_user = auth_service.get_current_user()

    # Show header
    console.print_separator()
    console.print_header("Mise à jour d'un client")
    console.print_separator()

    # Clean empty fields
    first_name = first_name.strip() if first_name else None
    last_name = last_name.strip() if last_name else None
    email = email.strip() if email else None
    phone = phone.strip() if phone else None
    company_name = company_name.strip() if company_name else None

    try:
        # Call business logic
        updated_client = update_client_logic(
            client_id=client_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company_name=company_name,
            current_user=current_user,
            container=container,
        )

    except ValueError as e:
        # Business logic errors (validation, authorization, etc.)
        console.print_separator()
        console.print_error(str(e))
        console.print_separator()
        raise typer.Exit(code=1)

    except IntegrityError as e:
        error_msg = (
            str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()
        )
        if "unique" in error_msg or "duplicate" in error_msg:
            console.print_error(
                f"Un client avec l'email '{email}' existe déjà"
            )
        else:
            console.print_error(f"Erreur d'intégrité: {error_msg}")
        raise typer.Exit(code=1)

    except Exception as e:
        console.print_error(ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success("Client mis à jour avec succès!")
    console.print_field(LABEL_ID, str(updated_client.id))
    console.print_field(
        "Nom", f"{updated_client.first_name} {updated_client.last_name}"
    )
    console.print_field(LABEL_EMAIL, updated_client.email)
    console.print_field(LABEL_PHONE, updated_client.phone)
    console.print_field("Entreprise", updated_client.company_name)
    console.print_field(
        LABEL_CONTACT_COMMERCIAL,
        f"{updated_client.sales_contact.first_name} {updated_client.sales_contact.last_name} (ID: {updated_client.sales_contact_id})",
    )
    console.print_field(
        LABEL_DATE_CREATION,
        updated_client.created_at.strftime(FORMAT_DATETIME),
    )
    console.print_field(
        "Dernière mise à jour",
        updated_client.updated_at.strftime(FORMAT_DATETIME),
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
        None,
        prompt="Nouveau montant total (laisser vide pour ne pas modifier)",
    ),
    remaining_amount: str = typer.Option(
        None,
        prompt="Nouveau montant restant (laisser vide pour ne pas modifier)",
    ),
    is_signed: bool = typer.Option(None, prompt="Marquer comme signé ?"),
):
    """
    Mettre à jour les informations d'un contrat.

    Cette commande permet de modifier les informations d'un contrat existant.
    Les champs laissés vides ne seront pas modifiés.

    Args:
        contract_id: ID du contrat à modifier
        total_amount: Nouveau montant total (optionnel)
        remaining_amount: Nouveau montant restant (optionnel)
        is_signed: Marquer comme signé (optionnel)

    Returns:
        None. Affiche un message de succès avec les détails.

    Raises:
        typer.Exit: En cas d'erreur (contrat inexistant, montants invalides, etc.)

    Examples:
        epicevents update-contract
    """
    from decimal import Decimal

    # Get container and current user
    container = Container()
    auth_service = container.auth_service()
    current_user = auth_service.get_current_user()

    # Show header
    console.print_separator()
    console.print_header("Mise à jour d'un contrat")
    console.print_separator()

    # Clean and convert amounts
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

    try:
        # Call business logic
        updated_contract = update_contract_logic(
            contract_id=contract_id,
            total_amount=total_decimal,
            remaining_amount=remaining_decimal,
            is_signed=is_signed,
            current_user=current_user,
            container=container,
        )

    except ValueError as e:
        # Business logic errors (validation, authorization, etc.)
        console.print_separator()
        console.print_error(str(e))
        console.print_separator()
        raise typer.Exit(code=1)

    except Exception as e:
        console.print_error(f"Erreur lors de la mise à jour: {e}")
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success("Contrat mis à jour avec succès!")
    console.print_field(LABEL_ID, str(updated_contract.id))
    console.print_field(
        LABEL_CLIENT,
        f"{updated_contract.client.first_name} {updated_contract.client.last_name} ({updated_contract.client.company_name})",
    )
    console.print_field(
        LABEL_CONTACT_COMMERCIAL,
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
        LABEL_DATE_CREATION,
        updated_contract.created_at.strftime(FORMAT_DATETIME),
    )
    console.print_field(
        "Dernière mise à jour",
        updated_contract.updated_at.strftime(FORMAT_DATETIME),
    )
    console.print_separator()


@app.command()
@require_department(Department.GESTION, Department.SUPPORT)
def update_event_attendees(
    event_id: int = typer.Option(
        ...,
        prompt="ID de l'événement",
        callback=validators.validate_event_id_callback,
    ),
    attendees: int = typer.Option(
        ...,
        prompt="Nouveau nombre de participants",
        callback=validators.validate_attendees_callback,
    ),
):
    """
    Mettre à jour le nombre de participants d'un événement.

    Cette commande permet de modifier le nombre de participants attendus
    pour un événement existant.

    Args:
        event_id: ID de l'événement à modifier
        attendees: Nouveau nombre de participants (>= 0)

    Returns:
        None. Affiche un message de succès avec les détails de l'événement.

    Raises:
        typer.Exit: En cas d'erreur (événement inexistant, nombre invalide, etc.)

    Examples:
        epicevents update-event-attendees
        # Suit les prompts pour saisir l'ID et le nouveau nombre
    """
    # Manually get services from container
    container = Container()
    event_service = container.event_service()
    auth_service = container.auth_service()

    console.print_separator()
    console.print_header("Mise à jour du nombre de participants")
    console.print_separator()

    # Get current user for permission check
    current_user = auth_service.get_current_user()

    # Vérifier que l'événement existe
    event = event_service.get_event(event_id)
    if not event:
        console.print_error(f"Événement avec l'ID {event_id} n'existe pas")
        raise typer.Exit(code=1)

    # Permission check: SUPPORT can only update their own events
    if current_user.department == Department.SUPPORT:
        if (
            not event.support_contact_id
            or event.support_contact_id != current_user.id
        ):
            console.print_error(
                "Vous ne pouvez modifier que vos propres événements"
            )
            if event.support_contact:
                console.print_error(
                    f"Cet événement est assigné à {event.support_contact.first_name} {event.support_contact.last_name}"
                )
            else:
                console.print_error(
                    "Cet événement n'a pas encore de contact support assigné"
                )
            raise typer.Exit(code=1)

    # Business validation: validate attendees is positive
    try:
        validators.validate_attendees_positive(attendees)
    except ValueError as e:
        console.print_error(str(e))
        raise typer.Exit(code=1)

    # Mettre à jour le nombre de participants
    try:
        updated_event = event_service.update_attendees(event_id, attendees)
        if not updated_event:
            console.print_error(f"Événement avec l'ID {event_id} n'existe pas")
            raise typer.Exit(code=1)
    except Exception as e:
        console.print_error(f"Erreur lors de la mise à jour: {e}")
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success(
        f"Nombre de participants mis à jour avec succès pour l'événement #{event_id}!"
    )
    console.print_field(LABEL_ID, str(updated_event.id))
    console.print_field("Nom de l'événement", updated_event.name)
    console.print_field("Contrat ID", str(updated_event.contract_id))
    console.print_field(
        "Début", format_event_datetime(updated_event.event_start)
    )
    console.print_field("Fin", format_event_datetime(updated_event.event_end))
    console.print_field("Lieu", updated_event.location)
    console.print_field("Nombre de participants", str(updated_event.attendees))
    if updated_event.support_contact:
        console.print_field(
            LABEL_SUPPORT_CONTACT,
            f"{updated_event.support_contact.first_name} {updated_event.support_contact.last_name} (ID: {updated_event.support_contact_id})",
        )
    else:
        console.print_field(LABEL_SUPPORT_CONTACT, LABEL_NON_ASSIGNE)
    if updated_event.notes:
        console.print_field(LABEL_NOTES, updated_event.notes)
    console.print_separator()
