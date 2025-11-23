"""CLI commands for Epic Events CRM."""

import typer

from .auth_commands import app as auth_app
from .client_commands import app as client_app
from .contract_commands import app as contract_app
from .event_commands import app as event_app
from .user_commands import app as user_app

# Main app that aggregates all command modules
app = typer.Typer()

# Mount sub-applications
# No 'name' parameter = commands are added directly to root level
# This allows: epicevents login, epicevents create-client, etc.
# Instead of: epicevents auth login, epicevents client create-client
app.add_typer(auth_app)
app.add_typer(client_app)
app.add_typer(contract_app)
app.add_typer(event_app)
app.add_typer(user_app)
