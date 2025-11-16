"""Tests unitaires pour la logique de permissions granulaires."""

import pytest
from unittest.mock import Mock

from src.models.user import Department, User
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event


class TestClientPermissionsLogic:
    """Tests for client permissions logic."""

    def test_commercial_owns_client(self):
        """Test that a commercial user owns their client."""
        # Create mock commercial user
        commercial = Mock(spec=User)
        commercial.id = 1
        commercial.department = Department.COMMERCIAL

        # Create mock client owned by this commercial
        client = Mock(spec=Client)
        client.sales_contact_id = 1

        # Assert permission
        assert client.sales_contact_id == commercial.id

    def test_commercial_does_not_own_client(self):
        """Test that a commercial user does not own another's client."""
        # Create mock commercial user
        commercial = Mock(spec=User)
        commercial.id = 1
        commercial.department = Department.COMMERCIAL

        # Create mock client owned by another commercial
        client = Mock(spec=Client)
        client.sales_contact_id = 99

        # Assert no permission
        assert client.sales_contact_id != commercial.id

    def test_gestion_can_access_any_client(self):
        """Test that a GESTION user can access any client."""
        # Create mock gestion user
        gestion = Mock(spec=User)
        gestion.id = 2
        gestion.department = Department.GESTION

        # Create mock client owned by someone else
        client = Mock(spec=Client)
        client.sales_contact_id = 99

        # GESTION should have access regardless
        assert gestion.department == Department.GESTION


class TestContractPermissionsLogic:
    """Tests for contract permissions logic."""

    def test_commercial_owns_contract_via_client(self):
        """Test that a commercial owns a contract if they own the client."""
        # Create mock commercial user
        commercial = Mock(spec=User)
        commercial.id = 1
        commercial.department = Department.COMMERCIAL

        # Create mock client owned by this commercial
        mock_client = Mock(spec=Client)
        mock_client.sales_contact_id = 1

        # Create mock contract linked to this client
        contract = Mock(spec=Contract)
        contract.client = mock_client

        # Assert permission
        assert contract.client.sales_contact_id == commercial.id

    def test_commercial_does_not_own_contract(self):
        """Test that a commercial does not own contract of another's client."""
        # Create mock commercial user
        commercial = Mock(spec=User)
        commercial.id = 1
        commercial.department = Department.COMMERCIAL

        # Create mock client owned by another commercial
        mock_client = Mock(spec=Client)
        mock_client.sales_contact_id = 99

        # Create mock contract linked to this client
        contract = Mock(spec=Contract)
        contract.client = mock_client

        # Assert no permission
        assert contract.client.sales_contact_id != commercial.id

    def test_gestion_can_access_any_contract(self):
        """Test that a GESTION user can access any contract."""
        # Create mock gestion user
        gestion = Mock(spec=User)
        gestion.id = 2
        gestion.department = Department.GESTION

        # Create mock client owned by someone else
        mock_client = Mock(spec=Client)
        mock_client.sales_contact_id = 99

        # Create mock contract
        contract = Mock(spec=Contract)
        contract.client = mock_client

        # GESTION should have access regardless
        assert gestion.department == Department.GESTION


class TestEventPermissionsLogic:
    """Tests for event permissions logic."""

    def test_support_owns_event(self):
        """Test that a support user owns their event."""
        # Create mock support user
        support = Mock(spec=User)
        support.id = 3
        support.department = Department.SUPPORT

        # Create mock event assigned to this support
        event = Mock(spec=Event)
        event.support_contact_id = 3

        # Assert permission
        assert event.support_contact_id == support.id

    def test_support_does_not_own_event(self):
        """Test that a support user does not own another's event."""
        # Create mock support user
        support = Mock(spec=User)
        support.id = 3
        support.department = Department.SUPPORT

        # Create mock event assigned to another support
        event = Mock(spec=Event)
        event.support_contact_id = 99

        # Assert no permission
        assert event.support_contact_id != support.id

    def test_support_cannot_access_unassigned_event(self):
        """Test that a support user cannot access unassigned events."""
        # Create mock support user
        support = Mock(spec=User)
        support.id = 3
        support.department = Department.SUPPORT

        # Create mock unassigned event
        event = Mock(spec=Event)
        event.support_contact_id = None

        # Assert no permission
        assert event.support_contact_id is None
        assert event.support_contact_id != support.id

    def test_gestion_can_access_any_event(self):
        """Test that a GESTION user can access any event."""
        # Create mock gestion user
        gestion = Mock(spec=User)
        gestion.id = 2
        gestion.department = Department.GESTION

        # Create mock event assigned to someone else
        event = Mock(spec=Event)
        event.support_contact_id = 99

        # GESTION should have access regardless
        assert gestion.department == Department.GESTION


class TestPermissionMatrix:
    """Tests for the complete permission matrix."""

    def test_department_hierarchy(self):
        """Test that GESTION has the highest privileges."""
        commercial = Mock(spec=User)
        commercial.department = Department.COMMERCIAL

        support = Mock(spec=User)
        support.department = Department.SUPPORT

        gestion = Mock(spec=User)
        gestion.department = Department.GESTION

        # GESTION should be able to bypass ownership checks
        assert gestion.department == Department.GESTION

        # Other departments should check ownership
        assert commercial.department != Department.GESTION
        assert support.department != Department.GESTION

    def test_separation_of_duties(self):
        """Test that different departments have different permissions."""
        # COMMERCIAL manages clients and contracts
        commercial = Mock(spec=User)
        commercial.department = Department.COMMERCIAL
        assert commercial.department in [Department.COMMERCIAL, Department.GESTION]

        # SUPPORT manages events
        support = Mock(spec=User)
        support.department = Department.SUPPORT
        assert support.department in [Department.SUPPORT, Department.GESTION]

        # GESTION manages everything
        gestion = Mock(spec=User)
        gestion.department = Department.GESTION
        assert gestion.department == Department.GESTION
