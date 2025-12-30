import typer

from src.cli import console
from src.cli import constants as c
from src.containers import Container

app = typer.Typer()


@app.command()
def login(
    username: str = typer.Option(..., prompt=c.LABEL_USERNAME),
    password: str = typer.Option(..., prompt="Mot de passe", hide_input=True),
):
    """Login to the Epic Events CRM application.

    This command authenticates with a username and password.
    A JWT token is generated and stored locally for persistent authentication.

    Args:
        username: Username
        password: Password (hidden during input)

    Returns:
        None. Displays success or error message.

    Examples:
        epicevents login
    """
    # Manually get auth_service from container
    container = Container()
    auth_service = container.auth_service()

    console.print_command_header("Authentification")

    # Authenticate user
    user = auth_service.authenticate(username, password)

    if not user:
        console.print_error("Nom d'utilisateur ou mot de passe incorrect")
        raise typer.Exit(code=1)

    # Generate JWT token
    token = auth_service.generate_token(user)

    auth_service.save_token(token)

    # Set Sentry user context
    from src.sentry_config import set_user_context

    set_user_context(user.id, user.username, user.department.value)

    # Success message
    console.print_separator()
    console.print_success(f"Bienvenue {user.first_name} {user.last_name} !")
    console.print_field(c.LABEL_DEPARTMENT, user.department.value)
    console.print_field("Session", "Valide pour 24 heures")
    console.print_separator()


@app.command()
def logout():
    """Logout from the Epic Events CRM application.

    This command deletes the locally stored JWT token.

    Returns:
        None. Displays confirmation message.

    Examples:
        epicevents logout
    """
    # Manually get auth_service from container
    container = Container()
    auth_service = container.auth_service()

    console.print_command_header("Déconnexion")

    # Check if user is authenticated
    user = auth_service.get_current_user()

    if not user:
        console.print_error("Vous n'êtes pas connecté")
        raise typer.Exit(code=1)

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
    """Display information about the currently authenticated user.

    This command shows details of the authenticated user.

    Returns:
        None. Displays user information or error message.

    Examples:
        epicevents whoami
    """
    # Manually get auth_service from container
    container = Container()
    auth_service = container.auth_service()

    console.print_command_header("Utilisateur actuel")

    user = auth_service.get_current_user()

    if not user:
        console.print_error(
            "Vous n'êtes pas connecté. Utilisez 'epicevents login' pour vous connecter."
        )
        raise typer.Exit(code=1)

    console.print_field(c.LABEL_ID, str(user.id))
    console.print_field(c.LABEL_USERNAME, user.username)
    console.print_field("Nom complet", f"{user.first_name} {user.last_name}")
    console.print_field(c.LABEL_EMAIL, user.email)
    console.print_field(c.LABEL_PHONE, user.phone)
    console.print_field(c.LABEL_DEPARTMENT, user.department.value)
    console.print_separator()
