from datetime import datetime, timedelta, UTC
import pytz

from .config import get_user_timezone

class ProjectNotFound(Exception):
    pass

class TimerNotRunning(Exception):
    pass

def format_duration(seconds: int) -> str:
    if seconds is None:
        return ""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

def parse_duration_string(s: str) -> int:
    total_seconds = 0
    # Regex to find numbers followed by h, m, or s
    import re
    matches = re.findall(r'(\d+)([hms])', s)
    for value, unit in matches:
        value = int(value)
        if unit == 'h':
            total_seconds += value * 3600
        elif unit == 'm':
            total_seconds += value * 60
        elif unit == 's':
            total_seconds += value
    return total_seconds

def get_current_datetime() -> datetime:
    return datetime.now(UTC)

def convert_utc_to_local(dt_utc: datetime) -> datetime:
    if dt_utc.tzinfo is None: # Assume naive datetime is UTC
        dt_utc = dt_utc.replace(tzinfo=UTC)
    local_tz = pytz.timezone(get_user_timezone())
    return dt_utc.astimezone(local_tz)

def convert_local_to_utc(dt_local: datetime) -> datetime:
    local_tz = pytz.timezone(get_user_timezone())
    if dt_local.tzinfo is None: # Assume naive datetime is local
        dt_local = local_tz.localize(dt_local)
    return dt_local.astimezone(UTC)

def parse_date_string(s: str, as_local: bool = True) -> datetime:
    # Try parsing with various formats
    dt_naive = None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt_naive = datetime.strptime(s, fmt)
            break
        except ValueError:
            continue
    
    if dt_naive is None:
        raise ValueError(f"Unable to parse date string: {s}. Expected format YYYY-MM-DD [HH:MM[:SS]].")

    if as_local:
        return convert_local_to_utc(dt_naive)
    return dt_naive.replace(tzinfo=UTC) # Return as UTC if not local

def get_start_of_day(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

def get_start_of_week(dt: datetime) -> datetime:
    start_of_day = get_start_of_day(dt)
    return start_of_day - timedelta(days=start_of_day.weekday())

def get_start_of_month(dt: datetime) -> datetime:
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

# UI Helper Functions for CLI
def prompt_for_project(db, message: str = "Select a project:", allow_create: bool = False):
    """
    Unified project selection prompt across all commands.
    
    Args:
        db: Database session
        message: Custom message to display
        allow_create: If True, adds option to create new project
    
    Returns:
        Project object
    """
    from .services import project_service
    from InquirerPy import inquirer
    from InquirerPy.base.control import Choice
    from rich.console import Console
    import typer
    
    console = Console()
    projects = project_service.list_projects(db, include_archived=False)
    
    if not projects and not allow_create:
        console.print("[bold yellow]Warning:[/bold yellow] No projects found. Please add one first.")
        raise typer.Exit(1)
    
    choices = [Choice(value=p.id, name=p.name) for p in projects]
    
    if allow_create:
        CREATE_NEW = Choice(value=None, name="[Create New Project]")
        choices.append(CREATE_NEW)
    
    project_id = inquirer.select(message=message, choices=choices).execute()
    
    if project_id is None:  # Create new project
        new_project_name = inquirer.text(message="Enter the name for the new project:").execute()
        if not new_project_name:
            console.print("[bold red]Error:[/bold red] Project name cannot be empty.")
            raise typer.Exit(1)
        return project_service.create_project(db, new_project_name)
    else:
        return project_service.get_project_by_id(db, project_id)


def prompt_for_entry_selection(db, message: str = "Select a time entry:", limit: int = 15):
    """
    Unified entry selection prompt across all commands.
    
    Args:
        db: Database session
        message: Custom message to display
        limit: Maximum number of entries to show
    
    Returns:
        Entry ID or None if cancelled
    """
    from .services import time_entry_service
    from InquirerPy import inquirer
    from InquirerPy.base.control import Choice
    from rich.console import Console
    
    console = Console()
    entries = time_entry_service.list_time_entries(db, limit=limit)
    
    if not entries:
        console.print("[bold yellow]No time entries found.[/bold yellow]")
        return None
    
    choices = [
        Choice(
            value=entry.id,
            name=f"{entry.id}: {entry.project.name} - {entry.description or 'No description'} ({format_duration((entry.end_time - entry.start_time).total_seconds() if entry.end_time else 0)})"
        )
        for entry in entries
    ]
    
    return inquirer.select(message=message, choices=choices).execute()


def get_project_by_id_or_name(db, identifier: str):
    """
    Get project by ID (if numeric) or name.
    
    Args:
        db: Database session
        identifier: Project ID or name
    
    Returns:
        Project object
    
    Raises:
        typer.Exit if project not found
    """
    from .services import project_service
    from rich.console import Console
    import typer
    
    console = Console()
    
    try:
        project_id = int(identifier)
        project = project_service.get_project_by_id(db, project_id)
    except ValueError:
        project = project_service.get_project_by_name(db, identifier)
    
    if not project:
        console.print(f"[bold red]Error:[/bold red] Project '{identifier}' not found.")
        console.print("Create it first with: [bold]tick project add {identifier}[/bold]")
        raise typer.Exit(1)
    
    return project
