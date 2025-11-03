"""Dependency injection container for Epic Events CRM.

This module defines the dependency injection container using the
dependency-injector library. It wires together all services, repositories,
and database sessions for the application.
"""

from dependency_injector import containers, providers

from src.database import get_db_session
from src.repositories.sqlalchemy_client_repository import SqlAlchemyClientRepository
from src.repositories.sqlalchemy_contract_repository import SqlAlchemyContractRepository
from src.repositories.sqlalchemy_event_repository import SqlAlchemyEventRepository
from src.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from src.services.auth_service import AuthService
from src.services.client_service import ClientService
from src.services.contract_service import ContractService
from src.services.event_service import EventService
from src.services.user_service import UserService


class Container(containers.DeclarativeContainer):
    """Dependency injection container for Epic Events CRM.

    This container manages the lifecycle of all application dependencies:
    - Database sessions
    - Repositories (data access layer)
    - Services (business logic layer)

    Each dependency is configured as a Factory provider, creating
    new instances on each call for proper session management.
    """

    # Database session factory
    db_session = providers.Factory(get_db_session)

    # Repositories - recréés à chaque appel avec une nouvelle session
    client_repository = providers.Factory(
        SqlAlchemyClientRepository,
        session=db_session,
    )

    user_repository = providers.Factory(
        SqlAlchemyUserRepository,
        session=db_session,
    )

    contract_repository = providers.Factory(
        SqlAlchemyContractRepository,
        session=db_session,
    )

    event_repository = providers.Factory(
        SqlAlchemyEventRepository,
        session=db_session,
    )

    # Services
    auth_service = providers.Factory(
        AuthService,
        repository=user_repository,
    )

    client_service = providers.Factory(
        ClientService,
        repository=client_repository,
    )

    user_service = providers.Factory(
        UserService,
        repository=user_repository,
    )

    contract_service = providers.Factory(
        ContractService,
        repository=contract_repository,
    )

    event_service = providers.Factory(
        EventService,
        repository=event_repository,
    )
