"""
Tests unitaires pour EventService.

Tests couverts:
- create_event() : création avec tous les paramètres incluant support_contact_id optionnel
- get_event() : récupération par ID
- assign_support_contact() : assignation avec event_id et support_contact_id
- update_event_notes() : mise à jour notes avec event_id
- update_attendees() : mise à jour participants avec event_id
- get_events_by_support_contact() : filtrage par support
- get_unassigned_events() : filtrage événements sans support
"""

import pytest
from datetime import datetime

from src.models.event import Event
from src.services.event_service import EventService


@pytest.fixture
def mock_repository(mocker):
    """Create a mock EventRepository."""
    return mocker.Mock()


@pytest.fixture
def event_service(mock_repository):
    """Create an EventService instance with mock repository."""
    return EventService(repository=mock_repository)


@pytest.fixture
def mock_event():
    """Create a mock event for testing."""
    return Event(
        id=1,
        name="Conference Tech 2025",
        contract_id=10,
        event_start=datetime(2025, 6, 15, 9, 0),
        event_end=datetime(2025, 6, 15, 18, 0),
        location="Paris",
        attendees=100,
        notes="Conférence annuelle",
        support_contact_id=None,
    )


class TestCreateEvent:
    """Test create_event method."""

    def test_create_event_success(self, event_service, mock_repository, mock_event):
        """GIVEN valid event data / WHEN create_event() / THEN event created"""
        # Arrange
        mock_repository.add.return_value = mock_event

        # Act
        result = event_service.create_event(
            name="Conference Tech 2025",
            contract_id=10,
            event_start=datetime(2025, 6, 15, 9, 0),
            event_end=datetime(2025, 6, 15, 18, 0),
            location="Paris",
            attendees=100,
            notes="Conférence annuelle",
            support_contact_id=None,
        )

        # Assert
        mock_repository.add.assert_called_once()
        assert result == mock_event
        # Vérifier que add() a été appelé avec un Event
        call_args = mock_repository.add.call_args[0][0]
        assert isinstance(call_args, Event)
        assert call_args.name == "Conference Tech 2025"
        assert call_args.contract_id == 10

    def test_create_event_with_support_contact(self, event_service, mock_repository):
        """GIVEN support_contact_id / WHEN create_event() / THEN event created with support"""
        event_with_support = Event(
            id=2,
            name="Workshop Python",
            contract_id=11,
            event_start=datetime(2025, 7, 20, 14, 0),
            event_end=datetime(2025, 7, 20, 17, 0),
            location="Lyon",
            attendees=30,
            notes=None,
            support_contact_id=5,
        )
        mock_repository.add.return_value = event_with_support

        result = event_service.create_event(
            name="Workshop Python",
            contract_id=11,
            event_start=datetime(2025, 7, 20, 14, 0),
            event_end=datetime(2025, 7, 20, 17, 0),
            location="Lyon",
            attendees=30,
            notes=None,
            support_contact_id=5,
        )

        assert result.support_contact_id == 5

    def test_create_event_without_notes(self, event_service, mock_repository):
        """GIVEN no notes / WHEN create_event() / THEN event created without notes"""
        event_no_notes = Event(
            id=3,
            name="Meetup Dev",
            contract_id=12,
            event_start=datetime(2025, 8, 10, 19, 0),
            event_end=datetime(2025, 8, 10, 22, 0),
            location="Marseille",
            attendees=50,
            notes=None,
            support_contact_id=None,
        )
        mock_repository.add.return_value = event_no_notes

        # notes et support_contact_id sont optionnels
        result = event_service.create_event(
            name="Meetup Dev",
            contract_id=12,
            event_start=datetime(2025, 8, 10, 19, 0),
            event_end=datetime(2025, 8, 10, 22, 0),
            location="Marseille",
            attendees=50,
        )

        call_args = mock_repository.add.call_args[0][0]
        assert call_args.notes is None


class TestGetEvent:
    """Test get_event method."""

    def test_get_event_found(self, event_service, mock_repository, mock_event):
        """GIVEN existing event_id / WHEN get_event() / THEN returns event"""
        mock_repository.get.return_value = mock_event

        result = event_service.get_event(event_id=1)

        mock_repository.get.assert_called_once_with(1)
        assert result == mock_event
        assert result.id == 1

    def test_get_event_not_found(self, event_service, mock_repository):
        """GIVEN non-existing event_id / WHEN get_event() / THEN returns None"""
        mock_repository.get.return_value = None

        result = event_service.get_event(event_id=999)

        mock_repository.get.assert_called_once_with(999)
        assert result is None


class TestAssignSupportContact:
    """Test assign_support_contact method."""

    def test_assign_support_contact_success(
        self, event_service, mock_repository, mock_event
    ):
        """GIVEN event_id and support_contact_id / WHEN assign_support_contact() / THEN support assigned"""
        # Arrange
        mock_repository.get.return_value = mock_event
        mock_repository.update.return_value = mock_event

        # Act - IMPORTANT: prend event_id et support_contact_id (ints), pas objets
        result = event_service.assign_support_contact(
            event_id=1, support_contact_id=7
        )

        # Assert
        mock_repository.get.assert_called_once_with(1)
        mock_repository.update.assert_called_once_with(mock_event)
        assert result == mock_event
        assert result.support_contact_id == 7

    def test_assign_support_contact_not_found(self, event_service, mock_repository):
        """GIVEN non-existing event_id / WHEN assign_support_contact() / THEN returns None"""
        mock_repository.get.return_value = None

        result = event_service.assign_support_contact(
            event_id=999, support_contact_id=7
        )

        mock_repository.get.assert_called_once_with(999)
        mock_repository.update.assert_not_called()
        assert result is None


class TestUpdateEventNotes:
    """Test update_event_notes method."""

    def test_update_event_notes_success(
        self, event_service, mock_repository, mock_event
    ):
        """GIVEN event_id and notes / WHEN update_event_notes() / THEN notes updated"""
        # Arrange
        mock_repository.get.return_value = mock_event
        mock_repository.update.return_value = mock_event

        # Act - IMPORTANT: prend event_id (int), pas objet Event
        result = event_service.update_event_notes(
            event_id=1, notes="Notes mises à jour"
        )

        # Assert
        mock_repository.get.assert_called_once_with(1)
        mock_repository.update.assert_called_once_with(mock_event)
        assert result == mock_event
        assert result.notes == "Notes mises à jour"

    def test_update_event_notes_not_found(self, event_service, mock_repository):
        """GIVEN non-existing event_id / WHEN update_event_notes() / THEN returns None"""
        mock_repository.get.return_value = None

        result = event_service.update_event_notes(event_id=999, notes="New notes")

        mock_repository.get.assert_called_once_with(999)
        mock_repository.update.assert_not_called()
        assert result is None


class TestUpdateAttendees:
    """Test update_attendees method."""

    def test_update_attendees_success(
        self, event_service, mock_repository, mock_event
    ):
        """GIVEN event_id and attendees / WHEN update_attendees() / THEN attendees updated"""
        # Arrange
        mock_repository.get.return_value = mock_event
        mock_repository.update.return_value = mock_event

        # Act - IMPORTANT: prend event_id (int), pas objet Event
        result = event_service.update_attendees(event_id=1, attendees=150)

        # Assert
        mock_repository.get.assert_called_once_with(1)
        mock_repository.update.assert_called_once_with(mock_event)
        assert result == mock_event
        assert result.attendees == 150

    def test_update_attendees_to_zero(self, event_service, mock_repository, mock_event):
        """GIVEN attendees=0 / WHEN update_attendees() / THEN attendees set to 0"""
        mock_repository.get.return_value = mock_event
        mock_repository.update.return_value = mock_event

        result = event_service.update_attendees(event_id=1, attendees=0)

        assert result.attendees == 0

    def test_update_attendees_not_found(self, event_service, mock_repository):
        """GIVEN non-existing event_id / WHEN update_attendees() / THEN returns None"""
        mock_repository.get.return_value = None

        result = event_service.update_attendees(event_id=999, attendees=200)

        mock_repository.get.assert_called_once_with(999)
        mock_repository.update.assert_not_called()
        assert result is None


class TestGetEventsBySupportContact:
    """Test get_events_by_support_contact method."""

    def test_get_events_by_support_contact(self, event_service, mock_repository):
        """GIVEN support_contact_id / WHEN get_events_by_support_contact() / THEN returns events"""
        # Arrange
        events = [
            Event(
                id=1,
                name="Event 1",
                contract_id=10,
                event_start=datetime(2025, 6, 15, 9, 0),
                event_end=datetime(2025, 6, 15, 18, 0),
                location="Paris",
                attendees=100,
                notes=None,
                support_contact_id=5,
            ),
            Event(
                id=2,
                name="Event 2",
                contract_id=11,
                event_start=datetime(2025, 7, 20, 14, 0),
                event_end=datetime(2025, 7, 20, 17, 0),
                location="Lyon",
                attendees=50,
                notes=None,
                support_contact_id=5,
            ),
        ]
        mock_repository.get_by_support_contact.return_value = events

        # Act
        result = event_service.get_events_by_support_contact(support_contact_id=5)

        # Assert
        mock_repository.get_by_support_contact.assert_called_once_with(5)
        assert len(result) == 2
        assert all(event.support_contact_id == 5 for event in result)

    def test_get_events_by_support_contact_empty(
        self, event_service, mock_repository
    ):
        """GIVEN support without events / WHEN get_events_by_support_contact() / THEN returns empty list"""
        mock_repository.get_by_support_contact.return_value = []

        result = event_service.get_events_by_support_contact(support_contact_id=99)

        assert result == []


class TestGetUnassignedEvents:
    """Test get_unassigned_events method."""

    def test_get_unassigned_events(self, event_service, mock_repository):
        """WHEN get_unassigned_events() / THEN returns events without support"""
        # Arrange
        unassigned_events = [
            Event(
                id=3,
                name="Unassigned Event 1",
                contract_id=12,
                event_start=datetime(2025, 8, 10, 19, 0),
                event_end=datetime(2025, 8, 10, 22, 0),
                location="Marseille",
                attendees=50,
                notes=None,
                support_contact_id=None,
            ),
            Event(
                id=4,
                name="Unassigned Event 2",
                contract_id=13,
                event_start=datetime(2025, 9, 5, 10, 0),
                event_end=datetime(2025, 9, 5, 16, 0),
                location="Toulouse",
                attendees=75,
                notes=None,
                support_contact_id=None,
            ),
        ]
        mock_repository.get_unassigned_events.return_value = unassigned_events

        # Act
        result = event_service.get_unassigned_events()

        # Assert
        mock_repository.get_unassigned_events.assert_called_once()
        assert len(result) == 2
        assert all(event.support_contact_id is None for event in result)

    def test_get_unassigned_events_empty(self, event_service, mock_repository):
        """GIVEN all events assigned / WHEN get_unassigned_events() / THEN returns empty list"""
        mock_repository.get_unassigned_events.return_value = []

        result = event_service.get_unassigned_events()

        assert result == []


class TestGetEventsByContract:
    """Test get_events_by_contract method."""

    def test_get_events_by_contract_success(self, event_service, mock_repository):
        """GIVEN contract with events / WHEN get_events_by_contract() / THEN returns list"""
        # Arrange
        events = [
            Event(
                id=1, name="Conference", contract_id=10,
                event_start=datetime(2025, 3, 15, 9, 0),
                event_end=datetime(2025, 3, 15, 17, 0),
                location="Paris", attendees=100
            ),
            Event(
                id=2, name="Workshop", contract_id=10,
                event_start=datetime(2025, 4, 10, 14, 0),
                event_end=datetime(2025, 4, 10, 18, 0),
                location="Lyon", attendees=50
            ),
        ]
        mock_repository.get_by_contract_id.return_value = events

        # Act
        result = event_service.get_events_by_contract(contract_id=10)

        # Assert
        mock_repository.get_by_contract_id.assert_called_once_with(10)
        assert len(result) == 2
        assert all(event.contract_id == 10 for event in result)

    def test_get_events_by_contract_empty(self, event_service, mock_repository):
        """GIVEN contract with no events / WHEN get_events_by_contract() / THEN returns empty list"""
        mock_repository.get_by_contract_id.return_value = []

        result = event_service.get_events_by_contract(contract_id=999)

        assert result == []


class TestGetUpcomingEvents:
    """Test get_upcoming_events method."""

    def test_get_upcoming_events_success(self, event_service, mock_repository):
        """GIVEN upcoming events / WHEN get_upcoming_events() / THEN returns future events"""
        # Arrange
        from_date = datetime(2025, 3, 1)
        upcoming_events = [
            Event(
                id=5, name="Future Conference", contract_id=20,
                event_start=datetime(2025, 5, 15, 9, 0),
                event_end=datetime(2025, 5, 15, 17, 0),
                location="Paris", attendees=200
            ),
            Event(
                id=6, name="Future Workshop", contract_id=21,
                event_start=datetime(2025, 6, 10, 14, 0),
                event_end=datetime(2025, 6, 10, 18, 0),
                location="Marseille", attendees=80
            ),
        ]
        mock_repository.get_upcoming_events.return_value = upcoming_events

        # Act
        result = event_service.get_upcoming_events(from_date=from_date)

        # Assert
        mock_repository.get_upcoming_events.assert_called_once_with(from_date)
        assert len(result) == 2
        assert all(event.event_start >= from_date for event in result)

    def test_get_upcoming_events_empty(self, event_service, mock_repository):
        """GIVEN no upcoming events / WHEN get_upcoming_events() / THEN returns empty list"""
        from_date = datetime(2025, 12, 31)
        mock_repository.get_upcoming_events.return_value = []

        result = event_service.get_upcoming_events(from_date=from_date)

        assert result == []
