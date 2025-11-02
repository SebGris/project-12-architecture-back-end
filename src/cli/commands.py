import typer
from sqlalchemy.exc import IntegrityError, OperationalError

from src.cli.console import (
    print_error,
    print_field,
    print_header,
    print_separator,
    print_success,
)
from src.cli.validators import (
    validate_amount_callback,
    validate_client_id_callback,
    validate_company_name_callback,
    validate_department_callback,
    validate_email_callback,
    validate_first_name_callback,
    validate_last_name_callback,
    validate_password_callback,
    validate_phone_callback,
    validate_sales_contact_id_callback,
    validate_username_callback,
)
from src.models.user import Department

app = typer.Typer()

# Global container - will be set by main.py
_container = None  # todo: implement container ? chercher


def set_container(container):
    """Set the dependency injection container."""
    global _container
    _container = container


@app.command()
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
        ...,
        prompt="ID du contact commercial",
        callback=validate_sales_contact_id_callback,
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
        sales_contact_id: ID d'un utilisateur du département COMMERCIAL

    Returns:
        None. Affiche un message de succès avec les détails du client créé.

    Raises:
        typer.Exit: En cas d'erreur (données invalides, contact inexistant, etc.)

    Examples:
        epicevents create-client
        # Suit les prompts interactifs pour saisir les informations
    """
    # Show header at the beginning
    print_separator()
    print_header("Création d'un nouveau client")
    print_separator()

    # Get services from container
    client_service = _container.client_service()
    user_service = _container.user_service()

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
        error_msg = str(e.orig).lower() if hasattr(e, 'orig') else str(e).lower()

        if 'unique' in error_msg or 'duplicate' in error_msg:
            if 'email' in error_msg:
                print_error(
                    f"Un client avec l'email '{email}' existe déjà dans le système"
                )
            else:
                print_error(
                    "Erreur: Un client avec ces informations existe déjà"
                )
        elif 'foreign key' in error_msg:
            print_error(
                f"Le contact commercial (ID: {sales_contact_id}) n'existe pas"
            )
        else:
            print_error(
                f"Erreur d'intégrité de la base de données: {error_msg}"
            )
        raise typer.Exit(code=1)

    except OperationalError:
        print_error("Erreur de connexion à la base de données")
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
    print_field("Entreprise", client.company_name)
    print_separator()


@app.command()
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
    # Show header at the beginning
    print_separator()
    print_header("Création d'un nouvel utilisateur")
    print_separator()

    # Get service from container
    user_service = _container.user_service()

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
        error_msg = str(e.orig).lower() if hasattr(e, 'orig') else str(e).lower()

        if 'unique' in error_msg or 'duplicate' in error_msg:
            if 'username' in error_msg:
                print_error(
                    f"Le nom d'utilisateur '{username}' est déjà utilisé"
                )
            elif 'email' in error_msg:
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
    is_signed: bool = typer.Option(
        False, prompt="Contrat signé ?"
    ),
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

    # Show header at the beginning
    print_separator()
    print_header("Création d'un nouveau contrat")
    print_separator()

    # Get services from container
    contract_service = _container.contract_service()
    client_service = _container.client_service()

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

    # Business validation: remaining amount must not exceed total amount
    if remaining_decimal > total_decimal:
        print_error(
            f"Le montant restant ({remaining_decimal}) ne peut pas dépasser le montant total ({total_decimal})"
        )
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
        error_msg = str(e.orig).lower() if hasattr(e, 'orig') else str(e).lower()

        if 'foreign key' in error_msg:
            print_error(f"Le client (ID: {client_id}) n'existe pas")
        else:
            print_error(
                f"Erreur d'intégrité de la base de données: {error_msg}"
            )
        raise typer.Exit(code=1)

    except OperationalError:
        print_error("Erreur de connexion à la base de données")
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
    print_field("Client", f"{client.first_name} {client.last_name} ({client.company_name})")
    print_field("Montant total", f"{contract.total_amount}")
    print_field("Montant restant", f"{contract.remaining_amount}")
    print_field("Statut", "Signé" if contract.is_signed else "Non signé")
    print_separator()
