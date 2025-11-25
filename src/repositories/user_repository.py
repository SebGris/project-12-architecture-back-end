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

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Delete a user by ID.

        Args:
            user_id: The user's ID

        Returns:
            True if the user was deleted, False if not found
        """

    @abstractmethod
    def exists(self, user_id: int) -> bool:
        """Check if a user exists by ID.

        Args:
            user_id: The user's ID

        Returns:
            True if the user exists, False otherwise
        """

    @abstractmethod
    def username_exists(self, username: str, exclude_id: int = None) -> bool:
        """Check if a username is already in use.

        Args:
            username: The username to check
            exclude_id: Optional user ID to exclude from the check (for updates)

        Returns:
            True if the username is already used, False otherwise
        """

    @abstractmethod
    def email_exists(self, email: str, exclude_id: int = None) -> bool:
        """Check if an email is already in use.

        Args:
            email: The email to check
            exclude_id: Optional user ID to exclude from the check (for updates)

        Returns:
            True if the email is already used, False otherwise
        """
