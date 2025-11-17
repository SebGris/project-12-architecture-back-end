"""
Tests unitaires pour les commandes d'authentification CLI.

Tests couverts:
- whoami sans authentification (doit échouer)
- login avec credentials valides (doit réussir)
- Sauvegarde du token JWT dans le fichier
- whoami avec authentification (doit afficher les infos)
- logout (doit supprimer le token)
- login avec credentials invalides (doit échouer)
"""

import os

import pytest
from typer.testing import CliRunner

from src.cli.commands import app
from src.models.user import Department

runner = CliRunner()


@pytest.fixture
def mock_user(mocker):
    """Create a mock user for testing."""
    user = mocker.Mock()
    user.id = 1
    user.username = "admin"
    user.email = "admin@epicevents.com"
    user.first_name = "Alice"
    user.last_name = "Dubois"
    user.phone = "+33 1 23 45 67 89"
    user.department = Department.GESTION
    return user


@pytest.fixture
def mock_token_file(tmp_path):
    """Create a temporary token file for testing."""
    token_dir = tmp_path / ".epicevents"
    token_dir.mkdir(exist_ok=True)
    token_file = token_dir / "token"
    return token_file


class TestWhoamiWithoutAuthentication:
    """Test whoami command when user is not authenticated."""

    def test_whoami_without_authentication(self, mocker):
        """
        GIVEN no authenticated user
        WHEN whoami command is executed
        THEN it should display an error message and exit with code 1
        """
        mock_container = mocker.patch("src.cli.commands.Container")
        # Mock auth_service to return None (no user authenticated)
        mock_auth_service = mocker.MagicMock()
        mock_auth_service.get_current_user.return_value = None
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute whoami command
        result = runner.invoke(app, ["whoami"])

        # Verify exit code and error message
        assert result.exit_code == 1
        assert "Vous n'êtes pas connecté" in result.stdout
        assert "epicevents login" in result.stdout


class TestLoginCommand:
    """Test login command with valid and invalid credentials."""

    def test_login_with_valid_credentials(
        self, mocker, mock_user, mock_token_file
    ):
        """
        GIVEN valid username and password
        WHEN login command is executed
        THEN it should authenticate, generate token, and save it
        """
        mock_container = mocker.patch("src.cli.commands.Container")
        # Mock auth_service
        mock_auth_service = mocker.MagicMock()
        mock_auth_service.authenticate.return_value = mock_user
        mock_auth_service.generate_token.return_value = "fake.jwt.token"
        mock_auth_service.TOKEN_FILE = mock_token_file

        # Mock save_token to write to our test file
        def save_token_mock(token):
            mock_token_file.write_text(token)

        mock_auth_service.save_token.side_effect = save_token_mock
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Mock Sentry
        mocker.patch("src.sentry_config.set_user_context")

        # Execute login command
        result = runner.invoke(app, ["login"], input="admin\nAdmin123!\n")

        # Verify authentication was called
        mock_auth_service.authenticate.assert_called_once_with(
            "admin", "Admin123!"
        )

        # Verify token generation
        mock_auth_service.generate_token.assert_called_once_with(mock_user)

        # Verify token was saved
        mock_auth_service.save_token.assert_called_once_with("fake.jwt.token")

        # Verify success message
        assert result.exit_code == 0
        assert "Bienvenue Alice Dubois" in result.stdout
        assert "GESTION" in result.stdout
        assert "Valide pour 24 heures" in result.stdout

    def test_login_with_invalid_credentials(self, mocker):
        """
        GIVEN invalid username or password
        WHEN login command is executed
        THEN it should display an error and exit with code 1
        """
        mock_container = mocker.patch("src.cli.commands.Container")
        # Mock auth_service to return None (authentication failed)
        mock_auth_service = mocker.MagicMock()
        mock_auth_service.authenticate.return_value = None
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute login command with wrong credentials
        result = runner.invoke(
            app, ["login"], input="admin\nWrongPassword123!\n"
        )

        # Verify exit code and error message
        assert result.exit_code == 1
        assert "Nom d'utilisateur ou mot de passe incorrect" in result.stdout


class TestTokenStorage:
    """Test JWT token storage in file system."""

    def test_token_saved_to_file(self, mocker, mock_user, mock_token_file):
        """
        GIVEN a successful login
        WHEN token is saved
        THEN the token file should exist and contain the JWT token
        """
        mock_container = mocker.patch("src.cli.commands.Container")
        # Mock auth_service
        mock_auth_service = mocker.MagicMock()
        mock_auth_service.authenticate.return_value = mock_user
        mock_auth_service.generate_token.return_value = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.fake_signature"
        )
        mock_auth_service.TOKEN_FILE = mock_token_file

        # Mock save_token to write to our test file
        def save_token_mock(token):
            mock_token_file.write_text(token)
            # On Unix systems, set permissions to 600
            try:
                os.chmod(mock_token_file, 0o600)
            except Exception:
                pass  # Windows compatibility

        mock_auth_service.save_token.side_effect = save_token_mock
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Mock Sentry
        mocker.patch("src.sentry_config.set_user_context")

        # Execute login
        result = runner.invoke(app, ["login"], input="admin\nAdmin123!\n")

        # Verify file exists
        assert mock_token_file.exists()

        # Verify token content
        token_content = mock_token_file.read_text()
        assert (
            token_content
            == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.fake_signature"
        )


class TestWhoamiWithAuthentication:
    """Test whoami command when user is authenticated."""

    def test_whoami_with_authentication(self, mocker, mock_user):
        """
        GIVEN an authenticated user
        WHEN whoami command is executed
        THEN it should display user information
        """
        mock_container = mocker.patch("src.cli.commands.Container")
        # Mock auth_service to return authenticated user
        mock_auth_service = mocker.MagicMock()
        mock_auth_service.get_current_user.return_value = mock_user
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute whoami command
        result = runner.invoke(app, ["whoami"])

        # Verify success
        assert result.exit_code == 0

        # Verify user information is displayed
        assert "admin" in result.stdout
        assert "Alice Dubois" in result.stdout
        assert "admin@epicevents.com" in result.stdout
        assert "GESTION" in result.stdout


class TestLogoutCommand:
    """Test logout command and token deletion."""

    def test_logout_deletes_token(self, mocker, mock_user, mock_token_file):
        """
        GIVEN an authenticated user with a token file
        WHEN logout command is executed
        THEN the token file should be deleted
        """
        # Create a fake token file
        mock_token_file.write_text("fake.jwt.token")
        assert mock_token_file.exists()

        mock_container = mocker.patch("src.cli.commands.Container")
        # Mock auth_service
        mock_auth_service = mocker.MagicMock()
        mock_auth_service.get_current_user.return_value = mock_user
        mock_auth_service.TOKEN_FILE = mock_token_file

        # Mock delete_token to remove our test file
        def delete_token_mock():
            if mock_token_file.exists():
                mock_token_file.unlink()

        mock_auth_service.delete_token.side_effect = delete_token_mock
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Mock Sentry
        mocker.patch("src.sentry_config.clear_user_context")
        mocker.patch("src.sentry_config.add_breadcrumb")

        # Execute logout
        result = runner.invoke(app, ["logout"])

        # Verify success
        assert result.exit_code == 0
        assert "Au revoir Alice Dubois" in result.stdout

        # Verify token was deleted
        mock_auth_service.delete_token.assert_called_once()

        # Verify file no longer exists
        assert not mock_token_file.exists()

    def test_logout_without_authentication(self, mocker):
        """
        GIVEN no authenticated user
        WHEN logout command is executed
        THEN it should display an error message
        """
        mock_container = mocker.patch("src.cli.commands.Container")
        # Mock auth_service to return None (no user)
        mock_auth_service = mocker.MagicMock()
        mock_auth_service.get_current_user.return_value = None
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Execute logout
        result = runner.invoke(app, ["logout"])

        # Verify error
        assert result.exit_code == 1
        assert "Vous n'êtes pas connecté" in result.stdout


class TestAuthenticationFlow:
    """Test complete authentication flow (login -> whoami -> logout)."""

    def test_complete_authentication_flow(
        self, mocker, mock_user, mock_token_file
    ):
        """
        GIVEN a user going through complete auth flow
        WHEN login, whoami, then logout are executed
        THEN each command should work correctly in sequence
        """
        mock_container = mocker.patch("src.cli.commands.Container")
        # Mock auth_service
        mock_auth_service = mocker.MagicMock()
        mock_auth_service.TOKEN_FILE = mock_token_file

        # Helper functions for token operations
        def save_token_mock(token):
            mock_token_file.write_text(token)

        def delete_token_mock():
            if mock_token_file.exists():
                mock_token_file.unlink()

        mock_auth_service.save_token.side_effect = save_token_mock
        mock_auth_service.delete_token.side_effect = delete_token_mock
        mock_container.return_value.auth_service.return_value = mock_auth_service

        # Mock Sentry
        mocker.patch("src.sentry_config.set_user_context")
        mocker.patch("src.sentry_config.clear_user_context")
        mocker.patch("src.sentry_config.add_breadcrumb")

        # Step 1: Login
        mock_auth_service.authenticate.return_value = mock_user
        mock_auth_service.generate_token.return_value = "fake.jwt.token"

        result = runner.invoke(app, ["login"], input="admin\nAdmin123!\n")
        assert result.exit_code == 0
        assert mock_token_file.exists()

        # Step 2: Whoami (authenticated)
        mock_auth_service.get_current_user.return_value = mock_user

        result = runner.invoke(app, ["whoami"])
        assert result.exit_code == 0
        assert "Alice Dubois" in result.stdout

        # Step 3: Logout
        result = runner.invoke(app, ["logout"])
        assert result.exit_code == 0
        assert not mock_token_file.exists()
