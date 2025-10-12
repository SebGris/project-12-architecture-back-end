import typer
from rich.console import Console

from src.services import user_service
from src.database import get_db_session
from src.models.user import Department

app = typer.Typer()
console = Console()


@app.command()
def hello(name: str):
    """Greet someone by name."""
    print(f"Hello {name}")


@app.command()
def create_user():
    """Create a new user."""
    db = get_db_session()
    try:
        username = typer.prompt("Username")
        first_name = typer.prompt("First Name")
        last_name = typer.prompt("Last Name")
        email = typer.prompt("Email")
        phone = typer.prompt("Phone")
        password = typer.prompt("Password", hide_input=True)
        department_str = typer.prompt("Department (COMMERCIAL, GESTION, SUPPORT)").upper()

        # Convert department string to enum
        try:
            department = Department[department_str]
        except KeyError:
            console.print(f"[red]✗[/red] Invalid department. Must be one of: COMMERCIAL, GESTION, SUPPORT")
            return

        user = user_service.create_user(
            db, username, email, password, first_name, last_name, phone, department
        )
        console.print(f"[green]✓[/green] User {user.username} created!")
    except Exception as e:
        console.print(f"[red]✗[/red] Error creating user: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    app()
