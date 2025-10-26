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
        pass

    @abstractmethod
    def get(self, user_id: int) -> Optional[User]:
        """Get a user by ID.

        Args:
            user_id: The user's ID

        Returns:
            User instance or None if not found
        """
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username.

        Args:
            username: The user's username

        Returns:
            User instance or None if not found
        """
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email.

        Args:
            email: The user's email

        Returns:
            User instance or None if not found
        """
        pass
