"""Pagination utilities for CLI commands.

This module handles the logic for paginated display of data,
following the Single Responsibility Principle (SRP).
"""

from typing import Callable, List, TypeVar

from src.cli.console import (
    console,
    print_field,
    print_separator,
)

# Type variable for generic pagination
T = TypeVar("T")

# Default page size for pagination
DEFAULT_PAGE_SIZE = 5


def _print_pagination_info(
    current_page: int, total_pages: int, total_items: int
) -> None:
    """Print pagination information.

    Args:
        current_page: Current page number (1-indexed)
        total_pages: Total number of pages
        total_items: Total number of items in the dataset
    """
    console.print(
        f"[dim]Page {current_page}/{total_pages} "
        f"({total_items} élément(s) au total)[/dim]"
    )


def _print_pagination_menu(current_page: int, total_pages: int) -> None:
    """Print pagination navigation menu.

    Args:
        current_page: Current page number (1-indexed)
        total_pages: Total number of pages
    """
    options = []
    if current_page > 1:
        options.append("[cyan]P[/cyan]=Précédent")
    if current_page < total_pages:
        options.append("[cyan]S[/cyan]=Suivant")
    options.append("[cyan]Q[/cyan]=Quitter")

    console.print(f"\n  {' | '.join(options)}")


def _get_user_choice() -> str:
    """Get user input for pagination navigation.

    Returns:
        User's choice as uppercase string, or empty string on interrupt.
    """
    try:
        return console.input("\n  Votre choix: ").strip().upper()
    except (KeyboardInterrupt, EOFError):
        # Handle Ctrl+C or EOF gracefully
        return "Q"


def paginate_display(
    fetch_page: Callable[[int, int], List[T]],
    count_total: Callable[[], int],
    display_item: Callable[[T], None],
    item_name: str = "élément",
    page_size: int = DEFAULT_PAGE_SIZE,
) -> None:
    """Display paginated data with interactive navigation.

    This function fetches and displays data page by page, allowing the user
    to navigate through results using keyboard commands (P=Previous, S=Next,
    Q=Quit).

    Args:
        fetch_page: Function to fetch a page of items. Takes (offset, limit)
                    as parameters and returns a list of items.
        count_total: Function to count the total number of items in the dataset.
        display_item: Function to display a single item to the console.
        item_name: Name of the item type for display messages (e.g., "client").
        page_size: Number of items to display per page (default: DEFAULT_PAGE_SIZE).

    Example:
        >>> paginate_display(
        ...     fetch_page=client_service.get_all_clients,
        ...     count_total=client_service.count_clients,
        ...     display_item=display_client,
        ...     item_name="client",
        ... )
    """
    # Count total items to calculate pagination
    total_items = count_total()

    # Handle empty dataset
    if total_items == 0:
        print_separator()
        print_field("Résultat", f"Aucun {item_name} trouvé")
        print_separator()
        return

    # Calculate total pages using ceiling division (avoids importing math.ceil)
    total_pages = (total_items + page_size - 1) // page_size
    current_page = 1

    # Main pagination loop
    while True:
        # Calculate offset for current page (0-indexed)
        offset = (current_page - 1) * page_size

        # Fetch items for current page from the data source
        items = fetch_page(offset, page_size)

        # Display page header with pagination info
        print_separator()
        _print_pagination_info(current_page, total_pages, total_items)
        print_separator()

        # Display each item using the provided display function
        for item in items:
            display_item(item)
            print_separator()

        # Exit if only one page (no navigation needed)
        if total_pages <= 1:
            break

        # Show navigation menu
        _print_pagination_menu(current_page, total_pages)

        # Wait for user input and process choice
        choice = _get_user_choice()

        if choice == "Q":
            break
        elif choice == "S" and current_page < total_pages:
            current_page += 1
        elif choice == "P" and current_page > 1:
            current_page -= 1
        # Invalid input is silently ignored, page stays the same
