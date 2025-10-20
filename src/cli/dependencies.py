"""Dependency injection utilities for CLI commands.

This module centralizes the creation and configuration of services
and repositories, following the Dependency Inversion Principle.
"""

from contextlib import contextmanager
from typing import Iterator, TypeVar
from sqlalchemy.orm import Session
from src.database import get_db_session
from src.services.client_service import ClientService
from src.services.user_service import UserService
from src.repositories.sqlalchemy_client_repository import (
    SqlAlchemyClientRepository,
)
from src.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)

T = TypeVar("T")


@contextmanager
def db_session_scope() -> Iterator[Session]:
    """Context manager for database sessions with automatic cleanup.

    Yields:
        Active database session

    Example:
        with db_session_scope() as db:
            service = get_client_service(db)
            service.create_client(...)
    """
    db = get_db_session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_client_service(db_session: Session) -> ClientService:
    """Create and configure a ClientService with its dependencies.

    Args:
        db_session: Active database session

    Returns:
        Configured ClientService instance
    """
    repository = SqlAlchemyClientRepository(db_session)
    return ClientService(repository)


def get_user_service(db_session: Session) -> UserService:
    """Create and configure a UserService with its dependencies.

    Args:
        db_session: Active database session

    Returns:
        Configured UserService instance
    """
    repository = SqlAlchemyUserRepository(db_session)
    return UserService(repository)
