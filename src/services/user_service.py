"""User service module for Epic Events CRM.

This module contains the business logic for managing users,
including authentication and password management.
"""

from typing import List, Optional

from src.models.user import Department, User
from src.repositories.user_repository import UserRepository


class UserService:
    """Service for managing user-related business logic.

    This service handles user operations including creation,
    retrieval, password hashing, and password verification.
    """
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_user(self, user_id: int) -> Optional[User]:
        """Get a user by ID.

        Args:
            user_id: The user's ID

        Returns:
            User instance or None if not found
        """
        return self.repository.get(user_id)

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone: str,
        department: Department,
    ) -> User:
        """Create a new user with hashed password.

        Args:
            username: Unique username
            email: User email address
            password: Plain text password (will be hashed)
            first_name: User's first name
            last_name: User's last name
            phone: User's phone number
            department: User department (COMMERCIAL, GESTION, or SUPPORT)

        Returns:
            Created User object
        """
        user = User(
            username=username,
            email=email,
            password_hash="",  # Temporary, will be set by set_password
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            department=department,
        )
        user.set_password(password)
        return self.repository.add(user)

    def verify_password(self, user: User, password: str) -> bool:
        """Verify a password against a user's stored hash.

        Args:
            user: User instance with password_hash
            password: Plain text password to verify

        Returns:
            True if password matches, False otherwise
        """
        return user.verify_password(password)
