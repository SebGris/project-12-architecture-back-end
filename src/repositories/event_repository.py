"""Event repository interface for Epic Events CRM.

This module defines the abstract repository interface for Event persistence.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from src.models.event import Event


class EventRepository(ABC):
    """Abstract repository interface for Event persistence."""

    @abstractmethod
    def get(self, event_id: int) -> Optional[Event]:
        """Get an event by ID.

        Args:
            event_id: The event's ID

        Returns:
            Event instance or None if not found
        """

    @abstractmethod
    def add(self, event: Event) -> Event:
        """Add a new event to the repository.

        Args:
            event: Event instance to add

        Returns:
            The added Event instance (with ID populated after commit)
        """

    @abstractmethod
    def update(self, event: Event) -> Event:
        """Update an existing event in the repository.

        Args:
            event: Event instance to update (must have an ID)

        Returns:
            The updated Event instance
        """

    @abstractmethod
    def get_by_contract_id(self, contract_id: int) -> List[Event]:
        """Get all events for a specific contract.

        Args:
            contract_id: The contract's ID

        Returns:
            List of Event instances for the contract
        """

    @abstractmethod
    def get_by_support_contact(self, support_contact_id: int) -> List[Event]:
        """Get all events assigned to a specific support contact.

        Args:
            support_contact_id: The support user's ID

        Returns:
            List of Event instances assigned to the support contact
        """

    @abstractmethod
    def get_unassigned_events(self) -> List[Event]:
        """Get all events without a support contact assigned.

        Returns:
            List of Event instances without support contact
        """

    @abstractmethod
    def get_upcoming_events(
        self, from_date: Optional[datetime] = None
    ) -> List[Event]:
        """Get all upcoming events starting from a given date.

        Args:
            from_date: Starting date (defaults to now if not provided)

        Returns:
            List of upcoming Event instances
        """

    @abstractmethod
    def exists(self, event_id: int) -> bool:
        """Check if an event exists by ID.

        Args:
            event_id: The event's ID

        Returns:
            True if the event exists, False otherwise
        """
