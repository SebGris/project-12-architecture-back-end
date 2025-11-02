"""
Pytest configuration and shared fixtures for Epic Events CRM tests.
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

# L'importation échouera tant que l'implémentation n'existera pas - c'est ce que l'on attend de la méthode TDD.
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session, sessionmaker

    from src.database import Base
    from src.models.client import Client
    from src.models.contract import Contract
    from src.models.event import Event
    from src.models.user import Department, User
except ImportError:
    # Mock for TDD phase
    User = None
    Client = None
    Contract = None
    Event = None
    Base = None
    Department = None


@pytest.fixture
def db_session():
    """
    Create an in-memory SQLite database session for each test.
    Automatically rolls back after each test.
    """
    if Base is None:
        pytest.skip("Models not implemented yet (TDD)")

    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    # Create session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.rollback()
    session.close()


@pytest.fixture
def test_users(db_session):
    """
    Create test users for all departments.
    Returns: dict with user_id -> User object mapping
    """
    if User is None or Department is None:
        pytest.skip("User model not implemented yet (TDD)")

    users = {}

    # Admin (GESTION)
    admin = User(
        username="admin",
        email="admin@epicevents.com",
        first_name="Admin",
        last_name="Gestion",
        phone="+33 1 23 45 67 89",
        department=Department.GESTION,
    )
    admin.set_password("AdminPass123")
    db_session.add(admin)

    # Commercial 1
    commercial1 = User(
        username="commercial1",
        email="commercial1@epicevents.com",
        first_name="Commercial",
        last_name="One",
        phone="+33 1 98 76 54 32",
        department=Department.COMMERCIAL,
    )
    commercial1.set_password("CommPass123")
    db_session.add(commercial1)

    # Commercial 2
    commercial2 = User(
        username="commercial2",
        email="commercial2@epicevents.com",
        first_name="Commercial",
        last_name="Two",
        phone="+33 1 11 22 33 44",
        department=Department.COMMERCIAL,
    )
    commercial2.set_password("Comm2Pass123")
    db_session.add(commercial2)

    # Support 1
    support1 = User(
        username="support1",
        email="support1@epicevents.com",
        first_name="Support",
        last_name="One",
        phone="+33 1 55 66 77 88",
        department=Department.SUPPORT,
    )
    support1.set_password("SuppPass123")
    db_session.add(support1)

    # Support 2
    support2 = User(
        username="support2",
        email="support2@epicevents.com",
        first_name="Support",
        last_name="Two",
        phone="+33 1 99 88 77 66",
        department=Department.SUPPORT,
    )
    support2.set_password("Supp2Pass123")
    db_session.add(support2)

    db_session.commit()

    users["admin"] = admin
    users["commercial1"] = commercial1
    users["commercial2"] = commercial2
    users["support1"] = support1
    users["support2"] = support2

    return users


@pytest.fixture
def test_clients(db_session, test_users):
    """
    Create test clients with different sales contacts.
    """
    if Client is None:
        pytest.skip("Client model not implemented yet (TDD)")

    clients = {}

    # Client 1 - owned by commercial1
    client1 = Client(
        first_name="Kevin",
        last_name="Casey",
        email="kevin@startup.io",
        phone="+678 123 456 78",
        company_name="Cool Startup LLC",
        sales_contact_id=test_users["commercial1"].id,
    )
    db_session.add(client1)

    # Client 2 - owned by commercial1
    client2 = Client(
        first_name="Lou",
        last_name="Bouzin",
        email="lou@company.com",
        phone="+123 456 789 01",
        company_name="Lou Corp",
        sales_contact_id=test_users["commercial1"].id,
    )
    db_session.add(client2)

    # Client 3 - owned by commercial2
    client3 = Client(
        first_name="Jane",
        last_name="Smith",
        email="jane@business.com",
        phone="+999 888 777 66",
        company_name="Smith Enterprises",
        sales_contact_id=test_users["commercial2"].id,
    )
    db_session.add(client3)

    db_session.commit()

    clients["kevin"] = client1
    clients["lou"] = client2
    clients["jane"] = client3

    return clients


@pytest.fixture
def test_contracts(db_session, test_clients):
    """
    Create test contracts with different states (signed/unsigned, paid/unpaid).
    """
    if Contract is None:
        pytest.skip("Contract model not implemented yet (TDD)")

    contracts = {}

    # Contract 1 - signed, partially paid
    contract1 = Contract(
        client_id=test_clients["kevin"].id,
        total_amount=50000.00,
        remaining_amount=10000.00,
        is_signed=True,
    )
    db_session.add(contract1)

    # Contract 2 - unsigned, unpaid
    contract2 = Contract(
        client_id=test_clients["kevin"].id,
        total_amount=30000.00,
        remaining_amount=30000.00,
        is_signed=False,
    )
    db_session.add(contract2)

    # Contract 3 - signed, fully paid
    contract3 = Contract(
        client_id=test_clients["lou"].id,
        total_amount=45000.00,
        remaining_amount=0.00,
        is_signed=True,
    )
    db_session.add(contract3)

    # Contract 4 - signed, unpaid
    contract4 = Contract(
        client_id=test_clients["jane"].id,
        total_amount=20000.00,
        remaining_amount=20000.00,
        is_signed=True,
    )
    db_session.add(contract4)

    db_session.commit()

    contracts["signed_partial"] = contract1
    contracts["unsigned"] = contract2
    contracts["signed_paid"] = contract3
    contracts["signed_unpaid"] = contract4

    return contracts


@pytest.fixture
def test_signed_contracts(db_session, test_contracts):
    """
    Return only signed contracts for testing event creation.
    """
    return {k: v for k, v in test_contracts.items() if v.is_signed}


@pytest.fixture
def test_unsigned_contracts(db_session, test_contracts):
    """
    Return only unsigned contracts for testing validation.
    """
    return {k: v for k, v in test_contracts.items() if not v.is_signed}


@pytest.fixture
def test_events(db_session, test_contracts, test_users):
    """
    Create test events with different support assignments.
    """
    if Event is None:
        pytest.skip("Event model not implemented yet (TDD)")

    events = {}

    # Event 1 - assigned to support1
    event1 = Event(
        name="Cool Startup Launch Event",
        contract_id=test_contracts["signed_partial"].id,
        event_start=datetime(2025, 11, 15, 18, 0),
        event_end=datetime(2025, 11, 15, 23, 0),
        location="Tech Conference Center",
        attendees=100,
        support_contact_id=test_users["support1"].id,
    )
    db_session.add(event1)

    # Event 2 - no support assigned
    event2 = Event(
        name="Corporate Assembly",
        contract_id=test_contracts["signed_paid"].id,
        event_start=datetime(2025, 12, 1, 10, 0),
        event_end=datetime(2025, 12, 1, 15, 0),
        location="Business Center",
        attendees=50,
        support_contact_id=None,
    )
    db_session.add(event2)

    # Event 3 - assigned to support2
    event3 = Event(
        name="Product Demo",
        contract_id=test_contracts["signed_unpaid"].id,
        event_start=datetime(2025, 10, 20, 14, 0),
        event_end=datetime(2025, 10, 20, 17, 0),
        location="Demo Room",
        attendees=30,
        support_contact_id=test_users["support2"].id,
    )
    db_session.add(event3)

    db_session.commit()

    events["launch"] = event1
    events["assembly"] = event2
    events["demo"] = event3

    return events


@pytest.fixture
def authenticated_user(test_users):
    """
    Mock authenticated user (generic).
    """
    return test_users["admin"]


@pytest.fixture
def authenticated_gestion(test_users):
    """
    Mock authenticated GESTION user.
    """
    return test_users["admin"]


@pytest.fixture
def authenticated_commercial(test_users):
    """
    Mock authenticated COMMERCIAL user.
    """
    return test_users["commercial1"]


@pytest.fixture
def authenticated_support(test_users):
    """
    Mock authenticated SUPPORT user.
    """
    return test_users["support1"]


@pytest.fixture
def token_file(tmp_path):
    """
    Create a temporary token file for authentication tests.
    """
    token_dir = tmp_path / ".epic-crm"
    token_dir.mkdir(exist_ok=True)
    token_file_path = token_dir / "token"
    return token_file_path


@pytest.fixture
def mock_sentry():
    """
    Mock Sentry SDK to avoid actual logging during tests.
    """
    # TODO: Implement Sentry mocking when sentry_config.py is created
    pass
