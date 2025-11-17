"""
Integration tests for SqlAlchemyEventRepository.
"""

import pytest
from datetime import datetime

from src.models.event import Event
from src.repositories.sqlalchemy_event_repository import SqlAlchemyEventRepository


@pytest.fixture
def event_repository(db_session):
    """Create an EventRepository with the test database session."""
    return SqlAlchemyEventRepository(session=db_session)


class TestEventRepositoryGet:
    """Test get method."""

    def test_get_existing_event(self, event_repository, test_events):
        """GIVEN existing event / WHEN get(event_id) / THEN returns event"""
        launch = test_events["launch"]

        result = event_repository.get(launch.id)

        assert result is not None
        assert result.id == launch.id
        assert result.name == "Cool Startup Launch Event"

    def test_get_nonexistent_event(self, event_repository):
        """GIVEN nonexistent event_id / WHEN get() / THEN returns None"""
        result = event_repository.get(99999)

        assert result is None


class TestEventRepositoryAdd:
    """Test add method."""

    def test_add_new_event(self, event_repository, test_contracts, db_session):
        """GIVEN new event / WHEN add() / THEN event saved with ID"""
        new_event = Event(
            name="New Product Launch",
            contract_id=test_contracts["signed_partial"].id,
            event_start=datetime(2025, 12, 10, 18, 0),
            event_end=datetime(2025, 12, 10, 22, 0),
            location="Convention Center",
            attendees=200,
        )

        result = event_repository.add(new_event)

        assert result.id is not None
        assert result.name == "New Product Launch"

        # Verify it's in database
        db_event = db_session.query(Event).filter_by(id=result.id).first()
        assert db_event is not None


class TestEventRepositoryUpdate:
    """Test update method."""

    def test_update_event(self, event_repository, test_events, test_users, db_session):
        """GIVEN existing event with changes / WHEN update() / THEN changes persisted"""
        event = test_events["assembly"]
        event.support_contact_id = test_users["support1"].id
        event.notes = "Updated notes"

        result = event_repository.update(event)

        assert result.support_contact_id == test_users["support1"].id
        assert result.notes == "Updated notes"

        # Verify changes persisted
        db_session.expire_all()
        db_event = db_session.query(Event).filter_by(id=event.id).first()
        assert db_event.support_contact_id == test_users["support1"].id


class TestEventRepositoryGetByContractId:
    """Test get_by_contract_id method."""

    def test_get_by_contract_id(self, event_repository, test_events, test_contracts):
        """GIVEN contract with event / WHEN get_by_contract_id() / THEN returns events"""
        contract = test_contracts["signed_partial"]

        result = event_repository.get_by_contract_id(contract.id)

        assert len(result) == 1
        assert result[0].name == "Cool Startup Launch Event"


class TestEventRepositoryGetBySupportContact:
    """Test get_by_support_contact method."""

    def test_get_by_support_contact(self, event_repository, test_users, test_events):
        """GIVEN support user with events / WHEN get_by_support_contact() / THEN returns their events"""
        support1 = test_users["support1"]

        result = event_repository.get_by_support_contact(support1.id)

        assert len(result) == 1
        assert result[0].support_contact_id == support1.id


class TestEventRepositoryGetUnassignedEvents:
    """Test get_unassigned_events method."""

    def test_get_unassigned_events(self, event_repository, test_events):
        """GIVEN events with and without support / WHEN get_unassigned_events() / THEN returns unassigned"""
        result = event_repository.get_unassigned_events()

        assert len(result) == 1
        assert all(e.support_contact_id is None for e in result)
        assert result[0].name == "Corporate Assembly"


class TestEventRepositoryGetUpcomingEvents:
    """Test get_upcoming_events method."""

    def test_get_upcoming_events(self, event_repository, test_events):
        """GIVEN upcoming events / WHEN get_upcoming_events() / THEN returns future events"""
        from_date = datetime(2025, 11, 1)

        result = event_repository.get_upcoming_events(from_date)

        # Should return "Cool Startup Launch Event" (2025-11-15) and "Corporate Assembly" (2025-12-01)
        # but NOT "Product Demo" (2025-10-20)
        assert len(result) == 2
        assert all(e.event_start >= from_date for e in result)
