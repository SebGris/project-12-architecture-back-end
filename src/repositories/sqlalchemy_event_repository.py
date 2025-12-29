"""SQLAlchemy implementation of EventRepository.

This module provides the concrete implementation of the EventRepository
interface using SQLAlchemy ORM.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.event import Event
from src.repositories.event_repository import EventRepository


class SqlAlchemyEventRepository(EventRepository):
    """SQLAlchemy implementation of EventRepository."""

    def __init__(self, session: Session):
        self.session = session

    def get(self, event_id: int) -> Optional[Event]:
        """Get an event by ID.

        Args:
            event_id: The event's ID

        Returns:
            Event instance or None if not found
        """
        return self.session.query(Event).filter_by(id=event_id).first()

    def add(self, event: Event) -> Event:
        """Add a new event to the repository.

        Args:
            event: Event instance to add

        Returns:
            The added Event instance (with ID populated after commit)
        """
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def update(self, event: Event) -> Event:
        """Update an existing event in the repository.

        Args:
            event: Event instance to update (must have an ID)

        Returns:
            The updated Event instance
        """
        event = self.session.merge(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def get_by_contract_id(self, contract_id: int) -> List[Event]:
        """Get all events for a specific contract.

        Args:
            contract_id: The contract's ID

        Returns:
            List of Event instances for the contract
        """
        return (
            self.session.query(Event).filter_by(contract_id=contract_id).all()
        )

    def get_by_support_contact(self, support_contact_id: int) -> List[Event]:
        """Get all events assigned to a specific support contact.

        Args:
            support_contact_id: The support user's ID

        Returns:
            List of Event instances assigned to the support contact
        """
        return (
            self.session.query(Event)
            .filter_by(support_contact_id=support_contact_id)
            .all()
        )

    def get_unassigned_events(self) -> List[Event]:
        """Get all events without a support contact assigned.

        Returns:
            List of Event instances without support contact
        """
        return (
            self.session.query(Event).filter_by(support_contact_id=None).all()
        )

    def get_upcoming_events(
        self, from_date: Optional[datetime] = None
    ) -> List[Event]:
        """Get all upcoming events starting from a given date.

        Args:
            from_date: Starting date (defaults to now if not provided)

        Returns:
            List of upcoming Event instances
        """
        if from_date is None:
            from_date = datetime.now()

        return (
            self.session.query(Event)
            .filter(Event.event_start >= from_date)
            .order_by(Event.event_start)
            .all()
        )

    def exists(self, event_id: int) -> bool:
        """Check if an event exists by ID.

        Args:
            event_id: The event's ID

        Returns:
            True if the event exists, False otherwise
        """
        return (
            self.session.query(Event).filter_by(id=event_id).first() is not None
        )

    def get_all(self) -> List[Event]:
        """Get all events (read-only access for all departments).

        Returns:
            List of all Event instances
        """
        return self.session.query(Event).all()
