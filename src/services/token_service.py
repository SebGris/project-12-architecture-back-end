"""Token service for JWT generation and validation.

This module handles JWT token operations following the Single Responsibility
Principle (SRP). It focuses solely on token creation and validation.
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from dotenv import load_dotenv

from src.models.user import User

# Load environment variables from .env file
load_dotenv()


class TokenService:
    """Service for JWT token generation and validation.

    This service handles:
    - JWT token generation from user data
    - JWT token validation and payload extraction
    - Secret key management
    """

    # JWT Configuration
    TOKEN_EXPIRATION_HOURS = 24
    ALGORITHM = "HS256"

    def __init__(self) -> None:
        """Initialize the token service."""
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
            secret_key = secrets.token_hex(32)  # 256 bits

        return secret_key

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
        now = datetime.now(timezone.utc)
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
                token, self._secret_key, algorithms=[self.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Token is invalid
            return None
