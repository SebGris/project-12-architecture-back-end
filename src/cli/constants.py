"""Shared constants for CLI commands.

This module centralizes common constants used across multiple command modules
to follow DRY (Don't Repeat Yourself) principles and facilitate maintenance.
"""

# Common field labels
LABEL_ID = "ID"
LABEL_EMAIL = "Email"
LABEL_PHONE = "Téléphone"
LABEL_USERNAME = "Nom d'utilisateur"
LABEL_DEPARTMENT = "Département"
LABEL_DATE_CREATION = "Date de création"
LABEL_CONTACT_COMMERCIAL = "Contact commercial"

# Date/time formats
FORMAT_DATETIME = "%Y-%m-%d %H:%M:%S"
FORMAT_DATE = "%Y-%m-%d"

# Common error messages
ERROR_UNEXPECTED = "Erreur inattendue: {e}"

# Common prompts
PROMPT_TELEPHONE = "Téléphone"
