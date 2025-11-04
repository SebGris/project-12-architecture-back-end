"""Event service module for Epic Events CRM.

This module contains the business logic for managing events.
"""

from datetime import datetime
from typing import List, Optional

from src.models.event import Event
from src.repositories.event_repository import EventRepository


class EventService:
    """Service for managing event-related business logic.

    This service handles all event operations including creation,
    retrieval, assignment of support contacts, and validation of event data.
    """

    def __init__(self, repository: EventRepository) -> None:
        self.repository = repository

    def get_event(self, event_id: int) -> Optional[Event]:
        """Get an event by ID.

        Args:
            event_id: The event's ID

        Returns:
            Event instance or None if not found
        """
        return self.repository.get(event_id)

    def create_event(
        self,
        name: str,
        contract_id: int,
        event_start: datetime,
        event_end: datetime,
        location: str,
        attendees: int,
        notes: Optional[str] = None,
        support_contact_id: Optional[int] = None,
    ) -> Event:
        """Create a new event in the database.

        Args:
            name: Name of the event
            contract_id: ID of the associated contract
            event_start: Start date and time of the event
            event_end: End date and time of the event
            location: Location of the event
            attendees: Number of attendees
            notes: Optional notes about the event
            support_contact_id: Optional ID of the support contact

        Returns:
            The created Event instance

        Raises:
            ValueError: If event dates are invalid or attendees is negative
        """
        event = Event(
            name=name,
            contract_id=contract_id,
            event_start=event_start,
            event_end=event_end,
            location=location,
            attendees=attendees,
            notes=notes,
            support_contact_id=support_contact_id,
        )
        return self.repository.add(event)

    def get_events_by_contract(self, contract_id: int) -> List[Event]:
        """Get all events for a specific contract.

        Args:
            contract_id: The contract's ID

        Returns:
            List of Event instances for the contract
        """
        return self.repository.get_by_contract_id(contract_id)

    def get_events_by_support_contact(
        self, support_contact_id: int
    ) -> List[Event]:
        """Get all events assigned to a specific support contact.

        Args:
            support_contact_id: The support user's ID

        Returns:
            List of Event instances assigned to the support contact
        """
        return self.repository.get_by_support_contact(support_contact_id)

    def get_unassigned_events(self) -> List[Event]:
        """Get all events without a support contact assigned.

        Returns:
            List of Event instances without support contact
        """
        return self.repository.get_unassigned_events()

    def get_upcoming_events(
        self, from_date: Optional[datetime] = None
    ) -> List[Event]:
        """Get all upcoming events starting from a given date.

        Args:
            from_date: Starting date (defaults to now if not provided)

        Returns:
            List of upcoming Event instances
        """
        return self.repository.get_upcoming_events(from_date)

    def assign_support_contact(
        self, event_id: int, support_contact_id: int
    ) -> Optional[Event]:
        """Assign a support contact to an event.

        Args:
            event_id: The event's ID
            support_contact_id: The support user's ID

        Returns:
            Updated Event instance or None if not found
        """
        event = self.repository.get(event_id)
        if not event:
            return None

        event.support_contact_id = support_contact_id
        return self.repository.update(event)

    def update_event_notes(self, event_id: int, notes: str) -> Optional[Event]:
        """Update the notes for an event.

        Args:
            event_id: The event's ID
            notes: New notes for the event

        Returns:
            Updated Event instance or None if not found
        """
        event = self.repository.get(event_id)
        if not event:
            return None

        event.notes = notes
        return self.repository.update(event)

    def update_attendees(
        self, event_id: int, attendees: int
    ) -> Optional[Event]:
        """Update the number of attendees for an event.

        Args:
            event_id: The event's ID
            attendees: New number of attendees

        Returns:
            Updated Event instance or None if not found

        Raises:
            ValueError: If attendees is negative
        """
        if attendees < 0:
            raise ValueError("Le nombre de participants doit être positif")

        event = self.repository.get(event_id)
        if not event:
            return None

        event.attendees = attendees
        return self.repository.update(event)

    # todo trop de methode update
