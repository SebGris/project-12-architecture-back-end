"""User service module for Epic Events CRM.

This module contains the business logic for managing users,
including authentication and password management.
"""

from typing import Optional

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

    def update_user(
        self,
        user_id: int,
        username: str = None,
        email: str = None,
        first_name: str = None,
        last_name: str = None,
        phone: str = None,
        department: Department = None,
    ) -> Optional[User]:
        """Update user information.

        Args:
            user_id: ID of the user to update
            username: New username (optional)
            email: New email (optional)
            first_name: New first name (optional)
            last_name: New last name (optional)
            phone: New phone number (optional)
            department: New department (optional)

        Returns:
            Updated User instance or None if user not found
        """
        user = self.repository.get(user_id)
        if not user:
            return None

        if username:
            user.username = username
        if email:
            user.email = email
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if phone:
            user.phone = phone
        if department:
            user.department = department

        return self.repository.update(user)

    def delete_user(self, user_id: int) -> bool:
        """Delete a user from the system.

        Args:
            user_id: ID of the user to delete

        Returns:
            True if the user was deleted, False if not found
        """
        return self.repository.delete(user_id)

    def exists(self, user_id: int) -> bool:
        """Check if a user exists by ID.

        Args:
            user_id: The user's ID

        Returns:
            True if the user exists, False otherwise
        """
        return self.repository.exists(user_id)

    def username_exists(self, username: str, exclude_id: int = None) -> bool:
        """Check if a username is already in use.

        Args:
            username: The username to check
            exclude_id: Optional user ID to exclude from the check (for updates)

        Returns:
            True if the username is already used, False otherwise
        """
        return self.repository.username_exists(username, exclude_id)

    def email_exists(self, email: str, exclude_id: int = None) -> bool:
        """Check if an email is already in use.

        Args:
            email: The email to check
            exclude_id: Optional user ID to exclude from the check (for updates)

        Returns:
            True if the email is already used, False otherwise
        """
        return self.repository.email_exists(email, exclude_id)
