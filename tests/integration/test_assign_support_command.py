"""
Tests d'intégration pour la commande assign-support.

Tests couverts:
- assign-support : erreur utilisateur non SUPPORT (validation métier)

Ce test utilise de vrais objets (User, Client, Contract, Event) créés en base de données
SQLite in-memory, sans aucun mock. Cela respecte les bonnes pratiques de tests d'intégration.
"""

import pytest
from datetime import datetime, timedelta
from typer.testing import CliRunner

from src.cli.commands import app
from src.models.user import Department, User
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event

runner = CliRunner()


@pytest.fixture
def support_user(db_session):
    """Create a real support user in database."""
    user = User(
        username="support1",
        email="support1@epicevents.com",
        first_name="Charlie",
        last_name="Support",
        phone="+33133333333",
        department=Department.SUPPORT,
        password_hash="",
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def commercial_user(db_session):
    """Create a real commercial user in database."""
    user = User(
        username="commercial1",
        email="commercial1@epicevents.com",
        first_name="Bob",
        last_name="Commercial",
        phone="+33122222222",
        department=Department.COMMERCIAL,
        password_hash="",
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def gestion_user(db_session):
    """Create a real gestion user in database."""
    user = User(
        username="gestion1",
        email="gestion1@epicevents.com",
        first_name="Alice",
        last_name="Gestion",
        phone="+33111111111",
        department=Department.GESTION,
        password_hash="",
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_client(db_session, commercial_user):
    """Create a real client in database."""
    client = Client(
        first_name="Test",
        last_name="Client",
        email="client@test.com",
        phone="+33144444444",
        company_name="Test Corp",
        sales_contact_id=commercial_user.id,
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


@pytest.fixture
def test_contract(db_session, test_client):
    """Create a real contract in database."""
    contract = Contract(
        client_id=test_client.id,
        total_amount=10000.00,
        remaining_amount=5000.00,
        is_signed=True,
    )
    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)
    return contract


@pytest.fixture
def test_event(db_session, test_contract):
    """Create a real event in database without support contact."""
    event = Event(
        name="Conference Tech",
        contract_id=test_contract.id,
        event_start=datetime.now() + timedelta(days=30),
        event_end=datetime.now() + timedelta(days=30, hours=8),
        location="Paris",
        attendees=100,
        notes="Test conference",
        support_contact_id=None,  # No support assigned yet
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


class TestAssignSupportCommand:
    """Test assign-support command - validation métier avec vrais objets."""

    def test_assign_support_user_not_support_department(
        self, db_session, test_event, commercial_user
    ):
        """
        GIVEN user from COMMERCIAL department (not SUPPORT)
        WHEN assign-support is executed with commercial user ID
        THEN error displayed about wrong department
        AND support contact is NOT assigned
        """
        # Execute command - try to assign commercial user as support
        result = runner.invoke(
            app,
            ["assign-support"],
            input=f"{test_event.id}\n{commercial_user.id}\n",
        )

        # Verify error is raised
        assert result.exit_code == 1
        assert (
            "support" in result.stdout.lower()
            or "département" in result.stdout.lower()
        )

        # Verify event was NOT modified in database
        db_session.refresh(test_event)
        assert test_event.support_contact_id is None
