"""Configuration module for Epic Events CRM.

This module provides a centralized mapping of repository interfaces to their
concrete implementations. This allows easy switching between implementations
for different environments (development, testing, production).

Following the Dependency Inversion Principle, the container depends on this
configuration module rather than directly importing concrete implementations.
"""

import os

# Import concrete repository implementations
from src.repositories.sqlalchemy_client_repository import SqlAlchemyClientRepository
from src.repositories.sqlalchemy_contract_repository import (
    SqlAlchemyContractRepository,
)
from src.repositories.sqlalchemy_event_repository import SqlAlchemyEventRepository
from src.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository

# Determine environment
ENV = os.getenv("APP_ENV", "development")


# Repository implementations mapping
# This maps repository names to their concrete implementation classes
# Can be easily changed for different environments or testing
REPOSITORY_IMPLEMENTATIONS = {
    "user": SqlAlchemyUserRepository,
    "client": SqlAlchemyClientRepository,
    "contract": SqlAlchemyContractRepository,
    "event": SqlAlchemyEventRepository,
}


# For testing environment, you could override with:
# if ENV == "testing":
#     from tests.fakes.in_memory_user_repository import InMemoryUserRepository
#     REPOSITORY_IMPLEMENTATIONS["user"] = InMemoryUserRepository
#     ...

# For a different database backend (e.g., MongoDB):
# if ENV == "production":
#     from src.repositories.mongodb_user_repository import MongoDBUserRepository
#     REPOSITORY_IMPLEMENTATIONS["user"] = MongoDBUserRepository
#     ...
