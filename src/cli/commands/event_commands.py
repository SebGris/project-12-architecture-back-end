from datetime import datetime

import typer

from src.cli import console
from src.cli import validators
from src.cli import constants as c
from src.models.user import Department
from src.containers import Container
from src.cli.permissions import require_department

app = typer.Typer()

# Event-specific constants
LABEL_SUPPORT_CONTACT = "Support contact"
LABEL_EVENT_ID = "Event ID"
LABEL_CONTRACT_ID = "Contract ID"
LABEL_CLIENT_NAME = "Client name"
LABEL_CLIENT_CONTACT = "Client contact"
LABEL_EVENT_DATE_START = "Event date start"
LABEL_EVENT_DATE_END = "Event date end"
LABEL_LOCATION = "Location"
LABEL_ATTENDEES = "Attendees"
LABEL_NOTES = "Notes"
LABEL_NON_ASSIGNE = "Non assigné"
PROMPT_ID_CONTRAT = "ID du contrat"


def format_event_datetime(dt: datetime) -> str:
    """Format datetime for event display (e.g., '4 Jun 2023 @ 1PM')."""
    # Get hour in 12-hour format and remove leading zero
    hour_12 = dt.strftime("%I").lstrip("0") or "12"
    # Get AM/PM
    am_pm = dt.strftime("%p")
    # Get date part
    date_part = dt.strftime("%d %b %Y")
    # Remove leading zero from day if present
    if date_part.startswith("0"):
        date_part = date_part[1:]
    return f"{date_part} @ {hour_12}{am_pm}"


@app.command()
@require_department(Department.COMMERCIAL, Department.GESTION)
def create_event(
    name: str = typer.Option(
        ...,
        prompt="Nom de l'événement",
        callback=validators.validate_event_name_callback,
    ),
    contract_id: int = typer.Option(
        ...,
        prompt=PROMPT_ID_CONTRAT,
        callback=validators.validate_contract_id_callback,
    ),
    event_start: str = typer.Option(
        ..., prompt="Date et heure de début (YYYY-MM-DD HH:MM)"
    ),
    event_end: str = typer.Option(
        ..., prompt="Date et heure de fin (YYYY-MM-DD HH:MM)"
    ),
    location: str = typer.Option(
        ..., prompt="Lieu", callback=validators.validate_location_callback
    ),
    attendees: int = typer.Option(
        ...,
        prompt="Nombre de participants",
        callback=validators.validate_attendees_callback,
    ),
    notes: str = typer.Option("", prompt="Notes (optionnel)"),
    support_contact_id: int = typer.Option(
        0, prompt="ID du contact support (0 si aucun)"
    ),
    current_user=None,
):
    """Create a new event in the CRM system.

    This command registers a new event associated with an existing contract,
    with details about the date, location and number of attendees.

    Args:
        name: Event name (minimum 3 characters)
        contract_id: Associated contract ID (must exist in database)
        event_start: Start date and time (format: YYYY-MM-DD HH:MM)
        event_end: End date and time (format: YYYY-MM-DD HH:MM)
        location: Event location
        attendees: Expected number of attendees (>= 0)
        notes: Optional notes about the event
        support_contact_id: Optional support contact ID (SUPPORT user)

    Returns:
        None. Displays success message with created event details.

    Raises:
        typer.Exit: On error (non-existent contract, invalid dates, etc.)

    Examples:
        epicevents create-event
        # Follow interactive prompts to enter information
    """
    # Manually get services from container
    container = Container()
    event_service = container.event_service()
    contract_service = container.contract_service()
    user_service = container.user_service()

    # Show header at the beginning
    console.print_command_header("Création d'un nouvel événement")

    # Business validation: check if contract exists
    contract = contract_service.get_contract(contract_id)

    if not contract:
        console.print_error(f"Contrat avec l'ID {contract_id} n'existe pas")
        raise typer.Exit(code=1)

    # Business validation: check if contract is signed
    if not contract.is_signed:
        console.print_error(
            f"Le contrat #{contract_id} n'est pas encore signé. "
            "Seuls les contrats signés peuvent avoir des événements."
        )
        raise typer.Exit(code=1)

    # Permission check: COMMERCIAL can only create events for their own clients
    if current_user.department == Department.COMMERCIAL:
        if contract.client.sales_contact_id != current_user.id:
            console.print_error(
                "Vous ne pouvez créer des événements que pour vos propres clients"
            )
            console.print_error(
                f"Ce contrat appartient au client {contract.client.first_name} {contract.client.last_name}, "
                f"assigné à {contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name}"
            )
            raise typer.Exit(code=1)

    # Parse datetime strings
    try:
        start_dt = datetime.strptime(event_start, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(event_end, "%Y-%m-%d %H:%M")
    except ValueError:
        console.print_error(
            "Format de date invalide. Utilisez le format: YYYY-MM-DD HH:MM"
        )
        raise typer.Exit(code=1)

    # Business validation: validate event dates and attendees
    try:
        validators.validate_event_dates(start_dt, end_dt, attendees)
    except ValueError as e:
        console.print_error(str(e))
        raise typer.Exit(code=1)

    # Business validation: check if support contact exists and is from SUPPORT dept
    support_id = support_contact_id if support_contact_id > 0 else None
    if support_id:
        user = user_service.get_user(support_id)
        if not user:
            console.print_error(
                f"Utilisateur avec l'ID {support_id} n'existe pas"
            )
            raise typer.Exit(code=1)
        try:
            validators.validate_user_is_support(user)
        except ValueError as e:
            console.print_error(str(e))
            raise typer.Exit(code=1)

    try:
        # Create event via service
        event = event_service.create_event(
            name=name,
            contract_id=contract_id,
            event_start=start_dt,
            event_end=end_dt,
            location=location,
            attendees=attendees,
            notes=notes if notes else None,
            support_contact_id=support_id,
        )

    except ValueError as e:
        console.print_error(str(e))
        raise typer.Exit(code=1)

    except Exception as e:
        console.print_error(c.ERROR_UNEXPECTED.format(e=e))
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success(f"Événement '{event.name}' créé avec succès!")
    console.print_field(LABEL_EVENT_ID, str(event.id))
    console.print_field(LABEL_CONTRACT_ID, str(contract.id))
    console.print_field(
        LABEL_CLIENT_NAME,
        f"{contract.client.first_name} {contract.client.last_name}",
    )
    console.print_field(
        LABEL_CLIENT_CONTACT,
        f"{contract.client.email}\n{contract.client.phone}",
    )
    console.print_field(
        LABEL_EVENT_DATE_START, format_event_datetime(event.event_start)
    )
    console.print_field(
        LABEL_EVENT_DATE_END, format_event_datetime(event.event_end)
    )
    if event.support_contact:
        console.print_field(
            LABEL_SUPPORT_CONTACT,
            f"{event.support_contact.first_name} {event.support_contact.last_name} (ID: {event.support_contact_id})",
        )
    else:
        console.print_field(LABEL_SUPPORT_CONTACT, LABEL_NON_ASSIGNE)
    console.print_field(LABEL_LOCATION, event.location)
    console.print_field(LABEL_ATTENDEES, str(event.attendees))
    if event.notes:
        console.print_field(LABEL_NOTES, event.notes)
    console.print_separator()


@app.command()
@require_department(Department.GESTION, Department.SUPPORT)
def update_event(
    event_id: int = typer.Option(
        ...,
        prompt="ID de l'événement",
        callback=validators.validate_event_id_callback,
    ),
    name: str = typer.Option(
        "", prompt="Nouveau nom (laisser vide pour ne pas modifier)"
    ),
    event_start: str = typer.Option(
        "",
        prompt="Nouvelle date de début YYYY-MM-DD HH:MM (laisser vide pour ne pas modifier)",
    ),
    event_end: str = typer.Option(
        "",
        prompt="Nouvelle date de fin YYYY-MM-DD HH:MM (laisser vide pour ne pas modifier)",
    ),
    location: str = typer.Option(
        "", prompt="Nouveau lieu (laisser vide pour ne pas modifier)"
    ),
    attendees: int = typer.Option(
        -1,
        prompt="Nouveau nombre de participants (-1 pour ne pas modifier)",
    ),
    notes: str = typer.Option(
        "", prompt="Nouvelles notes (laisser vide pour ne pas modifier)"
    ),
    current_user=None,
):
    """Update event information.

    This command modifies multiple fields of an existing event.
    Fields left empty will not be modified.

    Args:
        event_id: ID of the event to modify
        name: New event name (optional)
        event_start: New start date/time (optional)
        event_end: New end date/time (optional)
        location: New location (optional)
        attendees: New number of attendees (optional)
        notes: New notes (optional)

    Returns:
        None. Displays success message with updated details.

    Raises:
        typer.Exit: On error (non-existent event, invalid dates, etc.)

    Examples:
        epicevents update-event
    """
    # Manually get services from container
    container = Container()
    event_service = container.event_service()

    console.print_command_header("Mise à jour d'un événement")

    # Vérifier que l'événement existe
    event = event_service.get_event(event_id)
    if not event:
        console.print_error(f"Événement avec l'ID {event_id} n'existe pas")
        raise typer.Exit(code=1)

    # Permission check: SUPPORT can only update their own events
    if current_user.department == Department.SUPPORT:
        if (
            not event.support_contact_id
            or event.support_contact_id != current_user.id
        ):
            console.print_error(
                "Vous ne pouvez modifier que vos propres événements"
            )
            if event.support_contact:
                console.print_error(
                    f"Cet événement est assigné à {event.support_contact.first_name} {event.support_contact.last_name}"
                )
            else:
                console.print_error(
                    "Cet événement n'a pas encore de contact support assigné"
                )
            raise typer.Exit(code=1)

    # Nettoyer les champs vides
    name = name.strip() if name else None
    event_start_str = event_start.strip() if event_start else None
    event_end_str = event_end.strip() if event_end else None
    location = location.strip() if location else None
    attendees_value = attendees if attendees >= 0 else None
    notes = notes.strip() if notes else None

    # Parse datetime strings
    start_dt = None
    end_dt = None

    if event_start_str:
        try:
            start_dt = datetime.strptime(event_start_str, "%Y-%m-%d %H:%M")
        except ValueError:
            console.print_error(
                "Format de date de début invalide. Utilisez: YYYY-MM-DD HH:MM"
            )
            raise typer.Exit(code=1)

    if event_end_str:
        try:
            end_dt = datetime.strptime(event_end_str, "%Y-%m-%d %H:%M")
        except ValueError:
            console.print_error(
                "Format de date de fin invalide. Utilisez: YYYY-MM-DD HH:MM"
            )
            raise typer.Exit(code=1)

    # Validation des champs si fournis
    if name and len(name) < 3:
        console.print_error("Le nom doit avoir au moins 3 caractères")
        raise typer.Exit(code=1)

    if location and len(location) < 3:
        console.print_error("Le lieu doit avoir au moins 3 caractères")
        raise typer.Exit(code=1)

    if attendees_value and attendees_value < 0:
        console.print_error("Le nombre de participants doit être positif")
        raise typer.Exit(code=1)

    # Validate event dates if both are provided
    if start_dt and end_dt:
        try:
            validators.validate_event_dates(start_dt, end_dt, attendees_value or 0)
        except ValueError as e:
            console.print_error(str(e))
            raise typer.Exit(code=1)
    elif start_dt and not end_dt:
        # Check that new start is before existing end
        if start_dt >= event.event_end:
            console.print_error(
                "La date de début doit être antérieure à la date de fin"
            )
            raise typer.Exit(code=1)
    elif end_dt and not start_dt:
        # Check that new end is after existing start
        if end_dt <= event.event_start:
            console.print_error(
                "La date de fin doit être postérieure à la date de début"
            )
            raise typer.Exit(code=1)

    try:
        # Mettre à jour l'événement
        updated_event = event_service.update_event(
            event_id=event_id,
            name=name,
            event_start=start_dt,
            event_end=end_dt,
            location=location,
            attendees=attendees_value,
            notes=notes,
        )

        if not updated_event:
            console.print_error(f"Événement avec l'ID {event_id} n'existe pas")
            raise typer.Exit(code=1)

    except Exception as e:
        console.print_error(f"Erreur lors de la mise à jour: {e}")
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success("Événement mis à jour avec succès!")
    console.print_field(c.LABEL_ID, str(updated_event.id))
    console.print_field("Nom de l'événement", updated_event.name)
    console.print_field("Contrat ID", str(updated_event.contract_id))
    console.print_field(
        LABEL_CLIENT_NAME,
        f"{updated_event.contract.client.first_name} {updated_event.contract.client.last_name}",
    )
    console.print_field(
        "Début", format_event_datetime(updated_event.event_start)
    )
    console.print_field("Fin", format_event_datetime(updated_event.event_end))
    console.print_field("Lieu", updated_event.location)
    console.print_field("Nombre de participants", str(updated_event.attendees))
    if updated_event.support_contact:
        console.print_field(
            LABEL_SUPPORT_CONTACT,
            f"{updated_event.support_contact.first_name} {updated_event.support_contact.last_name} (ID: {updated_event.support_contact_id})",
        )
    else:
        console.print_field(LABEL_SUPPORT_CONTACT, LABEL_NON_ASSIGNE)
    if updated_event.notes:
        console.print_field(LABEL_NOTES, updated_event.notes)
    console.print_field(
        "Dernière mise à jour",
        updated_event.updated_at.strftime(c.FORMAT_DATETIME),
    )
    console.print_separator()


@app.command()
@require_department(Department.GESTION)
def assign_support(
    event_id: int = typer.Option(
        ...,
        prompt="ID de l'événement",
        callback=validators.validate_event_id_callback,
    ),
    support_contact_id: int = typer.Option(
        ...,
        prompt="ID du contact support",
        callback=validators.validate_user_id_callback,
    ),
):
    """Assign a support contact to an event.

    This command assigns or reassigns a SUPPORT department user
    to an existing event.

    Args:
        event_id: Event ID
        support_contact_id: SUPPORT user ID to assign

    Returns:
        None. Displays success message with details.

    Raises:
        typer.Exit: On error (non-existent event, non-SUPPORT user, etc.)

    Examples:
        epicevents assign-support
    """
    # Manually get services from container
    container = Container()
    event_service = container.event_service()
    user_service = container.user_service()

    console.print_command_header("Assignation d'un contact support")

    # Vérifier que l'événement existe
    event = event_service.get_event(event_id)
    if not event:
        console.print_error(f"Événement avec l'ID {event_id} n'existe pas")
        raise typer.Exit(code=1)

    # Vérifier que l'utilisateur existe et est du département SUPPORT
    user = user_service.get_user(support_contact_id)
    if not user:
        console.print_error(
            f"Utilisateur avec l'ID {support_contact_id} n'existe pas"
        )
        raise typer.Exit(code=1)

    try:
        validators.validate_user_is_support(user)
    except ValueError as e:
        console.print_error(str(e))
        raise typer.Exit(code=1)

    # Assigner le contact support
    try:
        updated_event = event_service.assign_support_contact(
            event_id, support_contact_id
        )
    except Exception as e:
        console.print_error(f"Erreur lors de l'assignation: {e}")
        raise typer.Exit(code=1)

    # Success message
    console.print_separator()
    console.print_success(
        f"Contact support assigné avec succès à l'événement '{updated_event.name}'!"
    )
    console.print_field(LABEL_EVENT_ID, str(updated_event.id))
    console.print_field(LABEL_CONTRACT_ID, str(updated_event.contract_id))
    console.print_field(
        LABEL_CLIENT_NAME,
        f"{updated_event.contract.client.first_name} {updated_event.contract.client.last_name}",
    )
    console.print_field(
        LABEL_CLIENT_CONTACT,
        f"{updated_event.contract.client.email}\n{updated_event.contract.client.phone}",
    )
    console.print_field(
        "Event date start", format_event_datetime(updated_event.event_start)
    )
    console.print_field(
        LABEL_EVENT_DATE_END, format_event_datetime(updated_event.event_end)
    )
    console.print_field(
        "Support contact",
        f"{user.first_name} {user.last_name} (ID: {user.id})",
    )
    console.print_field(LABEL_LOCATION, updated_event.location)
    console.print_field(LABEL_ATTENDEES, str(updated_event.attendees))
    if updated_event.notes:
        console.print_field(LABEL_NOTES, updated_event.notes)
    console.print_separator()


@app.command()
@require_department()
def filter_unassigned_events():
    """Display all events without assigned support contact.

    This command lists all events that do not yet have a support contact.

    Returns:
        None. Displays the list of unassigned events.

    Examples:
        epicevents filter-unassigned-events
    """
    # Manually get services from container
    container = Container()
    event_service = container.event_service()

    console.print_command_header("Événements sans contact support")

    events = event_service.get_unassigned_events()

    if not events:
        console.print_success("Aucun événement sans contact support")
        return

    for event in events:
        console.print_field(LABEL_EVENT_ID, str(event.id))
        console.print_field(LABEL_CONTRACT_ID, str(event.contract_id))
        console.print_field(
            LABEL_CLIENT_NAME,
            f"{event.contract.client.first_name} {event.contract.client.last_name}",
        )
        console.print_field(
            LABEL_CLIENT_CONTACT,
            f"{event.contract.client.email}\n{event.contract.client.phone}",
        )
        console.print_field(
            LABEL_EVENT_DATE_START, format_event_datetime(event.event_start)
        )
        console.print_field(
            LABEL_EVENT_DATE_END, format_event_datetime(event.event_end)
        )
        console.print_field(LABEL_SUPPORT_CONTACT, LABEL_NON_ASSIGNE)
        console.print_field(LABEL_LOCATION, event.location)
        console.print_field(LABEL_ATTENDEES, str(event.attendees))
        if event.notes:
            console.print_field(LABEL_NOTES, event.notes)
        console.print_separator()

    console.print_success(
        f"Total: {len(events)} événement(s) sans contact support"
    )


@app.command()
@require_department(Department.SUPPORT)
def filter_my_events(current_user=None):
    """Display my assigned events.

    This command lists all events assigned to the logged-in SUPPORT user.
    No parameters are needed, the user is automatically detected.

    Returns:
        None. Displays the list of events assigned to the logged-in user.

    Examples:
        epicevents filter-my-events
    """
    # Manually get services from container
    container = Container()
    event_service = container.event_service()

    console.print_command_header("Mes événements")

    events = event_service.get_events_by_support_contact(current_user.id)

    if not events:
        console.print_error(
            f"Aucun événement assigné à {current_user.first_name} {current_user.last_name}"
        )
        return

    for event in events:
        console.print_field(LABEL_EVENT_ID, str(event.id))
        console.print_field(LABEL_CONTRACT_ID, str(event.contract_id))
        console.print_field(
            LABEL_CLIENT_NAME,
            f"{event.contract.client.first_name} {event.contract.client.last_name}",
        )
        console.print_field(
            LABEL_CLIENT_CONTACT,
            f"{event.contract.client.email}\n{event.contract.client.phone}",
        )
        console.print_field(
            LABEL_EVENT_DATE_START, format_event_datetime(event.event_start)
        )
        console.print_field(
            LABEL_EVENT_DATE_END, format_event_datetime(event.event_end)
        )
        console.print_field(
            LABEL_SUPPORT_CONTACT,
            f"{current_user.first_name} {current_user.last_name} (ID: {current_user.id})",
        )
        console.print_field(LABEL_LOCATION, event.location)
        console.print_field(LABEL_ATTENDEES, str(event.attendees))
        if event.notes:
            console.print_field(LABEL_NOTES, event.notes)
        console.print_separator()

    console.print_success(
        f"Total: {len(events)} événement(s) assigné(s) à {current_user.first_name} {current_user.last_name}"
    )
