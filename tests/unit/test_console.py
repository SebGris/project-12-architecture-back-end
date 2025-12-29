"""Unit tests for console.py output functions."""

import pytest

from src.cli.console import (
    print_success,
    print_error,
    print_info,
    print_warning,
    print_header,
    print_field,
    print_separator,
    print_command_header,
)


@pytest.fixture
def mock_console(mocker):
    """Mock the console.print method."""
    return mocker.patch("src.cli.console.console")


class TestPrintFunctions:
    """Test console print functions."""

    @pytest.mark.parametrize(
        "func,message,expected_prefix",
        [
            (
                print_success,
                "Test message",
                "[bold green][SUCCES][/bold green]",
            ),
            (print_error, "Test message", "[bold red][ERREUR][/bold red]"),
            (print_info, "Test message", "[bold blue][INFO][/bold blue]"),
            (
                print_warning,
                "Test message",
                "[bold yellow][ATTENTION][/bold yellow]",
            ),
        ],
        ids=["success", "error", "info", "warning"],
    )
    def test_print_functions(
        self, mock_console, func, message, expected_prefix
    ):
        """Test print functions output correct format."""
        func(message)

        mock_console.print.assert_called_once()
        call_arg = mock_console.print.call_args[0][0]
        assert expected_prefix in call_arg
        assert message in call_arg


class TestPrintHeader:
    """Test print_header function."""

    def test_print_header_creates_panel(self, mock_console):
        """GIVEN a title / WHEN print_header() / THEN prints Panel with title."""
        print_header("Test Title")

        mock_console.print.assert_called_once()
        call_arg = mock_console.print.call_args[0][0]
        # Panel object should be passed
        from rich.panel import Panel

        assert isinstance(call_arg, Panel)


class TestPrintField:
    """Test print_field function."""

    def test_print_field_default_color(self, mock_console):
        """GIVEN label and value / WHEN print_field() / THEN prints formatted field."""
        print_field("Label", "Value")

        mock_console.print.assert_called_once()
        call_arg = mock_console.print.call_args[0][0]
        assert "[cyan]Label:[/cyan]" in call_arg
        assert "Value" in call_arg

    def test_print_field_custom_color(self, mock_console):
        """GIVEN custom color / WHEN print_field() / THEN uses custom color."""
        print_field("Label", "Value", label_color="green")

        call_arg = mock_console.print.call_args[0][0]
        assert "[green]Label:[/green]" in call_arg


class TestPrintSeparator:
    """Test print_separator function."""

    def test_print_separator(self, mock_console):
        """GIVEN nothing / WHEN print_separator() / THEN prints empty line."""
        print_separator()

        mock_console.print.assert_called_once_with()


class TestPrintCommandHeader:
    """Test print_command_header function."""

    def test_print_command_header(self, mock_console):
        """GIVEN title / WHEN print_command_header() / THEN prints with separators."""
        print_command_header("Command Title")

        # Should call print 3 times: separator, header, separator
        assert mock_console.print.call_count == 3
