"""Password hashing service for Epic Events CRM.

This module provides secure password hashing and verification functionality
using bcrypt, following the Single Responsibility Principle by separating
password management from the User model.
"""

import bcrypt


class PasswordHashingService:
    """Service for hashing and verifying passwords using bcrypt.

    This service encapsulates all password-related cryptographic operations,
    providing a secure and consistent interface for password management.

    Bcrypt is used as it is designed specifically for password hashing with:
    - Adaptive cost factor (work factor) to resist brute-force attacks
    - Automatic salt generation
    - Resistance to rainbow table attacks
    """

    def hash_password(self, password: str) -> str:
        """Hash a plain text password using bcrypt.

        Args:
            password: The plain text password to hash

        Returns:
            The hashed password as a UTF-8 string

        Example:
            >>> service = PasswordHashingService()
            >>> hashed = service.hash_password("my_password")
            >>> print(hashed)
            $2b$12$...
        """
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash using bcrypt.

        Args:
            password: The plain text password to verify
            password_hash: The hashed password to compare against

        Returns:
            True if the password matches the hash, False otherwise

        Example:
            >>> service = PasswordHashingService()
            >>> hashed = service.hash_password("my_password")
            >>> service.verify_password("my_password", hashed)
            True
            >>> service.verify_password("wrong_password", hashed)
            False
        """
        password_bytes = password.encode("utf-8")
        hash_bytes = password_hash.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)
