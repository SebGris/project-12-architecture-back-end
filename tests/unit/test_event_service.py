"""
Tests unitaires pour EventService.

Tests couverts:
- create_event() : création avec validation dates
- get_event() : récupération par ID
- get_events_by_support_contact() : filtre par support
- get_unassigned_events() : filtre événements sans support
- update_event() : mise à jour
"""

import pytest
from datetime import datetime
from src.services.event_service import EventService


@pytest.fixture
def mock_event_repository(mocker):
    """Create a mock event repository."""
    return mocker.Mock()


@pytest.fixture
def event_service(mock_event_repository):
    """Create an EventService instance with mocked repository."""
    return EventService(mock_event_repository)


@pytest.fixture
def sample_event(mocker):
    """Create a sample event for testing."""
    event = mocker.Mock()
    event.id = 1
    event.contract_id = 1
    event.name = "Conférence Tech"
    event.event_start = datetime(2025, 12, 15, 14, 0)
    event.event_end = datetime(2025, 12, 15, 18, 0)
    event.location = "Paris"
    event.attendees = 100
    event.notes = "Événement important"
    event.support_contact_id = 3
    return event


class TestCreateEvent:
    """Test create_event method."""

    def test_create_event_success(
        self, event_service, mock_event_repository, sample_event
    ):
        """
        GIVEN valid event data
        WHEN create_event is called
        THEN event should be created
        """
        # Configure mock
        mock_event_repository.create.return_value = sample_event

        # Call service
        result = event_service.create_event(
            contract_id=1,
            name="Conférence Tech",
            event_start=datetime(2025, 12, 15, 14, 0),
            event_end=datetime(2025, 12, 15, 18, 0),
            location="Paris",
            attendees=100,
            notes="Événement important",
            support_contact_id=3,
        )

        # Verify repository was called
        mock_event_repository.create.assert_called_once_with(
            contract_id=1,
            name="Conférence Tech",
            event_start=datetime(2025, 12, 15, 14, 0),
            event_end=datetime(2025, 12, 15, 18, 0),
            location="Paris",
            attendees=100,
            notes="Événement important",
            support_contact_id=3,
        )

        # Verify result
        assert result == sample_event


class TestGetEvent:
    """Test get_event method."""

    def test_get_event_found(
        self, event_service, mock_event_repository, sample_event
    ):
        """
        GIVEN an event ID that exists
        WHEN get_event is called
        THEN the event should be returned
        """
        # Configure mock
        mock_event_repository.get_by_id.return_value = sample_event

        # Call service
        result = event_service.get_event(1)

        # Verify
        mock_event_repository.get_by_id.assert_called_once_with(1)
        assert result == sample_event

    def test_get_event_not_found(self, event_service, mock_event_repository):
        """
        GIVEN an event ID that does not exist
        WHEN get_event is called
        THEN None should be returned
        """
        # Configure mock
        mock_event_repository.get_by_id.return_value = None

        # Call service
        result = event_service.get_event(999)

        # Verify
        mock_event_repository.get_by_id.assert_called_once_with(999)
        assert result is None


class TestGetEventsBySupportContact:
    """Test get_events_by_support_contact method."""

    def test_get_events_by_support_contact(
        self, event_service, mock_event_repository, sample_event
    ):
        """
        GIVEN events assigned to a support contact
        WHEN get_events_by_support_contact is called
        THEN assigned events should be returned
        """
        # Configure mock
        events = [sample_event]
        mock_event_repository.get_by_support_contact.return_value = events

        # Call service
        result = event_service.get_events_by_support_contact(support_contact_id=3)

        # Verify
        mock_event_repository.get_by_support_contact.assert_called_once_with(3)
        assert result == events
        assert len(result) == 1
        assert result[0].support_contact_id == 3

    def test_get_events_by_support_contact_empty(
        self, event_service, mock_event_repository
    ):
        """
        GIVEN a support contact with no assigned events
        WHEN get_events_by_support_contact is called
        THEN an empty list should be returned
        """
        # Configure mock
        mock_event_repository.get_by_support_contact.return_value = []

        # Call service
        result = event_service.get_events_by_support_contact(support_contact_id=99)

        # Verify
        mock_event_repository.get_by_support_contact.assert_called_once_with(99)
        assert result == []


class TestGetUnassignedEvents:
    """Test get_unassigned_events method."""

    def test_get_unassigned_events(
        self, event_service, mock_event_repository, sample_event
    ):
        """
        GIVEN events without support contact
        WHEN get_unassigned_events is called
        THEN unassigned events should be returned
        """
        # Configure mock
        unassigned_event = sample_event
        unassigned_event.support_contact_id = None
        mock_event_repository.get_unassigned.return_value = [unassigned_event]

        # Call service
        result = event_service.get_unassigned_events()

        # Verify
        mock_event_repository.get_unassigned.assert_called_once()
        assert result == [unassigned_event]
        assert len(result) == 1

    def test_get_unassigned_events_empty(
        self, event_service, mock_event_repository
    ):
        """
        GIVEN no unassigned events
        WHEN get_unassigned_events is called
        THEN an empty list should be returned
        """
        # Configure mock
        mock_event_repository.get_unassigned.return_value = []

        # Call service
        result = event_service.get_unassigned_events()

        # Verify
        mock_event_repository.get_unassigned.assert_called_once()
        assert result == []


class TestUpdateEvent:
    """Test update_event method."""

    def test_update_event_success(
        self, event_service, mock_event_repository, sample_event
    ):
        """
        GIVEN an existing event and update data
        WHEN update_event is called
        THEN event should be updated
        """
        # Configure mock
        updated_event = sample_event
        updated_event.attendees = 150
        updated_event.notes = "Mise à jour"
        mock_event_repository.update.return_value = updated_event

        # Call service
        result = event_service.update_event(
            event_id=1,
            attendees=150,
            notes="Mise à jour",
        )

        # Verify repository was called
        mock_event_repository.update.assert_called_once_with(
            event_id=1,
            attendees=150,
            notes="Mise à jour",
        )

        # Verify result
        assert result == updated_event
        assert result.attendees == 150
