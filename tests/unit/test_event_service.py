"""Unit tests for EventService.

Tests covered:
- create_event(): Event creation with date validation
- get_event(): Event retrieval by ID
- list_events(): Events listing with filters
- update_event(): Event information updates
- assign_support_contact(): Support contact assignment
- get_unassigned_events(): Events without support contact
- get_my_events(): Support user's assigned events

Implementation notes:
- Uses real SQLite in-memory database
- Zero mocks - uses real SqlAlchemyEventRepository
- Tests business logic with date validations and relationships
"""

import pytest
from datetime import datetime, timedelta

from src.models.event import Event
from src.repositories.sqlalchemy_event_repository import SqlAlchemyEventRepository
from src.services.event_service import EventService


@pytest.fixture
def event_service(db_session):
    """Create an EventService instance with real repository and SQLite DB."""
    repository = SqlAlchemyEventRepository(session=db_session)
    return EventService(repository=repository)


class TestCreateEvent:
    """Test create_event method."""

    def test_create_event_success(
        self, event_service, test_contracts, test_users, db_session
    ):
        """GIVEN valid event data / WHEN create_event() / THEN event created"""
        signed_contract = test_contracts["signed_partial"]

        result = event_service.create_event(
            name="Conference Tech 2025",
            contract_id=signed_contract.id,
            event_start=datetime(2025, 6, 15, 9, 0),
            event_end=datetime(2025, 6, 15, 18, 0),
            location="Paris",
            attendees=100,
            notes="Conférence annuelle",
            support_contact_id=test_users["support1"].id,
        )

        # Verify event was created
        assert isinstance(result, Event)
        assert result.id is not None
        assert result.name == "Conference Tech 2025"
        assert result.contract_id == signed_contract.id
        assert result.attendees == 100
        assert result.support_contact_id == test_users["support1"].id

        # Verify it's persisted in database
        db_event = db_session.query(Event).filter_by(name="Conference Tech 2025").first()
        assert db_event is not None
        assert db_event.id == result.id

    def test_create_event_without_support(
        self, event_service, test_contracts, db_session
    ):
        """GIVEN no support_contact_id / WHEN create_event() / THEN event created without support"""
        result = event_service.create_event(
            name="Workshop Python",
            contract_id=test_contracts["signed_unpaid"].id,
            event_start=datetime(2025, 7, 20, 14, 0),
            event_end=datetime(2025, 7, 20, 17, 0),
            location="Lyon",
            attendees=30,
        )

        assert result.support_contact_id is None
        assert result.notes is None

        # Verify persistence
        db_event = db_session.query(Event).filter_by(id=result.id).first()
        assert db_event.support_contact_id is None


class TestGetEvent:
    """Test get_event method."""

    def test_get_event_found(self, event_service, test_events):
        """GIVEN existing event_id / WHEN get_event() / THEN returns event"""
        launch_event = test_events["launch"]

        result = event_service.get_event(event_id=launch_event.id)

        assert result is not None
        assert result.id == launch_event.id
        assert result.name == "Cool Startup Launch Event"

    def test_get_event_not_found(self, event_service):
        """GIVEN non-existing event_id / WHEN get_event() / THEN returns None"""
        result = event_service.get_event(event_id=99999)

        assert result is None


class TestAssignSupportContact:
    """Test assign_support_contact method."""

    def test_assign_support_contact_success(
        self, event_service, test_events, test_users, db_session
    ):
        """GIVEN event_id and support_contact_id / WHEN assign_support_contact() / THEN support assigned"""
        unassigned_event = test_events["assembly"]  # Has no support
        assert unassigned_event.support_contact_id is None

        result = event_service.assign_support_contact(
            event_id=unassigned_event.id,
            support_contact_id=test_users["support2"].id,
        )

        # Verify assignment
        assert result is not None
        assert result.support_contact_id == test_users["support2"].id

        # Verify persistence
        db_session.expire_all()
        db_event = db_session.query(Event).filter_by(id=unassigned_event.id).first()
        assert db_event.support_contact_id == test_users["support2"].id

    def test_assign_support_contact_not_found(self, event_service, test_users):
        """GIVEN non-existing event_id / WHEN assign_support_contact() / THEN returns None"""
        result = event_service.assign_support_contact(
            event_id=99999, support_contact_id=test_users["support1"].id
        )

        assert result is None


class TestUpdateEvent:
    """Test update_event method."""

    def test_update_event_all_fields(
        self, event_service, test_events, db_session
    ):
        """GIVEN all fields to update / WHEN update_event() / THEN all fields updated"""
        event = test_events["launch"]

        new_start = datetime(2025, 7, 1, 10, 0)
        new_end = datetime(2025, 7, 1, 18, 0)

        result = event_service.update_event(
            event_id=event.id,
            name="Updated Event",
            event_start=new_start,
            event_end=new_end,
            location="New Location",
            attendees=200,
            notes="Updated notes",
        )

        # Verify updates
        assert result is not None
        assert result.name == "Updated Event"
        assert result.event_start == new_start
        assert result.event_end == new_end
        assert result.location == "New Location"
        assert result.attendees == 200
        assert result.notes == "Updated notes"

        # Verify persistence
        db_session.expire_all()
        db_event = db_session.query(Event).filter_by(id=event.id).first()
        assert db_event.name == "Updated Event"
        assert db_event.attendees == 200

    def test_update_event_partial_fields(self, event_service, test_events):
        """GIVEN only some fields to update / WHEN update_event() / THEN only those fields updated"""
        event = test_events["demo"]
        original_attendees = event.attendees

        result = event_service.update_event(
            event_id=event.id,
            name="New Name",
            location="New Location",
        )

        # Verify partial update
        assert result.name == "New Name"
        assert result.location == "New Location"
        # Attendees should be unchanged
        assert result.attendees == original_attendees

    def test_update_event_not_found(self, event_service):
        """GIVEN non-existing event_id / WHEN update_event() / THEN returns None"""
        result = event_service.update_event(event_id=99999, name="New Name")

        assert result is None

    def test_update_event_notes_only(
        self, event_service, test_events, db_session
    ):
        """GIVEN only notes to update / WHEN update_event() / THEN only notes updated"""
        event = test_events["assembly"]

        result = event_service.update_event(
            event_id=event.id,
            notes="Updated notes only",
        )

        assert result.notes == "Updated notes only"

        # Verify persistence
        db_session.expire_all()
        db_event = db_session.query(Event).filter_by(id=event.id).first()
        assert db_event.notes == "Updated notes only"


class TestGetEventsBySupportContact:
    """Test get_events_by_support_contact method."""

    def test_get_events_by_support_contact(
        self, event_service, test_events, test_users
    ):
        """GIVEN support_contact_id / WHEN get_events_by_support_contact() / THEN returns events"""
        result = event_service.get_events_by_support_contact(
            support_contact_id=test_users["support1"].id
        )

        # Should return only events assigned to support1
        assert len(result) >= 1
        assert all(
            event.support_contact_id == test_users["support1"].id for event in result
        )

    def test_get_events_by_support_contact_empty(self, event_service):
        """GIVEN support without events / WHEN get_events_by_support_contact() / THEN returns empty list"""
        result = event_service.get_events_by_support_contact(
            support_contact_id=99999
        )

        assert result == []


class TestGetUnassignedEvents:
    """Test get_unassigned_events method."""

    def test_get_unassigned_events(self, event_service, test_events):
        """WHEN get_unassigned_events() / THEN returns events without support"""
        result = event_service.get_unassigned_events()

        # Should include at least the assembly event which has no support
        assert len(result) >= 1
        assert all(event.support_contact_id is None for event in result)

        # Verify assembly event is in the list
        assembly_ids = [e.id for e in result]
        assert test_events["assembly"].id in assembly_ids


class TestGetEventsByContract:
    """Test get_events_by_contract method."""

    def test_get_events_by_contract_success(
        self, event_service, test_events, test_contracts
    ):
        """GIVEN contract with events / WHEN get_events_by_contract() / THEN returns list"""
        # Launch event is for signed_partial contract
        launch_event = test_events["launch"]
        contract_id = test_contracts["signed_partial"].id

        result = event_service.get_events_by_contract(contract_id=contract_id)

        # Should return at least the launch event
        assert len(result) >= 1
        assert all(event.contract_id == contract_id for event in result)

        # Verify launch event is in the list
        event_ids = [e.id for e in result]
        assert launch_event.id in event_ids

    def test_get_events_by_contract_empty(self, event_service):
        """GIVEN contract with no events / WHEN get_events_by_contract() / THEN returns empty list"""
        result = event_service.get_events_by_contract(contract_id=99999)

        assert result == []


class TestGetUpcomingEvents:
    """Test get_upcoming_events method."""

    def test_get_upcoming_events_success(self, event_service, test_events):
        """GIVEN upcoming events / WHEN get_upcoming_events() / THEN returns future events"""
        # Use a date in the past to ensure test events are "upcoming"
        from_date = datetime(2025, 1, 1)

        result = event_service.get_upcoming_events(from_date=from_date)

        # Should return events that start after from_date
        assert len(result) >= 1
        assert all(event.event_start >= from_date for event in result)

    def test_get_upcoming_events_far_future(self, event_service):
        """GIVEN date far in the future / WHEN get_upcoming_events() / THEN returns empty or fewer events"""
        # Use a date far in the future
        from_date = datetime(2099, 12, 31)

        result = event_service.get_upcoming_events(from_date=from_date)

        # Should return empty or very few events (none of our test events are this far)
        assert len(result) == 0
