"""CLI input validators for Typer callbacks.

This module contains validators for CLI input (Typer callbacks).
Business validation rules are in src/cli/business_validator.py (SRP compliance).
"""

import re

import typer

from src.models.user import Department

# Regex patterns for validation
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
# Pattern pour numéros de téléphone: accepte chiffres, espaces, tirets, +, parenthèses et points
# Permet des formats comme: "01 23 45 67 89", "+33 1 23 45 67 89", "(01) 23.45.67.89"
PHONE_PATTERN = re.compile(r"^[\d\s\-\+\(\)\.]+$")
# Pattern pour nom d'utilisateur: lettres (a-z, A-Z), chiffres (0-9), underscore (_) et tiret (-)
# Longueur: entre 4 et 50 caractères. Ex: "john_doe", "user-123", "Admin_2024"
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{4,50}$")
# Pattern pour noms et prénoms: lettres (incluant accents), espaces, tirets et apostrophes
# Permet: "Jean", "Marie-Claire", "O'Connor", "François", "De La Cruz"
NAME_PATTERN = re.compile(r"^[a-zA-ZÀ-ÿ\s\-']+$")


# Callback validators for typer.Option
def validate_first_name_callback(value: str) -> str:
    """Validate and clean first name."""
    cleaned = value.strip()
    if len(cleaned) < 2:
        raise typer.BadParameter("Le prénom doit avoir au moins 2 caractères")
    if not NAME_PATTERN.match(cleaned):
        raise typer.BadParameter(
            "Le prénom ne peut contenir que des lettres, espaces, tirets et apostrophes"
        )
    return cleaned


def validate_last_name_callback(value: str) -> str:
    """Validate and clean last name."""
    cleaned = value.strip()
    if len(cleaned) < 2:
        raise typer.BadParameter("Le nom doit avoir au moins 2 caractères")
    if not NAME_PATTERN.match(cleaned):
        raise typer.BadParameter(
            "Le nom ne peut contenir que des lettres, espaces, tirets et apostrophes"
        )
    return cleaned


def validate_email_callback(value: str) -> str:
    """Validate and clean email."""
    cleaned = value.strip().lower()
    if not EMAIL_PATTERN.match(cleaned):
        raise typer.BadParameter(f"Email invalide: {value}")
    return cleaned


def validate_phone_callback(value: str) -> str:
    """Validate and clean phone number."""
    cleaned = value.strip()
    if not PHONE_PATTERN.match(cleaned):
        raise typer.BadParameter(f"Format de téléphone invalide: {value}")
    # Extrait uniquement les chiffres en supprimant tous les caractères non-numériques
    # Ex: "+33 1 23 45 67 89" devient "33123456789"
    digits = re.sub(r"\D", "", cleaned)
    if len(digits) < 10:
        raise typer.BadParameter(
            "Le téléphone doit avoir au moins 10 chiffres"
        )
    return cleaned


def validate_company_name_callback(value: str) -> str:
    """Validate and clean company name."""
    cleaned = value.strip()
    if not cleaned:
        raise typer.BadParameter("Le nom de l'entreprise est requis")
    return cleaned


def validate_sales_contact_id_callback(value: int) -> int:
    """Validate sales contact ID.

    Accepts 0 for auto-assignment or positive integers for specific sales contact.
    """
    if value < 0:
        raise typer.BadParameter(
            "L'ID du contact doit être 0 (auto-assignation) ou positif"
        )
    return value


def validate_username_callback(value: str) -> str:
    """Validate and clean username."""
    cleaned = value.strip()
    if not USERNAME_PATTERN.match(cleaned):
        raise typer.BadParameter(
            "Username invalide (4-50 caractères, lettres/chiffres/_/-)"
        )
    return cleaned


def validate_password_callback(value: str) -> str:
    """Validate password."""
    if len(value) < 8:
        raise typer.BadParameter(
            "Le mot de passe doit avoir au moins 8 caractères"
        )
    return value


def validate_department_callback(value: int) -> int:
    """Validate department selection."""
    departments = list(Department)
    if value < 1 or value > len(departments):
        raise typer.BadParameter(
            f"Choix invalide. Veuillez choisir entre 1 et {len(departments)}"
        )
    return value


def validate_client_id_callback(value: int) -> int:
    """Validate client ID."""
    if value <= 0:
        raise typer.BadParameter("L'ID du client doit être positif")
    return value


def validate_amount_callback(value: str) -> str:
    """Validate monetary amount."""
    cleaned = value.strip()
    try:
        amount = float(cleaned)
        if amount < 0:
            raise typer.BadParameter("Le montant doit être positif ou zéro")
        return cleaned
    except ValueError:
        raise typer.BadParameter(f"Montant invalide: {value}")


def validate_contract_id_callback(value: int) -> int:
    """Validate contract ID."""
    if value <= 0:
        raise typer.BadParameter("L'ID du contrat doit être positif")
    return value


def validate_event_id_callback(value: int) -> int:
    """Validate event ID."""
    if value <= 0:
        raise typer.BadParameter("L'ID de l'événement doit être positif")
    return value


def validate_user_id_callback(value: int) -> int:
    """Validate user ID."""
    if value <= 0:
        raise typer.BadParameter("L'ID de l'utilisateur doit être positif")
    return value


def validate_event_name_callback(value: str) -> str:
    """Validate and clean event name."""
    cleaned = value.strip()
    if len(cleaned) < 3:
        raise typer.BadParameter(
            "Le nom de l'événement doit avoir au moins 3 caractères"
        )
    if len(cleaned) > 100:
        raise typer.BadParameter(
            "Le nom de l'événement ne peut pas dépasser 100 caractères"
        )
    return cleaned


def validate_location_callback(value: str) -> str:
    """Validate and clean location."""
    cleaned = value.strip()
    if not cleaned:
        raise typer.BadParameter("L'emplacement est requis")
    if len(cleaned) > 255:
        raise typer.BadParameter(
            "L'emplacement ne peut pas dépasser 255 caractères"
        )
    return cleaned


def validate_attendees_callback(value: int) -> int:
    """Validate number of attendees."""
    if value < 0:
        raise typer.BadParameter(
            "Le nombre de participants doit être positif ou zéro"
        )
    return value


def validate_support_contact_id_callback(value: int) -> int:
    """Validate support contact ID (optional, so 0 is acceptable)."""
    if value < 0:
        raise typer.BadParameter("L'ID du contact support doit être positif")
    return value
