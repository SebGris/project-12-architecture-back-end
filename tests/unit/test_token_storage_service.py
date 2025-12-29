"""Unit tests for TokenStorageService.

Tests covered:
- save(): Token persistence to file with proper permissions
- load(): Token retrieval from file
- delete(): Token file deletion
- exists(): Token file existence check

Implementation notes:
- Uses temporary directory to avoid modifying real token file
- Tests file operations directly without mocks
"""

import pytest
from pathlib import Path

from src.services.token_storage_service import TokenStorageService


@pytest.fixture
def token_storage(tmp_path, monkeypatch):
    """Create a TokenStorageService with a temporary token file path."""
    service = TokenStorageService()
    # Override TOKEN_FILE to use temp directory
    temp_token_file = tmp_path / ".epicevents" / "token"
    monkeypatch.setattr(TokenStorageService, "TOKEN_FILE", temp_token_file)
    return service


@pytest.fixture
def temp_token_file(tmp_path, monkeypatch):
    """Return the temporary token file path."""
    temp_token_file = tmp_path / ".epicevents" / "token"
    monkeypatch.setattr(TokenStorageService, "TOKEN_FILE", temp_token_file)
    return temp_token_file


class TestSaveToken:
    """Test save method."""

    def test_save_creates_directory_and_file(self, token_storage, temp_token_file):
        """GIVEN no existing token / WHEN save() / THEN creates directory and file"""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"

        token_storage.save(token)

        assert temp_token_file.parent.exists()
        assert temp_token_file.exists()
        assert temp_token_file.read_text() == token

    def test_save_overwrites_existing_token(self, token_storage, temp_token_file):
        """GIVEN existing token / WHEN save() with new token / THEN overwrites"""
        old_token = "old_token"
        new_token = "new_token"

        token_storage.save(old_token)
        token_storage.save(new_token)

        assert temp_token_file.read_text() == new_token

    def test_save_empty_token(self, token_storage, temp_token_file):
        """GIVEN empty string / WHEN save() / THEN saves empty file"""
        token_storage.save("")

        assert temp_token_file.exists()
        assert temp_token_file.read_text() == ""


class TestLoadToken:
    """Test load method."""

    def test_load_existing_token(self, token_storage, temp_token_file):
        """GIVEN existing token file / WHEN load() / THEN returns token"""
        expected_token = "test.jwt.token"
        temp_token_file.parent.mkdir(parents=True, exist_ok=True)
        temp_token_file.write_text(expected_token)

        result = token_storage.load()

        assert result == expected_token

    def test_load_nonexistent_file(self, token_storage):
        """GIVEN no token file / WHEN load() / THEN returns None"""
        result = token_storage.load()

        assert result is None

    def test_load_strips_whitespace(self, token_storage, temp_token_file):
        """GIVEN token with whitespace / WHEN load() / THEN strips whitespace"""
        temp_token_file.parent.mkdir(parents=True, exist_ok=True)
        temp_token_file.write_text("  token_with_whitespace  \n")

        result = token_storage.load()

        assert result == "token_with_whitespace"


class TestDeleteToken:
    """Test delete method."""

    def test_delete_existing_token(self, token_storage, temp_token_file):
        """GIVEN existing token file / WHEN delete() / THEN file is removed"""
        temp_token_file.parent.mkdir(parents=True, exist_ok=True)
        temp_token_file.write_text("token_to_delete")
        assert temp_token_file.exists()

        token_storage.delete()

        assert not temp_token_file.exists()

    def test_delete_nonexistent_file(self, token_storage, temp_token_file):
        """GIVEN no token file / WHEN delete() / THEN no error raised"""
        assert not temp_token_file.exists()

        # Should not raise an exception
        token_storage.delete()

        assert not temp_token_file.exists()


class TestExistsToken:
    """Test exists method."""

    def test_exists_returns_true_when_file_exists(
        self, token_storage, temp_token_file
    ):
        """GIVEN existing token file / WHEN exists() / THEN returns True"""
        temp_token_file.parent.mkdir(parents=True, exist_ok=True)
        temp_token_file.write_text("some_token")

        result = token_storage.exists()

        assert result is True

    def test_exists_returns_false_when_no_file(self, token_storage):
        """GIVEN no token file / WHEN exists() / THEN returns False"""
        result = token_storage.exists()

        assert result is False


class TestTokenStorageIntegration:
    """Integration tests for full token lifecycle."""

    def test_save_load_delete_cycle(self, token_storage, temp_token_file):
        """GIVEN token storage / WHEN save-load-delete cycle / THEN works correctly"""
        token = "full.lifecycle.token"

        # Initially no token
        assert not token_storage.exists()
        assert token_storage.load() is None

        # Save token
        token_storage.save(token)
        assert token_storage.exists()
        assert token_storage.load() == token

        # Delete token
        token_storage.delete()
        assert not token_storage.exists()
        assert token_storage.load() is None
