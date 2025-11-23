import typer
from sqlalchemy.exc import IntegrityError

from src.cli import console
from src.cli import validators
from src.cli.constants import (
    LABEL_USERNAME,
    LABEL_DEPARTMENT,
    LABEL_ID,
    LABEL_EMAIL,
    LABEL_PHONE,
    ERROR_UNEXPECTED,
)
from src.cli.error_handlers import handle_integrity_error
from src.models.user import Department
from src.containers import Container
from src.cli.permissions import require_department

app = typer.Typer()


@app.command()
@require_department(Department.GESTION)
def create_user():
    """Create a new user in the CRM system.

    This command registers a new user with their personal and professional
    information. The password is automatically hashed before being stored
    in the database.

    Returns:
        None. Displays success message with created user details.

    Raises:
        typer.Exit: On error (username/email already in use, invalid data, etc.)

    Examples:
        epicevents create-user
        # Follow interactive prompts to enter information
    """
    # Manually get services from container
    container = Container()
    user_service = container.user_service()

    # Show header at the beginning
    console.print_separator()
    console.print_header("Création d'un nouvel utilisateur")
    console.print_separator()

    # Prompt and validate each field
    while True:
        try:
            username = validators.validate_username_callback(
                typer.prompt(LABEL_USERNAME)
            )
            break
        except typer.BadParameter as e:
            console.print_error(str(e))

    while True:
        try:
            first_name = validators.validate_first_name_callback(
                typer.prompt("Prénom")
            )
            break
        except typer.BadParameter as e:
            console.print_error(str(e))

    while True:
        try:
            last_name = validators.validate_last_name_callback(
                typer.prompt("Nom")
            )
            break
        except typer.BadParameter as e:
            console.print_error(str(e))

    while True:
        try:
            email = validators.validate_email_callback(
                typer.prompt("Email")
            )
            break
        except typer.BadParameter as e:
            console.print_error(str(e))

    while True:
        try:
            phone = validators.validate_phone_callback(
                typer.prompt("Téléphone")
            )
            break
        except typer.BadParameter as e:
            console.print_error(str(e))

    while True:
        try:
            password = validators.validate_password_callback(
                typer.prompt("Mot de passe", hide_input=True)
            )
            break
        except typer.BadParameter as e:
            console.print_error(str(e))

    # Department selection
    console.print_separator()
    console.print_field("Départements disponibles", "")
    console.print_field("1", Department.COMMERCIAL.value)
    console.print_field("2", Department.GESTION.value)
    console.print_field("3", Department.SUPPORT.value)
    console.print_separator()

    while True:
        try:
            department_choice = validators.validate_department_callback(
                typer.prompt("Choisir un département (numéro)", type=int)
            )
            break
        except typer.BadParameter as e:
            console.print_error(str(e))

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
        handle_integrity_error(
            e,
            {
                "username": f"Le nom d'utilisateur '{username}' est déjà utilisé",
                "email": f"L'email '{email}' est déjà utilisé par un autre utilisateur",
            },
        )
        raise typer.Exit(code=1)

    except Exception as e:
        console.print_error(ERROR_UNEXPECTED.format(e=e))
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
@require_department(Department.GESTION)
def update_user():
    """Update user information.

    This command modifies information for an existing user.
    Fields left empty will not be modified.

    Returns:
        None. Displays success message with details.

    Raises:
        typer.Exit: On error (non-existent user, invalid data, etc.)

    Examples:
        epicevents update-user
    """
    # Manually get services from container
    container = Container()
    user_service = container.user_service()

    console.print_separator()
    console.print_header("Mise à jour d'un utilisateur")
    console.print_separator()

    # Prompt for user ID with validation
    user_id = typer.prompt("ID de l'utilisateur", type=int)
    if user_id <= 0:
        console.print_error("L'ID doit être un nombre positif")
        raise typer.Exit(code=1)

    # Vérifier que l'utilisateur existe
    user = user_service.get_user(user_id)
    if not user:
        console.print_error(f"Utilisateur avec l'ID {user_id} n'existe pas")
        raise typer.Exit(code=1)

    # Prompt for optional fields - accept empty string as "no change"
    username = typer.prompt(
        "Nouveau nom d'utilisateur (laisser vide pour ne pas modifier)",
        default="",
        show_default=False
    ).strip() or None

    first_name = typer.prompt(
        "Nouveau prénom (laisser vide pour ne pas modifier)",
        default="",
        show_default=False
    ).strip() or None

    last_name = typer.prompt(
        "Nouveau nom (laisser vide pour ne pas modifier)",
        default="",
        show_default=False
    ).strip() or None

    email = typer.prompt(
        "Nouvel email (laisser vide pour ne pas modifier)",
        default="",
        show_default=False
    ).strip() or None

    phone = typer.prompt(
        "Nouveau téléphone (laisser vide pour ne pas modifier)",
        default="",
        show_default=False
    ).strip() or None

    # Prompt for department choice
    department_choice = typer.prompt(
        f"Nouveau département (1={Department.COMMERCIAL.value}, 2={Department.GESTION.value}, 3={Department.SUPPORT.value}, 0=pas de changement)",
        type=int,
        default=0
    )

    # Convert department choice if provided
    department = None
    if department_choice > 0:
        if department_choice > 3:
            console.print_error("Choix invalide. Doit être entre 0 et 3")
            raise typer.Exit(code=1)
        departments = list(Department)
        department = departments[department_choice - 1]

    # Validation des champs si fournis
    if username and len(username) < 4:
        console.print_error("Le nom d'utilisateur doit avoir au moins 4 caractères")
        raise typer.Exit(code=1)

    if first_name and len(first_name) < 2:
        console.print_error("Le prénom doit avoir au moins 2 caractères")
        raise typer.Exit(code=1)

    if last_name and len(last_name) < 2:
        console.print_error("Le nom doit avoir au moins 2 caractères")
        raise typer.Exit(code=1)

    try:
        # Mettre à jour l'utilisateur
        updated_user = user_service.update_user(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            department=department,
        )

    except IntegrityError as e:
        error_msg = (
            str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()
        )
        if "unique" in error_msg or "duplicate" in error_msg:
            if "username" in error_msg:
                console.print_error(
                    f"Le nom d'utilisateur '{username}' est déjà utilisé"
                )
            elif "email" in error_msg:
                console.print_error(f"L'email '{email}' est déjà utilisé")
            else:
                console.print_error(
                    "Un utilisateur avec ces informations existe déjà"
                )
        else:
            console.print_error(f"Erreur d'intégrité: {error_msg}")
        raise typer.Exit(code=1)

    except Exception as e:
        console.print_error(ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success("Utilisateur mis à jour avec succès!")
    console.print_field(LABEL_ID, str(updated_user.id))
    console.print_field(LABEL_USERNAME, updated_user.username)
    console.print_field(
        "Nom complet", f"{updated_user.first_name} {updated_user.last_name}"
    )
    console.print_field(LABEL_EMAIL, updated_user.email)
    console.print_field(LABEL_PHONE, updated_user.phone)
    console.print_field(LABEL_DEPARTMENT, updated_user.department.value)
    console.print_separator()


@app.command()
@require_department(Department.GESTION)
def delete_user(
    user_id: int = typer.Option(
        ...,
        prompt="ID de l'utilisateur à supprimer",
        callback=validators.validate_user_id_callback,
    ),
    confirm: bool = typer.Option(
        False, prompt="Êtes-vous sûr de vouloir supprimer cet utilisateur ? (oui/non)"
    ),
):
    """Delete a user from the CRM system.

    This command permanently deletes a user from the database.
    WARNING: This action is irreversible.

    Args:
        user_id: ID of the user to delete
        confirm: Deletion confirmation

    Returns:
        None. Displays confirmation message.

    Raises:
        typer.Exit: On error (non-existent user, missing confirmation, etc.)

    Examples:
        epicevents delete-user --user-id 5 --confirm
    """
    # Manually get services from container
    container = Container()
    user_service = container.user_service()

    console.print_separator()
    console.print_header("Suppression d'un utilisateur")
    console.print_separator()

    # Vérifier que l'utilisateur existe
    user = user_service.get_user(user_id)
    if not user:
        console.print_error(f"Utilisateur avec l'ID {user_id} n'existe pas")
        raise typer.Exit(code=1)

    # Afficher les informations de l'utilisateur avant suppression
    console.print_field(LABEL_ID, str(user.id))
    console.print_field(LABEL_USERNAME, user.username)
    console.print_field("Nom complet", f"{user.first_name} {user.last_name}")
    console.print_field(LABEL_EMAIL, user.email)
    console.print_field(LABEL_DEPARTMENT, user.department.value)
    console.print_separator()

    # Demander confirmation
    if not confirm:
        console.print_error(
            "Suppression annulée. Utilisez --confirm True pour confirmer la suppression."
        )
        raise typer.Exit(code=1)

    # Delete user
    try:
        success = user_service.delete_user(user_id)
        if not success:
            console.print_error("Erreur lors de la suppression de l'utilisateur")
            raise typer.Exit(code=1)

    except Exception as e:
        console.print_error(ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success(
        f"Utilisateur {user.username} (ID: {user_id}) supprimé avec succès!"
    )
    console.print_separator()
