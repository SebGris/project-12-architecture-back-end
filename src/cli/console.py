"""Console utilities for colored and formatted output."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Create a global console instance
console = Console()


def print_success(message: str) -> None:
    """Print a success message in green."""
    console.print(f"[bold green][SUCCES][/bold green] {message}")


def print_error(message: str) -> None:
    """Print an error message in red."""
    console.print(f"[bold red][ERREUR][/bold red] {message}")


def print_info(message: str) -> None:
    """Print an info message in blue."""
    console.print(f"[bold blue][INFO][/bold blue] {message}")


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    console.print(f"[bold yellow][ATTENTION][/bold yellow] {message}")


def print_header(title: str) -> None:
    """Print a styled header with a panel."""
    console.print(
        Panel(
            Text(title, style="bold cyan", justify="center"),
            border_style="cyan",
            padding=(0, 2),
        )
    )


def print_field(label: str, value: str, label_color: str = "cyan") -> None:
    """Print a labeled field with color."""
    console.print(f"  [{label_color}]{label}:[/{label_color}] {value}")


def print_separator() -> None:
    """Print a visual separator."""
    console.print()


def print_command_header(title: str) -> None:
    """Print a command header with separators."""
    print_separator()
    print_header(title)
    print_separator()
