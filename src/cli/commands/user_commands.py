import typer

from src.cli import console
from src.cli import validators
from src.cli import constants as c
from src.models.user import Department
from src.containers import Container
from src.cli.permissions import require_department

app = typer.Typer()


@app.command()
@require_department(Department.GESTION)
def create_user(
    username: str = typer.Option(
        ...,
        prompt=c.LABEL_USERNAME,
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
        prompt=c.PROMPT_TELEPHONE,
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
    """Create a new user in the CRM system.

    This command registers a new user with their personal and professional
    information. The password is automatically hashed before being stored
    in the database.

    Args:
        username: Unique username (4-50 characters, letters/digits/_/-)
        first_name: User's first name (minimum 2 characters)
        last_name: User's last name (minimum 2 characters)
        email: Valid and unique email address
        phone: Phone number (minimum 10 digits)
        password: Password (minimum 8 characters, will be hashed)
        department_choice: Department choice (1=COMMERCIAL, 2=GESTION, 3=SUPPORT)

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
    console.print_command_header("Création d'un nouvel utilisateur")

    # Convert department choice (int) to Department enum
    departments = list(Department)
    department = departments[department_choice - 1]

    # Vérifications préventives: username et email déjà utilisés
    if user_service.username_exists(username):
        console.print_error(
            f"Le nom d'utilisateur '{username}' est déjà utilisé"
        )
        raise typer.Exit(code=1)

    if user_service.email_exists(email):
        console.print_error(
            f"L'email '{email}' est déjà utilisé par un autre utilisateur"
        )
        raise typer.Exit(code=1)

    try:
        user = user_service.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password=password,
            department=department,
        )

    except Exception as e:
        console.print_error(c.ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success(f"Utilisateur {user.username} créé avec succès!")
    console.print_field(c.LABEL_ID, str(user.id))
    console.print_field("Nom complet", f"{user.first_name} {user.last_name}")
    console.print_field(c.LABEL_EMAIL, user.email)
    console.print_field(c.LABEL_DEPARTMENT, user.department.value)
    console.print_separator()


@app.command()
@require_department(Department.GESTION)
def update_user(
    user_id: int = typer.Option(
        ...,
        prompt="ID de l'utilisateur",
        callback=validators.validate_user_id_callback,
    ),
    username: str = typer.Option(
        "", prompt="Nouveau nom d'utilisateur (laisser vide pour ne pas modifier)"
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
    department_choice: int = typer.Option(
        0,
        prompt=f"Nouveau département (1={Department.COMMERCIAL.value}, 2={Department.GESTION.value}, 3={Department.SUPPORT.value}, 0=pas de changement)",
    ),
):
    """Update user information.

    This command modifies information for an existing user.
    Fields left empty will not be modified.

    Args:
        user_id: ID of the user to modify
        username: New username (optional)
        first_name: New first name (optional)
        last_name: New last name (optional)
        email: New email (optional)
        phone: New phone number (optional)
        department_choice: New department (optional)

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

    console.print_command_header("Mise à jour d'un utilisateur")

    # Vérifier que l'utilisateur existe
    user = user_service.get_user(user_id)
    if not user:
        console.print_error(f"Utilisateur avec l'ID {user_id} n'existe pas")
        raise typer.Exit(code=1)

    # Nettoyer les champs vides
    username = username.strip() if username else None
    first_name = first_name.strip() if first_name else None
    last_name = last_name.strip() if last_name else None
    email = email.strip() if email else None
    phone = phone.strip() if phone else None

    # Convert department choice if provided
    department = None
    if department_choice > 0:
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

    # Vérifications préventives: username et email déjà utilisés (en excluant l'utilisateur actuel)
    if username and user_service.username_exists(username, exclude_id=user_id):
        console.print_error(
            f"Le nom d'utilisateur '{username}' est déjà utilisé"
        )
        raise typer.Exit(code=1)

    if email and user_service.email_exists(email, exclude_id=user_id):
        console.print_error(f"L'email '{email}' est déjà utilisé")
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

    except Exception as e:
        console.print_error(c.ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success("Utilisateur mis à jour avec succès!")
    console.print_field(c.LABEL_ID, str(updated_user.id))
    console.print_field(c.LABEL_USERNAME, updated_user.username)
    console.print_field(
        "Nom complet", f"{updated_user.first_name} {updated_user.last_name}"
    )
    console.print_field(c.LABEL_EMAIL, updated_user.email)
    console.print_field(c.LABEL_PHONE, updated_user.phone)
    console.print_field(c.LABEL_DEPARTMENT, updated_user.department.value)
    console.print_separator()


@app.command()
@require_department(Department.GESTION)
def delete_user(
    user_id: int = typer.Option(
        ...,
        prompt="ID de l'utilisateur à supprimer",
        callback=validators.validate_user_id_callback,
    ),
):
    """Delete a user from the CRM system.

    This command permanently deletes a user from the database.
    WARNING: This action is irreversible.

    Args:
        user_id: ID of the user to delete

    Returns:
        None. Displays confirmation message.

    Raises:
        typer.Exit: On error (non-existent user, cancellation, etc.)

    Examples:
        epicevents delete-user
    """
    # Manually get services from container
    container = Container()
    user_service = container.user_service()

    console.print_command_header("Suppression d'un utilisateur")

    # Vérifier que l'utilisateur existe
    user = user_service.get_user(user_id)
    if not user:
        console.print_error(f"Utilisateur avec l'ID {user_id} n'existe pas")
        raise typer.Exit(code=1)

    # Afficher les informations de l'utilisateur avant suppression
    console.print_field(c.LABEL_ID, str(user.id))
    console.print_field(c.LABEL_USERNAME, user.username)
    console.print_field("Nom complet", f"{user.first_name} {user.last_name}")
    console.print_field(c.LABEL_EMAIL, user.email)
    console.print_field(c.LABEL_DEPARTMENT, user.department.value)
    console.print_separator()

    # Demander confirmation
    confirm = typer.confirm(
        "Êtes-vous sûr de vouloir supprimer cet utilisateur ?",
        default=False
    )

    if not confirm:
        console.print_error("Suppression annulée.")
        raise typer.Exit(code=1)

    try:
        success = user_service.delete_user(user_id)
        if not success:
            console.print_error("Erreur lors de la suppression de l'utilisateur")
            raise typer.Exit(code=1)

    except Exception as e:
        console.print_error(c.ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success(
        f"Utilisateur {user.username} (ID: {user_id}) supprimé avec succès!"
    )
    console.print_separator()
