import typer
from rich.console import Console
from sqlalchemy.exc import IntegrityError

from src.services import UserService
from src.database import get_db_session
from src.models.user import Department

app = typer.Typer()
console = Console()
user_service = UserService()


@app.command()
def hello(name: str):
    """Greet someone by name."""
    console.print(f"[blue]👋[/blue] Hello {name}!")


@app.command()
def create_user():
    """Create a new user."""
    db = None
    try:
        db = get_db_session()

        username = typer.prompt("Username")
        first_name = typer.prompt("First Name")
        last_name = typer.prompt("Last Name")
        email = typer.prompt("Email")
        phone = typer.prompt("Phone")
        password = typer.prompt("Password", hide_input=True)
        department_str = typer.prompt(
            "Department (COMMERCIAL, GESTION, SUPPORT)", default="SUPPORT"
        ).upper()

        # Convert department string to enum
        try:
            department = Department[department_str]
        except KeyError:
            console.print(
                f"[red]✗[/red] Invalid department. Must be one of: COMMERCIAL, GESTION, SUPPORT"
            )
            raise typer.Exit(code=1)

        user = user_service.create_user(
            db,
            username,
            email,
            password,
            first_name,
            last_name,
            phone,
            department,
        )
        console.print(f"[green]✓[/green] User {user.username} created!")

    except typer.Abort:
        # User pressed Ctrl+C during prompts
        console.print("\n[yellow]⚠[/yellow] Operation cancelled")
        raise typer.Exit(code=1)
    except IntegrityError:
        # Database constraint violations (duplicate username/email, etc.)
        console.print(f"[red]✗[/red] Database error: User might already exist")
        raise typer.Exit(code=1)
    except Exception as e:
        # Unexpected errors
        console.print(f"[red]✗[/red] Error creating user: {e}")
        raise typer.Exit(code=1)
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    app()
