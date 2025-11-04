import typer
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from src.cli.console import (
    print_error,
    print_field,
    print_header,
    print_separator,
    print_success,
)
from src.cli.validators import (
    validate_amount_callback,
    validate_attendees_callback,
    validate_client_id_callback,
    validate_company_name_callback,
    validate_contract_amounts,
    validate_contract_id_callback,
    validate_department_callback,
    validate_email_callback,
    validate_event_id_callback,
    validate_event_name_callback,
    validate_first_name_callback,
    validate_last_name_callback,
    validate_location_callback,
    validate_password_callback,
    validate_phone_callback,
    validate_sales_contact_id_callback,
    validate_user_id_callback,
    validate_username_callback,
)
from src.models.user import Department, User
from src.containers import Container
from src.cli.permissions import (
    require_auth,
    require_department,
    check_client_ownership,
    check_event_ownership,
)

app = typer.Typer()


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
    username: str = typer.Option(..., prompt="Nom d'utilisateur"),
    password: str = typer.Option(..., prompt="Mot de passe", hide_input=True)
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

    print_separator()
    print_header("Authentification")
    print_separator()

    # Authenticate user
    user = auth_service.authenticate(username, password)

    if not user:
        print_error("Nom d'utilisateur ou mot de passe incorrect")
        raise typer.Exit(code=1)

    # Generate JWT token
    token = auth_service.generate_token(user)

    # Save token to disk
    auth_service.save_token(token)

    # Set Sentry user context
    from src.sentry_config import set_user_context
    set_user_context(user.id, user.username, user.department.value)

    # Success message
    print_separator()
    print_success(f"Bienvenue {user.first_name} {user.last_name} !")
    print_field("Département", user.department.value)
    print_field("Session", f"Valide pour 24 heures")
    print_separator()


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

    print_separator()
    print_header("Déconnexion")
    print_separator()

    # Check if user is authenticated
    user = auth_service.get_current_user()

    if not user:
        print_error("Vous n'êtes pas connecté")
        raise typer.Exit(code=1)

    # Delete token
    auth_service.delete_token()

    # Clear Sentry user context
    from src.sentry_config import clear_user_context, add_breadcrumb
    add_breadcrumb(
        f"Déconnexion de l'utilisateur: {user.username}",
        category="auth",
        level="info"
    )
    clear_user_context()

    # Success message
    print_success(f"Au revoir {user.first_name} {user.last_name} !")
    print_separator()


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

    print_separator()
    print_header("Utilisateur actuel")
    print_separator()

    # Get current user
    user = auth_service.get_current_user()

    if not user:
        print_error("Vous n'êtes pas connecté. Utilisez 'epicevents login' pour vous connecter.")
        raise typer.Exit(code=1)

    # Display user info
    print_field("ID", str(user.id))
    print_field("Nom d'utilisateur", user.username)
    print_field("Nom complet", f"{user.first_name} {user.last_name}")
    print_field("Email", user.email)
    print_field("Téléphone", user.phone)
    print_field("Département", user.department.value)
    print_separator()


@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def create_client(
    first_name: str = typer.Option(
        ..., prompt="Prénom", callback=validate_first_name_callback
    ),
    last_name: str = typer.Option(
        ..., prompt="Nom", callback=validate_last_name_callback
    ),
    email: str = typer.Option(
        ..., prompt="Email", callback=validate_email_callback
    ),
    phone: str = typer.Option(
        ..., prompt="Téléphone", callback=validate_phone_callback
    ),
    company_name: str = typer.Option(
        ...,
        prompt="Nom de l'entreprise",
        callback=validate_company_name_callback,
    ),
    sales_contact_id: int = typer.Option(
        None,
        prompt="ID du contact commercial (laisser vide pour auto-assignation)",
    )
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
    # Manually get services from container
    container = Container()
    client_service = container.client_service()
    user_service = container.user_service()
    auth_service = container.auth_service()

    # Show header at the beginning
    print_separator()
    print_header("Création d'un nouveau client")
    print_separator()

    # Get current user for auto-assignment
    current_user = auth_service.get_current_user()

    # Auto-assign for COMMERCIAL users if no sales_contact_id provided
    if sales_contact_id is None:
        if current_user.department == Department.COMMERCIAL:
            sales_contact_id = current_user.id
            print_field("Contact commercial", f"Auto-assigné à {current_user.username}")
        else:
            print_error("Vous devez spécifier un ID de contact commercial")
            raise typer.Exit(code=1)

    # Business validation: check if sales contact exists and is from COMMERCIAL dept
    user = user_service.get_user(sales_contact_id)

    if not user:
        print_error(f"Utilisateur avec l'ID {sales_contact_id} n'existe pas")
        raise typer.Exit(code=1)

    if user.department != Department.COMMERCIAL:
        print_error(
            f"L'utilisateur {sales_contact_id} n'est pas du département COMMERCIAL"
        )
        raise typer.Exit(code=1)

    try:
        # Create client via service
        client = client_service.create_client(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company_name=company_name,
            sales_contact_id=sales_contact_id,
        )

    except IntegrityError as e:
        error_msg = (
            str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()
        )

        if "unique" in error_msg or "duplicate" in error_msg:
            if "email" in error_msg:
                print_error(
                    f"Un client avec l'email '{email}' existe déjà dans le système"
                )
            else:
                print_error(
                    "Erreur: Un client avec ces informations existe déjà"
                )
        elif "foreign key" in error_msg:
            print_error(
                f"Le contact commercial (ID: {sales_contact_id}) n'existe pas"
            )
        else:
            print_error(
                f"Erreur d'intégrité de la base de données: {error_msg}"
            )
        raise typer.Exit(code=1)

    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        raise typer.Exit(code=1)

    # Success message
    print_separator()
    print_success(
        f"Client {client.first_name} {client.last_name} créé avec succès!"
    )
    print_field("ID", str(client.id))
    print_field("Email", client.email)
    print_field("Téléphone", client.phone)
    print_field("Entreprise", client.company_name)
    print_field(
        "Contact commercial",
        f"{client.sales_contact.first_name} {client.sales_contact.last_name} (ID: {client.sales_contact_id})"
    )
    print_field(
        "Date de création", client.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )
    print_separator()


@app.command()
@require_department(Department.GESTION)
def create_user(
    username: str = typer.Option(
        ..., prompt="Nom d'utilisateur", callback=validate_username_callback
    ),
    first_name: str = typer.Option(
        ..., prompt="Prénom", callback=validate_first_name_callback
    ),
    last_name: str = typer.Option(
        ..., prompt="Nom", callback=validate_last_name_callback
    ),
    email: str = typer.Option(
        ..., prompt="Email", callback=validate_email_callback
    ),
    phone: str = typer.Option(
        ..., prompt="Téléphone", callback=validate_phone_callback
    ),
    password: str = typer.Option(
        ...,
        prompt="Mot de passe",
        hide_input=True,
        callback=validate_password_callback,
    ),
    department_choice: int = typer.Option(
        ...,
        prompt=f"\nDépartements disponibles:\n1. {Department.COMMERCIAL.value}\n2. {Department.GESTION.value}\n3. {Department.SUPPORT.value}\n\nChoisir un département (numéro)",
        callback=validate_department_callback,
    )
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
    # Manually get services from container
    container = Container()
    user_service = container.user_service()

    # Show header at the beginning
    print_separator()
    print_header("Création d'un nouvel utilisateur")
    print_separator()

    # Convert department choice (int) to Department enum
    departments = list(Department)
    department = departments[department_choice - 1]

    try:
        # Create user via service
        user = user_service.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password=password,
            department=department,
        )

    except IntegrityError as e:
        error_msg = (
            str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()
        )

        if "unique" in error_msg or "duplicate" in error_msg:
            if "username" in error_msg:
                print_error(
                    f"Le nom d'utilisateur '{username}' est déjà utilisé"
                )
            elif "email" in error_msg:
                print_error(
                    f"L'email '{email}' est déjà utilisé par un autre utilisateur"
                )
            else:
                print_error(
                    "Erreur: Un utilisateur avec ces informations existe déjà"
                )
        else:
            print_error(
                f"Erreur d'intégrité de la base de données: {error_msg}"
            )
        raise typer.Exit(code=1)

    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        raise typer.Exit(code=1)

    # Success message
    print_separator()
    print_success(f"Utilisateur {user.username} créé avec succès!")
    print_field("ID", str(user.id))
    print_field("Nom complet", f"{user.first_name} {user.last_name}")
    print_field("Email", user.email)
    print_field("Département", user.department.value)
    print_separator()


@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def create_contract(
    client_id: int = typer.Option(
        ..., prompt="ID du client", callback=validate_client_id_callback
    ),
    total_amount: str = typer.Option(
        ..., prompt="Montant total", callback=validate_amount_callback
    ),
    remaining_amount: str = typer.Option(
        ..., prompt="Montant restant", callback=validate_amount_callback
    ),
    is_signed: bool = typer.Option(False, prompt="Contrat signé ?")
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

    # Manually get services from container
    container = Container()
    contract_service = container.contract_service()
    client_service = container.client_service()

    # Show header at the beginning
    print_separator()
    print_header("Création d'un nouveau contrat")
    print_separator()

    # Business validation: check if client exists
    client = client_service.get_client(client_id)

    if not client:
        print_error(f"Client avec l'ID {client_id} n'existe pas")
        raise typer.Exit(code=1)

    # Convert amounts to Decimal
    try:
        total_decimal = Decimal(total_amount)
        remaining_decimal = Decimal(remaining_amount)
    except Exception:
        print_error("Erreur de conversion des montants")
        raise typer.Exit(code=1)

    # Business validation: validate contract amounts
    try:
        validate_contract_amounts(total_decimal, remaining_decimal)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(code=1)

    try:
        # Create contract via service
        contract = contract_service.create_contract(
            client_id=client_id,
            total_amount=total_decimal,
            remaining_amount=remaining_decimal,
            is_signed=is_signed,
        )

    except IntegrityError as e:
        error_msg = (
            str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()
        )

        if "foreign key" in error_msg:
            print_error(f"Le client (ID: {client_id}) n'existe pas")
        else:
            print_error(
                f"Erreur d'intégrité de la base de données: {error_msg}"
            )
        raise typer.Exit(code=1)

    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        raise typer.Exit(code=1)

    # Success message
    print_separator()
    print_success(
        f"Contrat créé avec succès pour le client {client.first_name} {client.last_name}!"
    )
    print_field("ID du contrat", str(contract.id))
    print_field(
        "Client",
        f"{client.first_name} {client.last_name} ({client.company_name})",
    )
    print_field(
        "Contact commercial",
        f"{client.sales_contact.first_name} {client.sales_contact.last_name} (ID: {client.sales_contact_id})"
    )
    print_field("Montant total", f"{contract.total_amount} €")
    print_field("Montant restant à payer", f"{contract.remaining_amount} €")
    print_field("Statut", "Signé ✓" if contract.is_signed else "Non signé ✗")
    print_field(
        "Date de création", contract.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )
    print_separator()


@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def create_event(
    name: str = typer.Option(
        ..., prompt="Nom de l'événement", callback=validate_event_name_callback
    ),
    contract_id: int = typer.Option(
        ..., prompt="ID du contrat", callback=validate_contract_id_callback
    ),
    event_start: str = typer.Option(
        ..., prompt="Date et heure de début (YYYY-MM-DD HH:MM)"
    ),
    event_end: str = typer.Option(
        ..., prompt="Date et heure de fin (YYYY-MM-DD HH:MM)"
    ),
    location: str = typer.Option(
        ..., prompt="Lieu", callback=validate_location_callback
    ),
    attendees: int = typer.Option(
        ...,
        prompt="Nombre de participants",
        callback=validate_attendees_callback,
    ),
    notes: str = typer.Option("", prompt="Notes (optionnel)"),
    support_contact_id: int = typer.Option(
        0, prompt="ID du contact support (0 si aucun)"
    )
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
    from datetime import datetime

    # Manually get services from container
    container = Container()
    event_service = container.event_service()
    contract_service = container.contract_service()
    user_service = container.user_service()

    # Show header at the beginning
    print_separator()
    print_header("Création d'un nouvel événement")
    print_separator()

    # Business validation: check if contract exists
    contract = contract_service.get_contract(contract_id)

    if not contract:
        print_error(f"Contrat avec l'ID {contract_id} n'existe pas")
        raise typer.Exit(code=1)

    # Parse datetime strings
    try:
        start_dt = datetime.strptime(event_start, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(event_end, "%Y-%m-%d %H:%M")
    except ValueError:
        print_error(
            "Format de date invalide. Utilisez le format: YYYY-MM-DD HH:MM"
        )
        raise typer.Exit(code=1)

    # Business validation: check if support contact exists and is from SUPPORT dept
    support_id = support_contact_id if support_contact_id > 0 else None
    if support_id:
        user = user_service.get_user(support_id)
        if not user:
            print_error(f"Utilisateur avec l'ID {support_id} n'existe pas")
            raise typer.Exit(code=1)
        if user.department != Department.SUPPORT:
            print_error(
                f"L'utilisateur {support_id} n'est pas du département SUPPORT"
            )
            raise typer.Exit(code=1)

    try:
        # Create event via service
        event = event_service.create_event(
            name=name,
            contract_id=contract_id,
            event_start=start_dt,
            event_end=end_dt,
            location=location,
            attendees=attendees,
            notes=notes if notes else None,
            support_contact_id=support_id,
        )

    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(code=1)

    except IntegrityError as e:
        error_msg = (
            str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()
        )

        if "foreign key" in error_msg:
            if "contract" in error_msg:
                print_error(f"Le contrat (ID: {contract_id}) n'existe pas")
            elif "support" in error_msg:
                print_error(
                    f"Le contact support (ID: {support_id}) n'existe pas"
                )
        else:
            print_error(
                f"Erreur d'intégrité de la base de données: {error_msg}"
            )
        raise typer.Exit(code=1)

    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        raise typer.Exit(code=1)

    # Success message
    print_separator()
    print_success(f"Événement '{event.name}' créé avec succès!")
    print_field("Event ID", str(event.id))
    print_field("Contract ID", str(contract.id))
    print_field(
        "Client name",
        f"{contract.client.first_name} {contract.client.last_name}",
    )
    print_field(
        "Client contact",
        f"{contract.client.email}\n{contract.client.phone}"
    )
    print_field("Event date start", format_event_datetime(event.event_start))
    print_field("Event date end", format_event_datetime(event.event_end))
    if event.support_contact:
        print_field(
            "Support contact",
            f"{event.support_contact.first_name} {event.support_contact.last_name} (ID: {event.support_contact_id})",
        )
    else:
        print_field("Support contact", "Non assigné")
    print_field("Location", event.location)
    print_field("Attendees", str(event.attendees))
    if event.notes:
        print_field("Notes", event.notes)
    print_separator()


@app.command()
@require_department(Department.GESTION)
def assign_support(
    event_id: int = typer.Option(
        ..., prompt="ID de l'événement", callback=validate_event_id_callback
    ),
    support_contact_id: int = typer.Option(
        ..., prompt="ID du contact support", callback=validate_user_id_callback
    )
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

    print_separator()
    print_header("Assignation d'un contact support")
    print_separator()

    # Vérifier que l'événement existe
    event = event_service.get_event(event_id)
    if not event:
        print_error(f"Événement avec l'ID {event_id} n'existe pas")
        raise typer.Exit(code=1)

    # Vérifier que l'utilisateur existe et est du département SUPPORT
    user = user_service.get_user(support_contact_id)
    if not user:
        print_error(f"Utilisateur avec l'ID {support_contact_id} n'existe pas")
        raise typer.Exit(code=1)

    if user.department != Department.SUPPORT:
        print_error(
            f"L'utilisateur {support_contact_id} n'est pas du département SUPPORT"
        )
        raise typer.Exit(code=1)

    # Assigner le contact support
    try:
        updated_event = event_service.assign_support_contact(
            event_id, support_contact_id
        )
    except Exception as e:
        print_error(f"Erreur lors de l'assignation: {e}")
        raise typer.Exit(code=1)

    # Success message
    print_separator()
    print_success(
        f"Contact support assigné avec succès à l'événement '{updated_event.name}'!"
    )
    print_field("Event ID", str(updated_event.id))
    print_field("Contract ID", str(updated_event.contract_id))
    print_field(
        "Client name",
        f"{updated_event.contract.client.first_name} {updated_event.contract.client.last_name}",
    )
    print_field(
        "Client contact",
        f"{updated_event.contract.client.email}\n{updated_event.contract.client.phone}"
    )
    print_field("Event date start", format_event_datetime(updated_event.event_start))
    print_field("Event date end", format_event_datetime(updated_event.event_end))
    print_field(
        "Support contact",
        f"{user.first_name} {user.last_name} (ID: {user.id})",
    )
    print_field("Location", updated_event.location)
    print_field("Attendees", str(updated_event.attendees))
    if updated_event.notes:
        print_field("Notes", updated_event.notes)
    print_separator()


@app.command()
@require_auth
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

    print_separator()
    print_header("Contrats non signés")
    print_separator()

    contracts = contract_service.get_unsigned_contracts()

    if not contracts:
        print_success("Aucun contrat non signé")
        return

    for contract in contracts:
        print_field("ID", str(contract.id))
        print_field(
            "Client",
            f"{contract.client.first_name} {contract.client.last_name} ({contract.client.company_name})",
        )
        print_field(
            "Contact commercial",
            f"{contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name} (ID: {contract.client.sales_contact_id})"
        )
        print_field("Montant total", f"{contract.total_amount} €")
        print_field("Montant restant à payer", f"{contract.remaining_amount} €")
        print_field(
            "Date de création", contract.created_at.strftime("%Y-%m-%d")
        )
        print_separator()

    print_success(f"Total: {len(contracts)} contrat(s) non signé(s)")


@app.command()
@require_auth
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

    print_separator()
    print_header("Contrats non soldés")
    print_separator()

    contracts = contract_service.get_unpaid_contracts()

    if not contracts:
        print_success("Aucun contrat non soldé")
        return

    for contract in contracts:
        print_field("ID", str(contract.id))
        print_field(
            "Client",
            f"{contract.client.first_name} {contract.client.last_name} ({contract.client.company_name})",
        )
        print_field(
            "Contact commercial",
            f"{contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name} (ID: {contract.client.sales_contact_id})"
        )
        print_field("Montant total", f"{contract.total_amount} €")
        print_field("Montant restant à payer", f"{contract.remaining_amount} €")
        print_field(
            "Statut", "Signé ✓" if contract.is_signed else "Non signé ✗"
        )
        print_field(
            "Date de création", contract.created_at.strftime("%Y-%m-%d")
        )
        print_separator()

    print_success(f"Total: {len(contracts)} contrat(s) non soldé(s)")


@app.command()
@require_auth
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

    print_separator()
    print_header("Événements sans contact support")
    print_separator()

    events = event_service.get_unassigned_events()

    if not events:
        print_success("Aucun événement sans contact support")
        return

    for event in events:
        print_field("Event ID", str(event.id))
        print_field("Contract ID", str(event.contract_id))
        print_field(
            "Client name",
            f"{event.contract.client.first_name} {event.contract.client.last_name}",
        )
        print_field(
            "Client contact",
            f"{event.contract.client.email}\n{event.contract.client.phone}"
        )
        print_field("Event date start", format_event_datetime(event.event_start))
        print_field("Event date end", format_event_datetime(event.event_end))
        print_field("Support contact", "Non assigné")
        print_field("Location", event.location)
        print_field("Attendees", str(event.attendees))
        if event.notes:
            print_field("Notes", event.notes)
        print_separator()

    print_success(f"Total: {len(events)} événement(s) sans contact support")


@app.command()
@require_department(Department.SUPPORT, Department.GESTION)
def filter_my_events(
    support_contact_id: int = typer.Option(
        ..., prompt="ID du contact support", callback=validate_user_id_callback
    )
):
    """
    Afficher les événements assignés à un contact support spécifique.

    Cette commande liste tous les événements assignés à un utilisateur SUPPORT.

    Args:
        support_contact_id: ID de l'utilisateur SUPPORT

    Returns:
        None. Affiche la liste des événements assignés.

    Raises:
        typer.Exit: En cas d'erreur (utilisateur inexistant ou non SUPPORT)

    Examples:
        epicevents filter-my-events
    """
    # Manually get services from container
    container = Container()
    event_service = container.event_service()
    user_service = container.user_service()

    print_separator()
    print_header("Mes événements")
    print_separator()

    # Vérifier que l'utilisateur existe et est du département SUPPORT
    user = user_service.get_user(support_contact_id)
    if not user:
        print_error(f"Utilisateur avec l'ID {support_contact_id} n'existe pas")
        raise typer.Exit(code=1)

    if user.department != Department.SUPPORT:
        print_error(
            f"L'utilisateur {support_contact_id} n'est pas du département SUPPORT"
        )
        raise typer.Exit(code=1)

    events = event_service.get_events_by_support_contact(support_contact_id)

    if not events:
        print_error(
            f"Aucun événement assigné à {user.first_name} {user.last_name}"
        )
        return

    for event in events:
        print_field("Event ID", str(event.id))
        print_field("Contract ID", str(event.contract_id))
        print_field(
            "Client name",
            f"{event.contract.client.first_name} {event.contract.client.last_name}",
        )
        print_field(
            "Client contact",
            f"{event.contract.client.email}\n{event.contract.client.phone}"
        )
        print_field("Event date start", format_event_datetime(event.event_start))
        print_field("Event date end", format_event_datetime(event.event_end))
        print_field(
            "Support contact",
            f"{user.first_name} {user.last_name} (ID: {user.id})"
        )
        print_field("Location", event.location)
        print_field("Attendees", str(event.attendees))
        if event.notes:
            print_field("Notes", event.notes)
        print_separator()

    print_success(
        f"Total: {len(events)} événement(s) assigné(s) à {user.first_name} {user.last_name}"
    )


@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def update_client(
    client_id: int = typer.Option(
        ..., prompt="ID du client", callback=validate_client_id_callback
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
    )
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
    # Manually get services from container
    container = Container()
    client_service = container.client_service()

    print_separator()
    print_header("Mise à jour d'un client")
    print_separator()

    # Vérifier que le client existe
    client = client_service.get_client(client_id)
    if not client:
        print_error(f"Client avec l'ID {client_id} n'existe pas")
        raise typer.Exit(code=1)

    # Nettoyer les champs vides
    first_name = first_name.strip() if first_name else None
    last_name = last_name.strip() if last_name else None
    email = email.strip() if email else None
    phone = phone.strip() if phone else None
    company_name = company_name.strip() if company_name else None

    # Validation des champs si fournis
    if first_name and len(first_name) < 2:
        print_error("Le prénom doit avoir au moins 2 caractères")
        raise typer.Exit(code=1)

    if last_name and len(last_name) < 2:
        print_error("Le nom doit avoir au moins 2 caractères")
        raise typer.Exit(code=1)

    try:
        # Mettre à jour le client
        updated_client = client_service.update_client(
            client_id=client_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company_name=company_name,
        )

    except IntegrityError as e:
        error_msg = (
            str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()
        )
        if "unique" in error_msg or "duplicate" in error_msg:
            print_error(f"Un client avec l'email '{email}' existe déjà")
        else:
            print_error(f"Erreur d'intégrité: {error_msg}")
        raise typer.Exit(code=1)

    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        raise typer.Exit(code=1)

    # Success message
    print_separator()
    print_success(f"Client mis à jour avec succès!")
    print_field("ID", str(updated_client.id))
    print_field(
        "Nom", f"{updated_client.first_name} {updated_client.last_name}"
    )
    print_field("Email", updated_client.email)
    print_field("Téléphone", updated_client.phone)
    print_field("Entreprise", updated_client.company_name)
    print_field(
        "Contact commercial",
        f"{updated_client.sales_contact.first_name} {updated_client.sales_contact.last_name} (ID: {updated_client.sales_contact_id})"
    )
    print_field(
        "Date de création", updated_client.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )
    print_field(
        "Dernière mise à jour", updated_client.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    )
    print_separator()


@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def update_contract(
    contract_id: int = typer.Option(
        ..., prompt="ID du contrat", callback=validate_contract_id_callback
    ),
    total_amount: str = typer.Option(
        None,
        prompt="Nouveau montant total (laisser vide pour ne pas modifier)",
    ),
    remaining_amount: str = typer.Option(
        None,
        prompt="Nouveau montant restant (laisser vide pour ne pas modifier)",
    ),
    is_signed: bool = typer.Option(None, prompt="Marquer comme signé ? (o/n)")
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

    # Manually get services from container
    container = Container()
    contract_service = container.contract_service()

    print_separator()
    print_header("Mise à jour d'un contrat")
    print_separator()

    # Vérifier que le contrat existe
    contract = contract_service.get_contract(contract_id)
    if not contract:
        print_error(f"Contrat avec l'ID {contract_id} n'existe pas")
        raise typer.Exit(code=1)

    # Nettoyer et convertir les montants
    total_decimal = None
    remaining_decimal = None

    if total_amount:
        total_amount = total_amount.strip()
        try:
            total_decimal = Decimal(total_amount)
        except Exception:
            print_error("Montant total invalide")
            raise typer.Exit(code=1)

    if remaining_amount:
        remaining_amount = remaining_amount.strip()
        try:
            remaining_decimal = Decimal(remaining_amount)
        except Exception:
            print_error("Montant restant invalide")
            raise typer.Exit(code=1)

    # Validation des montants
    if total_decimal is not None and total_decimal < 0:
        print_error("Le montant total doit être positif")
        raise typer.Exit(code=1)

    if remaining_decimal is not None and remaining_decimal < 0:
        print_error("Le montant restant doit être positif")
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
        print_error("Le montant restant ne peut pas dépasser le montant total")
        raise typer.Exit(code=1)

    try:
        updated_contract = contract_service.update_contract(contract)
    except Exception as e:
        print_error(f"Erreur lors de la mise à jour: {e}")
        raise typer.Exit(code=1)

    # Success message
    print_separator()
    print_success("Contrat mis à jour avec succès!")
    print_field("ID", str(updated_contract.id))
    print_field(
        "Client",
        f"{updated_contract.client.first_name} {updated_contract.client.last_name} ({updated_contract.client.company_name})",
    )
    print_field(
        "Contact commercial",
        f"{updated_contract.client.sales_contact.first_name} {updated_contract.client.sales_contact.last_name} (ID: {updated_contract.client.sales_contact_id})"
    )
    print_field("Montant total", f"{updated_contract.total_amount} €")
    print_field("Montant restant à payer", f"{updated_contract.remaining_amount} €")
    print_field(
        "Statut", "Signé ✓" if updated_contract.is_signed else "Non signé ✗"
    )
    print_field(
        "Date de création", updated_contract.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )
    print_field(
        "Dernière mise à jour", updated_contract.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    )
    print_separator()
