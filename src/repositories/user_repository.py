"""User repository interface for Epic Events CRM.

This module defines the abstract repository interface for User persistence,
following the Repository pattern to decouple business logic from data access.
"""

from abc import ABC, abstractmethod
from typing import Optional

from src.models.user import User


class UserRepository(ABC):
    """Abstract repository interface for User persistence."""

    @abstractmethod
    def add(self, user: User) -> User:
        """Add a new user to the repository.

        Args:
            user: User instance to add

        Returns:
            The added User instance (with ID populated after commit)
        """

    @abstractmethod
    def get(self, user_id: int) -> Optional[User]:
        """Get a user by ID.

        Args:
            user_id: The user's ID

        Returns:
            User instance or None if not found
        """

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username.

        Args:
            username: The user's username

        Returns:
            User instance or None if not found
        """

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email.

        Args:
            email: The user's email

        Returns:
            User instance or None if not found
        """

    @abstractmethod
    def update(self, user: User) -> User:
        """Update an existing user.

        Args:
            user: User instance to update

        Returns:
            The updated User instance
        """
