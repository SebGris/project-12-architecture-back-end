"""
Point d'entrée principal de l'application Epic Events CRM.
Ce module est référencé dans pyproject.toml pour la commande 'epicevents'.
"""

from src.containers import Container
from src.cli import commands


def main():
    """Point d'entrée principal de l'application."""
    # 1. Initialiser le container d'injection de dépendances
    container = Container()

    # 2. Définir le container dans le module commands
    commands.set_container(container)

    # 3. Lancer l'application Typer
    commands.app()


if __name__ == "__main__":
    main()
