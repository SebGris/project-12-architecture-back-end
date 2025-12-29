"""Business validation rules for Epic Events CRM.

This module contains business logic validations that are independent
of the CLI layer. These validations can be reused in different contexts
(API, tests, etc.) following the Single Responsibility Principle (SRP).

Validators in this module raise ValueError for invalid business rules.
"""

from datetime import datetime
from decimal import Decimal

from src.models.user import User, Department


class BusinessValidator:
    """Business rules validator for Epic Events CRM.

    This class centralizes all business validation logic that is
    independent of the presentation layer (CLI, API, etc.).
    """

    # Contract validations

    @staticmethod
    def validate_contract_amounts(
        total_amount: Decimal,
        remaining_amount: Decimal,
    ) -> None:
        """Validate contract amounts business rules.

        Args:
            total_amount: Total contract amount
            remaining_amount: Remaining amount to pay

        Raises:
            ValueError: If amounts violate business rules
        """
        if total_amount < 0:
            raise ValueError("Le montant total doit être positif ou zéro")

        if remaining_amount < 0:
            raise ValueError("Le montant restant doit être positif ou zéro")

        if remaining_amount > total_amount:
            raise ValueError(
                f"Le montant restant ({remaining_amount}) ne peut pas "
                f"dépasser le montant total ({total_amount})"
            )

    @staticmethod
    def validate_payment_amount(
        amount_paid: Decimal,
        remaining_amount: Decimal,
    ) -> None:
        """Validate payment amount business rules.

        Args:
            amount_paid: Amount being paid
            remaining_amount: Remaining amount on contract

        Raises:
            ValueError: If payment amount violates business rules
        """
        if amount_paid <= 0:
            raise ValueError("Le montant du paiement doit être positif")

        if amount_paid > remaining_amount:
            raise ValueError(
                f"Le montant du paiement ({amount_paid}) dépasse "
                f"le montant restant ({remaining_amount})"
            )

    # User/Department validations

    @staticmethod
    def validate_user_is_commercial(user: User) -> None:
        """Validate that a user belongs to the COMMERCIAL department.

        Args:
            user: User object with a department attribute

        Raises:
            ValueError: If user is not from COMMERCIAL department
        """
        if user.department != Department.COMMERCIAL:
            raise ValueError(
                f"L'utilisateur {user.id} n'est pas du département COMMERCIAL"
            )

    @staticmethod
    def validate_user_is_support(user: User) -> None:
        """Validate that a user belongs to the SUPPORT department.

        Args:
            user: User object with a department attribute

        Raises:
            ValueError: If user is not from SUPPORT department
        """
        if user.department != Department.SUPPORT:
            raise ValueError(
                f"L'utilisateur {user.id} n'est pas du département SUPPORT"
            )

    # Event validations

    @staticmethod
    def validate_event_dates(
        event_start: datetime,
        event_end: datetime,
        attendees: int,
    ) -> None:
        """Validate event dates and attendees business rules.

        Args:
            event_start: Start date and time of the event
            event_end: End date and time of the event
            attendees: Number of attendees

        Raises:
            ValueError: If event dates are invalid or attendees is negative
        """
        if event_end <= event_start:
            raise ValueError(
                "L'heure de fin de l'événement doit être postérieure "
                "à l'heure de début."
            )
        if attendees < 0:
            raise ValueError("Le nombre de participants doit être positif.")
        if event_start < datetime.now():
            raise ValueError(
                "L'heure de début de l'événement doit être dans le futur."
            )

    @staticmethod
    def validate_attendees_positive(attendees: int) -> None:
        """Validate that the number of attendees is positive.

        Args:
            attendees: Number of attendees

        Raises:
            ValueError: If attendees is negative
        """
        if attendees < 0:
            raise ValueError("Le nombre de participants doit être positif.")
