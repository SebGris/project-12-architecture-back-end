"""Token storage service for file-based token persistence.

This module handles token storage operations following the Single Responsibility
Principle (SRP). It focuses solely on reading/writing tokens to the filesystem.
"""

import os
from pathlib import Path
from typing import Optional


class TokenStorageService:
    """Service for token persistence on the filesystem.

    This service handles:
    - Saving tokens to disk
    - Loading tokens from disk
    - Deleting tokens (logout)
    """

    TOKEN_FILE = Path.home() / ".epicevents" / "token"

    def save(self, token: str) -> None:
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

    def load(self) -> Optional[str]:
        """Load the JWT token from disk.

        Returns:
            The JWT token string if file exists, None otherwise
        """
        if not self.TOKEN_FILE.exists():
            return None

        return self.TOKEN_FILE.read_text().strip()

    def delete(self) -> None:
        """Delete the stored JWT token (logout)."""
        self.TOKEN_FILE.unlink(missing_ok=True)

    def exists(self) -> bool:
        """Check if a token file exists.

        Returns:
            True if token file exists, False otherwise
        """
        return self.TOKEN_FILE.exists()
