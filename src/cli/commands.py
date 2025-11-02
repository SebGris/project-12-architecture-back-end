import re

import typer
from sqlalchemy.exc import IntegrityError, OperationalError

from src.models.user import Department

app = typer.Typer()

# Global container - will be set by main.py
_container = None  # todo: implement container ? chercher


def set_container(container):
    """Set the dependency injection container."""
    global _container
    _container = container


# Regex patterns for validation
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
# Pattern pour numéros de téléphone: accepte chiffres, espaces, tirets, +, parenthèses et points
# Permet des formats comme: "01 23 45 67 89", "+33 1 23 45 67 89", "(01) 23.45.67.89"
PHONE_PATTERN = re.compile(r"^[\d\s\-\+\(\)\.]+$")
# Pattern pour nom d'utilisateur: lettres (a-z, A-Z), chiffres (0-9), underscore (_) et tiret (-)
# Longueur: entre 4 et 50 caractères. Ex: "john_doe", "user-123", "Admin_2024"
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{4,50}$")


# Callback validators for typer.Option
def validate_first_name_callback(value: str) -> str:
    """Validate and clean first name."""
    cleaned = value.strip()
    if len(cleaned) < 2:
        raise typer.BadParameter("Le prénom doit avoir au moins 2 caractères")
    return cleaned


def validate_last_name_callback(value: str) -> str:
    """Validate and clean last name."""
    cleaned = value.strip()
    if len(cleaned) < 2:
        raise typer.BadParameter("Le nom doit avoir au moins 2 caractères")
    return cleaned


def validate_email_callback(value: str) -> str:
    """Validate and clean email."""
    cleaned = value.strip().lower()
    if not EMAIL_PATTERN.match(cleaned):
        raise typer.BadParameter(f"Email invalide: {value}")
    return cleaned


def validate_phone_callback(value: str) -> str:
    """Validate and clean phone number."""
    cleaned = value.strip()
    if not PHONE_PATTERN.match(cleaned):
        raise typer.BadParameter(f"Format de téléphone invalide: {value}")
    # Extrait uniquement les chiffres en supprimant tous les caractères non-numériques
    # Ex: "+33 1 23 45 67 89" devient "33123456789"
    digits = re.sub(r"[^0-9]", "", cleaned)
    if len(digits) < 10:
        raise typer.BadParameter(
            "Le téléphone doit avoir au moins 10 chiffres"
        )
    return cleaned


def validate_company_name_callback(value: str) -> str:
    """Validate and clean company name."""
    cleaned = value.strip()
    if not cleaned:
        raise typer.BadParameter("Le nom de l'entreprise est requis")  # todo
    return cleaned


def validate_sales_contact_id_callback(value: int) -> int:
    """Validate sales contact ID."""
    if value <= 0:
        raise typer.BadParameter("L'ID du contact doit être positif")
    return value


def validate_username_callback(value: str) -> str:
    """Validate and clean username."""
    cleaned = value.strip()
    if not USERNAME_PATTERN.match(cleaned):
        raise typer.BadParameter(
            "Username invalide (4-50 caractères, lettres/chiffres/_/-)"
        )
    return cleaned


def validate_password_callback(value: str) -> str:
    """Validate password."""
    if len(value) < 8:
        raise typer.BadParameter(
            "Le mot de passe doit avoir au moins 8 caractères"
        )
    return value


def validate_department_callback(value: int) -> Department:
    """Validate department selection."""
    departments = list(Department)
    if value < 1 or value > len(departments):
        raise typer.BadParameter(
            f"Choix invalide. Veuillez choisir entre 1 et {len(departments)}"
        )
    return departments[value - 1]


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
        callback=validate_company_name_callback,  # todo
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
    typer.echo(
        "\n=== Création d'un nouveau client ===\n"
    )  # todo voir si couleur

    # Get services from container
    client_service = _container.client_service()
    user_service = _container.user_service()

    try:
        # Business validation: check if sales contact exists and is from COMMERCIAL dept
        user = user_service.get_user(sales_contact_id)  # err si inexistant

        if not user:  # hors try
            typer.echo(
                f"[ERREUR] Utilisateur avec l'ID {sales_contact_id} n'existe pas"
            )
            raise typer.Exit(code=1)

        if user.department != Department.COMMERCIAL:
            typer.echo(
                f"[ERREUR] L'utilisateur {sales_contact_id} n'est pas du département COMMERCIAL"
            )
            raise typer.Exit(code=1)

        # Create client via service
        client = client_service.create_client(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company_name=company_name,
            sales_contact_id=sales_contact_id,
        )

    except IntegrityError:
        typer.echo(
            "[ERREUR] Erreur d'intégrité: Données en double ou contrainte violée"  # todo explicite
        )
        raise typer.Exit(code=1)

    except Exception as e:
        typer.echo(f"[ERREUR] Erreur inattendue: {e}")
        raise typer.Exit(code=1)

    # Success message
    typer.echo(
        f"\n[SUCCÈS] Client {client.first_name} {client.last_name} créé avec succès!"
    )
    typer.echo(f"  ID: {client.id}")
    typer.echo(f"  Email: {client.email}")
    typer.echo(f"  Entreprise: {client.company_name}")


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
        prompt=f"\nDépartements disponibles:\n1. {Department.COMMERCIAL.value}\n2. {Department.SUPPORT.value}\n3. {Department.GESTION.value}\n\nChoisir un département (numéro)",
        callback=validate_department_callback,
    ),
):
    """Créer un nouvel utilisateur."""
    typer.echo("\n=== Création d'un nouvel utilisateur ===\n")

    # Get service from container
    user_service = _container.user_service()

    try:
        # Create user via service
        user = user_service.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password=password,
            department=department_choice,
        )

    except IntegrityError:
        typer.echo(
            "[ERREUR] Erreur d'intégrité: Données en double ou contrainte violée"
        )
        raise typer.Exit(code=1)

    except OperationalError:
        typer.echo("[ERREUR] Erreur de connexion à la base de données")
        raise typer.Exit(code=1)

    except KeyboardInterrupt:
        typer.echo("\n[ANNULÉ] Opération annulée")
        raise typer.Exit(code=1)

    except Exception as e:
        typer.echo(f"[ERREUR] Erreur inattendue: {e}")
        raise typer.Exit(code=1)

    # Success message
    typer.echo(f"\n[SUCCÈS] Utilisateur {user.username} créé avec succès!")
    typer.echo(f"  ID: {user.id}")
    typer.echo(f"  Nom complet: {user.first_name} {user.last_name}")
    typer.echo(f"  Email: {user.email}")
    typer.echo(f"  Département: {user.department.value}")
