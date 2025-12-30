"""Authentication service for Epic Events CRM.

This module handles user authentication and session management.
Token operations are delegated to TokenService and TokenStorageService
following the Single Responsibility Principle (SRP).
"""

from typing import Optional

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.password_hashing_service import PasswordHashingService
from src.services.token_service import TokenService
from src.services.token_storage_service import TokenStorageService
from src.sentry_config import add_breadcrumb, capture_message


class AuthService:
    """Service for handling user authentication and session management.

    This service manages:
    - User authentication (login/logout)
    - Session state (current user)

    Token generation/validation is delegated to TokenService.
    Token persistence is delegated to TokenStorageService.
    Password verification is delegated to PasswordHashingService.
    """

    def __init__(
        self,
        repository: UserRepository,
        token_service: TokenService,
        token_storage: TokenStorageService,
        password_service: PasswordHashingService,
    ) -> None:
        """Initialize the authentication service.

        Args:
            repository: User repository for database access
            token_service: Service for JWT token operations
            token_storage: Service for token persistence
            password_service: Service for password hashing/verification
        """
        self.repository = repository
        self.token_service = token_service
        self.token_storage = token_storage
        self.password_service = password_service

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password.

        Args:
            username: The username
            password: The plain text password

        Returns:
            User instance if authentication successful, None otherwise
        """
        # Add breadcrumb for login attempt
        add_breadcrumb(
            f"Tentative de connexion pour l'utilisateur: {username}",
            category="auth",
            level="info",
        )

        user = self.repository.get_by_username(username)

        if not user:
            # Log failed login attempt (user not found)
            capture_message(
                f"Tentative de connexion échouée - utilisateur inexistant: {username}",
                level="warning",
                context={"username": username, "reason": "user_not_found"},
            )
            return None

        if not self.password_service.verify_password(password, user.password_hash):
            # Log failed login attempt (wrong password)
            capture_message(
                f"Tentative de connexion échouée - mot de passe incorrect: {username}",
                level="warning",
                context={"username": username, "reason": "wrong_password"},
            )
            return None

        # Successful login
        add_breadcrumb(
            f"Connexion réussie pour l'utilisateur: {username}",
            category="auth",
            level="info",
            data={"user_id": user.id, "department": user.department.value},
        )

        return user

    def login(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return a token.

        Args:
            username: The username
            password: The plain text password

        Returns:
            JWT token if authentication successful, None otherwise
        """
        user = self.authenticate(username, password)
        if not user:
            return None

        token = self.token_service.generate_token(user)
        self.token_storage.save(token)
        return token

    def logout(self) -> None:
        """Logout the current user by deleting the stored token."""
        self.token_storage.delete()

    def get_current_user(self) -> Optional[User]:
        """Get the currently authenticated user from the stored token.

        Returns:
            User instance if authenticated, None otherwise
        """
        token = self.token_storage.load()

        if not token:
            return None

        payload = self.token_service.validate_token(token)

        if not payload:
            # Token is invalid or expired, delete it
            self.token_storage.delete()
            return None

        user_id = payload.get("user_id")
        if not user_id:
            return None

        return self.repository.get(user_id)

    def is_authenticated(self) -> bool:
        """Check if there is a currently authenticated user.

        Returns:
            True if authenticated, False otherwise
        """
        return self.get_current_user() is not None

    # Backward compatibility methods (delegate to services)

    def generate_token(self, user: User) -> str:
        """Generate a JWT token for an authenticated user.

        Args:
            user: The authenticated user

        Returns:
            JWT token as a string
        """
        return self.token_service.generate_token(user)

    def validate_token(self, token: str) -> Optional[dict]:
        """Validate a JWT token and return its payload.

        Args:
            token: The JWT token to validate

        Returns:
            Token payload as dict if valid, None otherwise
        """
        return self.token_service.validate_token(token)

    def save_token(self, token: str) -> None:
        """Save the JWT token to disk.

        Args:
            token: The JWT token to save
        """
        self.token_storage.save(token)

    def load_token(self) -> Optional[str]:
        """Load the JWT token from disk.

        Returns:
            The JWT token string if file exists, None otherwise
        """
        return self.token_storage.load()

    def delete_token(self) -> None:
        """Delete the stored JWT token."""
        self.token_storage.delete()
