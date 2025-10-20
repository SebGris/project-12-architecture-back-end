"""Input handlers for CLI commands.

This module handles user input collection through prompts.
"""

import re
import typer
from rich.prompt import Prompt
from typing import Dict, Any
from src.models.user import Department

# Regex patterns for validation
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_PATTERN = re.compile(r"^[\d\s\-\+\(\)\.]+$")  # Flexible phone format
USERNAME_PATTERN = re.compile(
    r"^[a-zA-Z0-9_-]{3,50}$"
)  # 3-50 chars, alphanumeric + _ -


def validate_email(email: str) -> bool:
    """Check if email is valid."""
    if not email:
        return False
    return EMAIL_PATTERN.match(email) is not None


def validate_phone(phone: str) -> bool:
    """Check if phone number is valid."""
    if not phone:
        return False

    # Check it contains only allowed characters
    if not PHONE_PATTERN.match(phone):
        return False

    # Check we have between 10 and 15 digits
    digits_count = len([c for c in phone if c.isdigit()])
    if digits_count < 10 or digits_count > 15:
        return False

    return True


def validate_username(username: str) -> bool:
    """Check if username is valid."""
    if not username:
        return False
    return USERNAME_PATTERN.match(username) is not None


def prompt_client_data() -> Dict[str, Any]:
    """Prompt user for client creation data.

    Returns:
        Dictionary containing client data
    """
    print("\n=== Création d'un nouveau client ===\n")

    # Get first name
    while True:
        first_name = typer.prompt("Prénom")
        if len(first_name) >= 2:
            break
        print("Le prénom doit contenir au moins 2 caractères")

    # Get last name
    while True:
        last_name = typer.prompt("Nom")
        if len(last_name) >= 2:
            break
        print("Le nom doit contenir au moins 2 caractères")

    # Get email with validation
    while True:
        email = typer.prompt("Email")
        if validate_email(email):
            break
        print("Format d'email invalide. Veuillez réessayer.")

    # Get phone
    while True:
        phone = typer.prompt("Téléphone")
        if validate_phone(phone):
            break
        print("Numéro de téléphone invalide (minimum 10 chiffres)")

    # Get company name
    company_name = typer.prompt("Nom de l'entreprise")
    while not company_name:
        print("Le nom de l'entreprise est obligatoire")
        company_name = typer.prompt("Nom de l'entreprise")

    # Get sales contact ID
    while True:
        try:
            sales_contact_id = int(typer.prompt("ID du contact commercial"))
            if sales_contact_id > 0:
                break
            print("L'ID doit être un nombre positif")
        except ValueError:
            print("Veuillez entrer un nombre valide")

    return {
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "email": email.strip().lower(),
        "phone": phone.strip(),
        "company_name": company_name.strip(),
        "sales_contact_id": sales_contact_id,
    }


def prompt_user_data() -> Dict[str, Any]:
    """Prompt user for user creation data.

    Returns:
        Dictionary containing user data
    """
    print("\n=== Création d'un nouvel utilisateur ===\n")

    # Username with regex validation
    while True:
        username = typer.prompt("Nom d'utilisateur")
        if validate_username(username):
            break
        print(
            "Le nom d'utilisateur doit contenir 3 à 50 caractères (lettres, chiffres, _, -)"
        )

    # First name
    first_name = typer.prompt("Prénom")
    while len(first_name) < 2:
        print("Le prénom est trop court")
        first_name = typer.prompt("Prénom")

    # Last name
    last_name = typer.prompt("Nom")
    while len(last_name) < 2:
        print("Le nom est trop court")
        last_name = typer.prompt("Nom")

    # Email with regex validation
    while True:
        email = typer.prompt("Email")
        if validate_email(email):
            break
        print("Email invalide")

    # Phone with regex validation
    while True:
        phone = typer.prompt("Téléphone")
        if validate_phone(phone):
            break
        print("Téléphone invalide (minimum 10 chiffres)")

    # Password with confirmation
    while True:
        password = typer.prompt("Mot de passe", hide_input=True)
        if len(password) < 8:
            print("Le mot de passe doit contenir au moins 8 caractères")
            continue

        password_confirm = typer.prompt(
            "Confirmer le mot de passe", hide_input=True
        )
        if password != password_confirm:
            print("Les mots de passe ne correspondent pas")
            continue
        break

    # Department selection
    print("\nDépartements disponibles:")
    departments = list(Department)
    for i, dept in enumerate(departments, 1):
        print(f"{i}. {dept.value}")

    while True:
        try:
            choice = int(typer.prompt("Choisir un département (numéro)"))
            if 1 <= choice <= len(departments):
                department = departments[choice - 1]
                break
            print(f"Veuillez choisir un numéro entre 1 et {len(departments)}")
        except ValueError:
            print("Veuillez entrer un numéro valide")

    return {
        "username": username.strip(),
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "email": email.strip().lower(),
        "phone": phone.strip(),
        "password": password,
        "department": department,
    }


def confirm_action(message: str = "Confirmer l'action?") -> bool:
    """Ask user for confirmation.

    Args:
        message: Question to ask

    Returns:
        True if user confirms, False otherwise
    """
    response = typer.prompt(f"{message} (oui/non)")
    return response.lower() in ["oui", "o", "yes", "y"]
