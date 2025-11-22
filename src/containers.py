"""Dependency injection container for Epic Events CRM.

This module defines the dependency injection container using the
dependency-injector library. It wires together all services, repositories,
and database sessions for the application.

Configuration is externalized in src/config.py, following professional
best practices for dependency injection and the Dependency Inversion Principle.
"""

import os
from pathlib import Path

from dependency_injector import containers, providers

from src.database import get_db_session
from src.config import REPOSITORY_IMPLEMENTATIONS
from src.services.auth_service import AuthService
from src.services.client_service import ClientService
from src.services.contract_service import ContractService
from src.services.event_service import EventService
from src.services.user_service import UserService


class Container(containers.DeclarativeContainer):
    """Dependency injection container for Epic Events CRM.

    This container manages the lifecycle of all application dependencies:
    - Configuration (loaded from YAML files based on APP_ENV)
    - Database sessions
    - Repositories (data access layer)
    - Services (business logic layer)

    Each dependency is configured as a Factory provider, creating
    new instances on each call for proper session management.

    The container supports multiple environments (development, testing, production)
    by loading the appropriate configuration file from the config/ directory.

    Repository implementations are loaded from src.config.REPOSITORY_IMPLEMENTATIONS,
    making it easy to swap implementations for different environments or testing.
    """

    # Configuration provider - loads from YAML based on APP_ENV
    config = providers.Configuration()

    # Determine which config file to load based on environment
    env = os.getenv("APP_ENV", "development")
    config_path = Path(__file__).parent.parent / "config" / f"{env}.yml"

    # Load YAML config if file exists and PyYAML is available
    # This is optional - the container works without it
    try:
        if config_path.exists():
            config.from_yaml(str(config_path))
    except Exception:
        # PyYAML not installed or config file error - continue without it
        pass

    # Database session resource (context manager)
    db_session = providers.Resource(get_db_session)

    # Repositories - loaded from config.REPOSITORY_IMPLEMENTATIONS
    # This allows easy switching of implementations for testing or different environments
    client_repository = providers.Factory(
        REPOSITORY_IMPLEMENTATIONS["client"],
        session=db_session,
    )

    user_repository = providers.Factory(
        REPOSITORY_IMPLEMENTATIONS["user"],
        session=db_session,
    )

    contract_repository = providers.Factory(
        REPOSITORY_IMPLEMENTATIONS["contract"],
        session=db_session,
    )

    event_repository = providers.Factory(
        REPOSITORY_IMPLEMENTATIONS["event"],
        session=db_session,
    )

    # Services (unchanged - depend on repository abstractions)
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
