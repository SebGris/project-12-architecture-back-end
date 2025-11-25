import typer

from src.cli import console
from src.cli import validators
from src.cli import constants as c
from src.models.user import Department
from src.containers import Container
from src.cli.permissions import require_department

app = typer.Typer()


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
        prompt=c.PROMPT_TELEPHONE,
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
    """Create a new client in the CRM system.

    This command registers a new client with their contact information
    and associates them with a sales contact from the COMMERCIAL department.

    Args:
        first_name: Client's first name (minimum 2 characters)
        last_name: Client's last name (minimum 2 characters)
        email: Valid client email address
        phone: Phone number (minimum 10 digits)
        company_name: Client's company name
        sales_contact_id: ID of a COMMERCIAL department user (auto-assigned if empty for COMMERCIAL)

    Returns:
        None. Displays success message with created client details.

    Raises:
        typer.Exit: On error (invalid data, non-existent contact, etc.)

    Examples:
        epicevents create-client
        # Follow interactive prompts to enter information
    """
    # Manually get services from container
    container = Container()
    client_service = container.client_service()
    user_service = container.user_service()
    auth_service = container.auth_service()

    # Show header at the beginning
    console.print_separator()
    console.print_header("Création d'un nouveau client")
    console.print_separator()

    # Get current user from auth_service (decorator already verified authentication)
    current_user = auth_service.get_current_user()

    # Auto-assign for COMMERCIAL users if no sales_contact_id provided
    if sales_contact_id == 0:
        if current_user.department == Department.COMMERCIAL:
            sales_contact_id = current_user.id
            console.print_field(
                c.LABEL_CONTACT_COMMERCIAL,
                f"Auto-assigné à {current_user.username}",
            )
        else:
            console.print_error(
                "Vous devez spécifier un ID de contact commercial"
            )
            raise typer.Exit(code=1)

    # Business validation: check if sales contact exists and is from COMMERCIAL dept
    user = user_service.get_user(sales_contact_id)

    if not user:
        console.print_error(
            f"Utilisateur avec l'ID {sales_contact_id} n'existe pas"
        )
        raise typer.Exit(code=1)

    try:
        validators.validate_user_is_commercial(user)
    except ValueError as e:
        console.print_error(str(e))
        raise typer.Exit(code=1)

    # Vérification préventive: email déjà utilisé
    if client_service.email_exists(email):
        console.print_error(
            f"Un client avec l'email '{email}' existe déjà dans le système"
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

    except Exception as e:
        console.print_error(c.ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success(
        f"Client {client.first_name} {client.last_name} créé avec succès!"
    )
    console.print_field(c.LABEL_ID, str(client.id))
    console.print_field(c.LABEL_EMAIL, client.email)
    console.print_field(c.LABEL_PHONE, client.phone)
    console.print_field("Entreprise", client.company_name)
    console.print_field(
        c.LABEL_CONTACT_COMMERCIAL,
        f"{client.sales_contact.first_name} {client.sales_contact.last_name} (ID: {client.sales_contact_id})",
    )
    console.print_field(
        c.LABEL_DATE_CREATION, client.created_at.strftime(c.FORMAT_DATETIME)
    )
    console.print_separator()


@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def update_client(
    client_id: int = typer.Option(
        ...,
        prompt="ID du client",
        callback=validators.validate_client_id_callback,
    ),
    first_name: str = typer.Option(
        "", prompt="Nouveau prénom (laisser vide pour ne pas modifier)"
    ),
    last_name: str = typer.Option(
        "", prompt="Nouveau nom (laisser vide pour ne pas modifier)"
    ),
    email: str = typer.Option(
        "", prompt="Nouvel email (laisser vide pour ne pas modifier)"
    ),
    phone: str = typer.Option(
        "", prompt="Nouveau téléphone (laisser vide pour ne pas modifier)"
    ),
    company_name: str = typer.Option(
        "",
        prompt="Nouveau nom d'entreprise (laisser vide pour ne pas modifier)",
    ),
):
    """Update client information.

    This command modifies information for an existing client.
    Fields left empty will not be modified.

    Args:
        client_id: ID of the client to modify
        first_name: New first name (optional)
        last_name: New last name (optional)
        email: New email (optional)
        phone: New phone number (optional)
        company_name: New company name (optional)

    Returns:
        None. Displays success message with details.

    Raises:
        typer.Exit: On error (non-existent client, invalid data, etc.)

    Examples:
        epicevents update-client
    """
    # Manually get services from container
    container = Container()
    client_service = container.client_service()
    auth_service = container.auth_service()

    console.print_separator()
    console.print_header("Mise à jour d'un client")
    console.print_separator()

    # Get current user for permission check
    current_user = auth_service.get_current_user()

    # Vérifier que le client existe
    client = client_service.get_client(client_id)
    if not client:
        console.print_error(f"Client avec l'ID {client_id} n'existe pas")
        raise typer.Exit(code=1)

    # Permission check: COMMERCIAL can only update their own clients
    if current_user.department == Department.COMMERCIAL:
        if client.sales_contact_id != current_user.id:
            console.print_error(
                "Vous ne pouvez modifier que vos propres clients"
            )
            console.print_error(
                f"Ce client est assigné à {client.sales_contact.first_name} {client.sales_contact.last_name}"
            )
            raise typer.Exit(code=1)

    # Nettoyer les champs vides
    first_name = first_name.strip() if first_name else None
    last_name = last_name.strip() if last_name else None
    email = email.strip() if email else None
    phone = phone.strip() if phone else None
    company_name = company_name.strip() if company_name else None

    # Validation des champs si fournis
    if first_name and len(first_name) < 2:
        console.print_error("Le prénom doit avoir au moins 2 caractères")
        raise typer.Exit(code=1)

    if last_name and len(last_name) < 2:
        console.print_error("Le nom doit avoir au moins 2 caractères")
        raise typer.Exit(code=1)

    # Vérification préventive: email déjà utilisé (en excluant le client actuel)
    if email and client_service.email_exists(email, exclude_id=client_id):
        console.print_error(f"Un client avec l'email '{email}' existe déjà")
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

    except Exception as e:
        console.print_error(c.ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success("Client mis à jour avec succès!")
    console.print_field(c.LABEL_ID, str(updated_client.id))
    console.print_field(
        "Nom", f"{updated_client.first_name} {updated_client.last_name}"
    )
    console.print_field(c.LABEL_EMAIL, updated_client.email)
    console.print_field(c.LABEL_PHONE, updated_client.phone)
    console.print_field("Entreprise", updated_client.company_name)
    console.print_field(
        c.LABEL_CONTACT_COMMERCIAL,
        f"{updated_client.sales_contact.first_name} {updated_client.sales_contact.last_name} (ID: {updated_client.sales_contact_id})",
    )
    console.print_field(
        c.LABEL_DATE_CREATION,
        updated_client.created_at.strftime(c.FORMAT_DATETIME),
    )
    console.print_field(
        "Dernière mise à jour",
        updated_client.updated_at.strftime(c.FORMAT_DATETIME),
    )
    console.print_separator()
