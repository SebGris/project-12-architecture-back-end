"""Authentication service for Epic Events CRM.

This module handles user authentication, JWT token generation and validation.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import jwt
from dotenv import load_dotenv

from src.models.user import User
from src.repositories.user_repository import UserRepository

# Load environment variables from .env file
load_dotenv()


class AuthService:
    """Service for handling authentication and JWT tokens.

    This service manages:
    - User authentication (login)
    - JWT token generation and validation
    - Token storage and retrieval
    - User session management
    """

    # JWT Configuration
    TOKEN_EXPIRATION_HOURS = 24
    ALGORITHM = "HS256"  # Secure algorithm (not HS512 which has vulnerabilities)
    TOKEN_FILE = Path.home() / ".epicevents" / "token"

    def __init__(self, repository: UserRepository) -> None:
        """Initialize the authentication service.

        Args:
            repository: User repository for database access
        """
        self.repository = repository
        self._secret_key = self._get_or_create_secret_key()

    def _get_or_create_secret_key(self) -> str:
        """Get or create a secure secret key for JWT signing.

        The secret key is stored in an environment variable or generated
        securely if not present.

        Returns:
            The secret key as a string
        """
        # Try to get from environment variable first (production)
        secret_key = os.getenv("EPICEVENTS_SECRET_KEY")

        if not secret_key:
            # For development, generate a secure random key
            # In production, this should ALWAYS be set via environment variable
            import secrets
            secret_key = secrets.token_hex(32)  # 256 bits

        return secret_key

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password.

        Args:
            username: The username
            password: The plain text password

        Returns:
            User instance if authentication successful, None otherwise
        """
        user = self.repository.get_by_username(username)

        if not user:
            return None

        if not user.verify_password(password):
            return None

        return user

    def generate_token(self, user: User) -> str:
        """Generate a JWT token for an authenticated user.

        The token contains:
        - user_id: The user's database ID
        - username: The user's username
        - department: The user's department
        - exp: Token expiration timestamp
        - iat: Token issued at timestamp

        Args:
            user: The authenticated user

        Returns:
            JWT token as a string
        """
        now = datetime.utcnow()
        expiration = now + timedelta(hours=self.TOKEN_EXPIRATION_HOURS)

        payload = {
            "user_id": user.id,
            "username": user.username,
            "department": user.department.value,
            "exp": expiration,
            "iat": now,
        }

        token = jwt.encode(payload, self._secret_key, algorithm=self.ALGORITHM)
        return token

    def validate_token(self, token: str) -> Optional[dict]:
        """Validate a JWT token and return its payload.

        Args:
            token: The JWT token to validate

        Returns:
            Token payload as dict if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Token is invalid
            return None

    def save_token(self, token: str) -> None:
        """Save the JWT token to disk for persistent authentication.

        The token is stored in the user's home directory in a hidden folder.

        Args:
            token: The JWT token to save
        """
        # Create directory if it doesn't exist
        self.TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Write token to file with restricted permissions
        self.TOKEN_FILE.write_text(token)

        # Set file permissions to read/write for owner only (Unix-like systems)
        try:
            os.chmod(self.TOKEN_FILE, 0o600)
        except Exception:
            # On Windows, this might not work, but that's okay
            pass

    def load_token(self) -> Optional[str]:
        """Load the JWT token from disk.

        Returns:
            The JWT token if it exists and is valid, None otherwise
        """
        if not self.TOKEN_FILE.exists():
            return None

        try:
            token = self.TOKEN_FILE.read_text().strip()

            # Validate the token before returning it
            if self.validate_token(token):
                return token
            else:
                # Token is invalid or expired, delete it
                self.delete_token()
                return None
        except Exception:
            return None

    def delete_token(self) -> None:
        """Delete the stored JWT token (logout)."""
        if self.TOKEN_FILE.exists():
            self.TOKEN_FILE.unlink()

    def get_current_user(self) -> Optional[User]:
        """Get the currently authenticated user from the stored token.

        Returns:
            User instance if authenticated, None otherwise
        """
        token = self.load_token()

        if not token:
            return None

        payload = self.validate_token(token)

        if not payload:
            return None

        # Get user from database
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
