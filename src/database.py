"""Database configuration and session management for Epic Events CRM.

This module provides database connection setup and session management
using SQLAlchemy ORM. It follows the dependency injection pattern
for better testability and maintainability.
"""

import logging
import os

from sqlalchemy import create_engine, orm
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/epic_events_crm.db")
_engine = create_engine(DATABASE_URL, echo=False)
_SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def get_db_session():
    """Get a database session with automatic cleanup.

    This is a generator function that yields a database session and ensures
    proper cleanup when the session is no longer needed. Use with a context
    manager or dependency injection framework.

    Yields:
        Session: SQLAlchemy Session instance

    Example:
        with get_db_session() as session:
            # Use session here
            session.add(obj)
            session.commit()
    """
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Initialize the database by creating all tables.

    This function should be called once when setting up the application
    to create all tables defined in the models.
    """
    Base.metadata.create_all(bind=_engine)
