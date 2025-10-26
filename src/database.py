from contextlib import contextmanager, AbstractContextManager
from typing import Callable
import logging
import os

from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

Base = declarative_base()

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/epic_events_crm.db")
_engine = create_engine(DATABASE_URL, echo=False)
_SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=_engine)


class Database:

    def __init__(self, db_url: str) -> None:
        self._engine = create_engine(db_url, echo=True)
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def create_database(self) -> None:
        Base.metadata.create_all(self._engine)

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()


def get_db_session() -> Session:
    """Get a database session for dependency injection.

    Returns:
        SQLAlchemy Session instance
    """
    return _SessionLocal()
