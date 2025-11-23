"""
Tests unitaires pour le module permissions.py.

Ces tests vérifient le comportement du décorateur require_department
dans tous les scénarios possibles.
"""

import pytest
import typer

from src.cli.permissions import require_department
from src.models.user import Department, User


@pytest.fixture
def mock_auth_service(mocker):
    """Create a mock AuthService."""
    return mocker.Mock()


@pytest.fixture
def mock_container(mocker, mock_auth_service):
    """Create a mock Container with auth_service."""
    container = mocker.Mock()
    container.auth_service.return_value = mock_auth_service
    return container


@pytest.fixture
def commercial_user(db_session):
    """Create a real commercial user in database."""
    user = User(
        username="commercial1",
        email="commercial1@epicevents.com",
        first_name="Bob",
        last_name="Commercial",
        phone="+33122222222",
        department=Department.COMMERCIAL,
        password_hash="",
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def gestion_user(db_session):
    """Create a real gestion user in database."""
    user = User(
        username="admin",
        email="admin@epicevents.com",
        first_name="Alice",
        last_name="Gestion",
        phone="+33111111111",
        department=Department.GESTION,
        password_hash="",
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def support_user(db_session):
    """Create a real support user in database."""
    user = User(
        username="support1",
        email="support1@epicevents.com",
        first_name="Charlie",
        last_name="Support",
        phone="+33133333333",
        department=Department.SUPPORT,
        password_hash="",
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestRequireDepartmentAuthentication:
    """Test authentication requirements."""

    def test_unauthenticated_user_raises_exit(self, mocker, mock_container, mock_auth_service):
        """GIVEN unauthenticated user / WHEN calling decorated function / THEN raises typer.Exit"""
        # Arrange
        mocker.patch('src.containers.Container', return_value=mock_container)
        mock_auth_service.get_current_user.return_value = None

        @require_department(Department.COMMERCIAL)
        def test_command(current_user: User):
            return "success"

        # Act & Assert
        with pytest.raises(typer.Exit) as exc_info:
            test_command()

        assert exc_info.value.exit_code == 1
        mock_auth_service.get_current_user.assert_called_once()

    def test_authenticated_user_allowed(self, mocker, mock_container, mock_auth_service, commercial_user):
        """GIVEN authenticated user with correct dept / WHEN calling decorated function / THEN succeeds"""
        # Arrange
        mocker.patch('src.containers.Container', return_value=mock_container)
        mock_auth_service.get_current_user.return_value = commercial_user

        @require_department(Department.COMMERCIAL)
        def test_command(current_user: User):
            return f"success: {current_user.username}"

        # Act
        result = test_command()

        # Assert
        assert result == "success: commercial1"
        mock_auth_service.get_current_user.assert_called_once()


class TestRequireDepartmentPermissions:
    """Test department-based permissions."""

    def test_wrong_department_single_dept(self, mocker, mock_container, mock_auth_service, commercial_user):
        """GIVEN user from wrong dept / WHEN single dept required / THEN raises typer.Exit"""
        # Arrange
        mocker.patch('src.containers.Container', return_value=mock_container)
        mock_auth_service.get_current_user.return_value = commercial_user

        @require_department(Department.GESTION)  # Requires GESTION, user is COMMERCIAL
        def test_command(current_user: User):
            return "success"

        # Act & Assert
        with pytest.raises(typer.Exit) as exc_info:
            test_command()

        assert exc_info.value.exit_code == 1

    def test_wrong_department_multiple_depts(self, mocker, mock_container, mock_auth_service, support_user):
        """GIVEN user from wrong dept / WHEN multiple depts allowed / THEN raises typer.Exit"""
        # Arrange
        mocker.patch('src.containers.Container', return_value=mock_container)
        mock_auth_service.get_current_user.return_value = support_user

        @require_department(Department.COMMERCIAL, Department.GESTION)  # User is SUPPORT
        def test_command(current_user: User):
            return "success"

        # Act & Assert
        with pytest.raises(typer.Exit) as exc_info:
            test_command()

        assert exc_info.value.exit_code == 1

    def test_correct_department_multiple_depts_first(self, mocker, mock_container, mock_auth_service, commercial_user):
        """GIVEN user from allowed dept / WHEN multiple depts allowed / THEN succeeds"""
        # Arrange
        mocker.patch('src.containers.Container', return_value=mock_container)
        mock_auth_service.get_current_user.return_value = commercial_user

        @require_department(Department.COMMERCIAL, Department.GESTION)
        def test_command(current_user: User):
            return f"success: {current_user.department.value}"

        # Act
        result = test_command()

        # Assert
        assert result == "success: COMMERCIAL"

    def test_correct_department_multiple_depts_second(self, mocker, mock_container, mock_auth_service, gestion_user):
        """GIVEN user from 2nd allowed dept / WHEN multiple depts allowed / THEN succeeds"""
        # Arrange
        mocker.patch('src.containers.Container', return_value=mock_container)
        mock_auth_service.get_current_user.return_value = gestion_user

        @require_department(Department.COMMERCIAL, Department.GESTION)
        def test_command(current_user: User):
            return f"success: {current_user.department.value}"

        # Act
        result = test_command()

        # Assert
        assert result == "success: GESTION"


class TestRequireDepartmentNoRestriction:
    """Test decorator with no department restriction (auth only)."""

    def test_no_department_restriction_authenticated(self, mocker, mock_container, mock_auth_service, commercial_user):
        """GIVEN authenticated user / WHEN no dept restriction / THEN succeeds"""
        # Arrange
        mocker.patch('src.containers.Container', return_value=mock_container)
        mock_auth_service.get_current_user.return_value = commercial_user

        @require_department()  # No department restriction
        def test_command(current_user: User):
            return f"success: {current_user.username}"

        # Act
        result = test_command()

        # Assert
        assert result == "success: commercial1"

    def test_no_department_restriction_unauthenticated(self, mocker, mock_container, mock_auth_service):
        """GIVEN unauthenticated user / WHEN no dept restriction / THEN raises typer.Exit"""
        # Arrange
        mocker.patch('src.containers.Container', return_value=mock_container)
        mock_auth_service.get_current_user.return_value = None

        @require_department()  # No department restriction
        def test_command(current_user: User):
            return "success"

        # Act & Assert
        with pytest.raises(typer.Exit) as exc_info:
            test_command()

        assert exc_info.value.exit_code == 1


class TestRequireDepartmentCurrentUserInjection:
    """Test current_user parameter injection."""

    def test_function_without_current_user_param(self, mocker, mock_container, mock_auth_service, commercial_user):
        """GIVEN function without current_user param / WHEN decorated / THEN works without injection"""
        # Arrange
        mocker.patch('src.containers.Container', return_value=mock_container)
        mock_auth_service.get_current_user.return_value = commercial_user

        @require_department(Department.COMMERCIAL)
        def test_command():  # No current_user parameter
            return "success without user"

        # Act
        result = test_command()

        # Assert
        assert result == "success without user"

    def test_function_with_current_user_param(self, mocker, mock_container, mock_auth_service, commercial_user):
        """GIVEN function with current_user param / WHEN decorated / THEN injects user"""
        # Arrange
        mocker.patch('src.containers.Container', return_value=mock_container)
        mock_auth_service.get_current_user.return_value = commercial_user

        @require_department(Department.COMMERCIAL)
        def test_command(current_user: User):  # Has current_user parameter
            return f"user: {current_user.username}"

        # Act
        result = test_command()

        # Assert
        assert result == "user: commercial1"

    def test_function_with_args_and_current_user(self, mocker, mock_container, mock_auth_service, gestion_user):
        """GIVEN function with args and current_user / WHEN decorated / THEN preserves args and injects user"""
        # Arrange
        mocker.patch('src.containers.Container', return_value=mock_container)
        mock_auth_service.get_current_user.return_value = gestion_user

        @require_department(Department.GESTION)
        def test_command(name: str, age: int, current_user: User):
            return f"{name} ({age}) - {current_user.username}"

        # Act
        result = test_command("John", 30)

        # Assert
        assert result == "John (30) - admin"

    def test_function_with_kwargs_and_current_user(self, mocker, mock_container, mock_auth_service, support_user):
        """GIVEN function with kwargs and current_user / WHEN decorated / THEN preserves kwargs and injects user"""
        # Arrange
        mocker.patch('src.containers.Container', return_value=mock_container)
        mock_auth_service.get_current_user.return_value = support_user

        @require_department(Department.SUPPORT)
        def test_command(current_user: User, event_id: int = 1, notes: str = "default"):
            return f"Event {event_id}: {notes} by {current_user.username}"

        # Act
        result = test_command(event_id=42, notes="test note")

        # Assert
        assert result == "Event 42: test note by support1"


class TestRequireDepartmentAllDepartments:
    """Test with all three departments using parametrize."""

    @pytest.mark.parametrize(
        "user_fixture_name,expected_department",
        [
            ("commercial_user", "COMMERCIAL"),
            ("gestion_user", "GESTION"),
            ("support_user", "SUPPORT"),
        ],
        ids=["commercial", "gestion", "support"],
    )
    def test_all_departments_allowed(
        self, mocker, mock_container, mock_auth_service, user_fixture_name, expected_department, request
    ):
        """GIVEN user from any department / WHEN all departments allowed / THEN succeeds"""
        mocker.patch('src.containers.Container', return_value=mock_container)

        # Get the user fixture dynamically using request.getfixturevalue()
        user = request.getfixturevalue(user_fixture_name)
        mock_auth_service.get_current_user.return_value = user

        @require_department(Department.COMMERCIAL, Department.GESTION, Department.SUPPORT)
        def test_command(current_user: User):
            return current_user.department.value

        assert test_command() == expected_department
