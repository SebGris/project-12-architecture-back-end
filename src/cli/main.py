"""
Point d'entrée principal de l'application Epic Events CRM.
Ce module est référencé dans pyproject.toml pour la commande 'epicevents'.
"""

from src.cli.commands import app

if __name__ == "__main__":
    app()
