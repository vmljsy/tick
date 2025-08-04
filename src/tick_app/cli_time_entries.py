import typer
from rich.console import Console
from rich.table import Table
from typing import Optional, List
from datetime import datetime, timedelta

from .database import get_db
from .services import time_entry_service, project_service, tag_service
from .utils import format_duration, parse_duration_string, get_start_of_day, get_start_of_week, get_start_of_month, parse_date_string

app = typer.Typer(rich_markup_mode="markdown", name="entry")
console = Console()

@app.command("logs")
def list_logs(
    date: Optional[str] = typer.Option(None, "--date", help="Filter by a specific date (YYYY-MM-DD)."),
    today: bool = typer.Option(False, "--today", help="Filter for entries logged today."),
    yesterday: bool = typer.Option(False, "--yesterday", help="Filter for entries logged yesterday."),
    week: bool = typer.Option(False, "--week", help="Filter for entries logged this week."),
    month: bool = typer.Option(False, "--month", help="Filter for entries logged this month."),
    project_name: Optional[str] = typer.Option(None, "--project", help="Filter by project name."),
    tag_name: Optional[str] = typer.Option(None, "--tag", help="Filter by tag name."),
):
    """
    Lists time entries with various filters.
    """
    db = next(get_db())
    start_date, end_date = None, None
    now = datetime.utcnow()

    if date:
        start_date = get_start_of_day(parse_date_string(date))
        end_date = start_date + timedelta(days=1)
    elif today:
        start_date = get_start_of_day(now)
    elif yesterday:
        start_date = get_start_of_day(now - timedelta(days=1))
        end_date = start_date + timedelta(days=1)
    elif week:
        start_date = get_start_of_week(now)
    elif month:
        start_date = get_start_of_month(now)

    project_id, tag_id = None, None
    if project_name:
        project = project_service.get_project_by_name(db, project_name)
        if not project:
            console.print(f"Project '{project_name}' not found.")
            raise typer.Exit(1)
        project_id = project.id
    
    if tag_name:
        tag = tag_service.get_tag_by_name(db, tag_name)
        if not tag:
            console.print(f"Tag '{tag_name}' not found.")
            raise typer.Exit(1)
        tag_id = tag.id

    entries = time_entry_service.list_time_entries(
        db, start_date=start_date, end_date=end_date, project_id=project_id, tag_id=tag_id
    )

    if not entries:
        console.print("No time entries found for the given criteria.")
        raise typer.Exit()

    table = Table(title="Time Logs")
    table.add_column("ID", style="cyan")
    table.add_column("Project")
    table.add_column("Description")
    table.add_column("Start Time", style="magenta")
    table.add_column("End Time", style="magenta")
    table.add_column("Duration", style="green")

    for entry in entries:
        duration = (entry.end_time - entry.start_time).total_seconds() if entry.end_time else 0
        table.add_row(
            str(entry.id),
            entry.project.name,
            entry.description or "",
            entry.start_time.strftime("%Y-%m-%d %H:%M"),
            entry.end_time.strftime("%Y-%m-%d %H:%M") if entry.end_time else "Running...",
            format_duration(duration),
        )
    
    console.print(table)


@app.command("adjust")
def adjust_entry(
    entry_id: int = typer.Argument(..., help="The ID of the time entry to adjust."),
    duration: Optional[str] = typer.Option(None, "--duration", help="New duration (e.g., '1h30m')."),
    desc: Optional[str] = typer.Option(None, "--desc", help="New description."),
    start: Optional[str] = typer.Option(None, "--start", help="New start time (YYYY-MM-DD HH:MM)."),
    end: Optional[str] = typer.Option(None, "--end", help="New end time (YYYY-MM-DD HH:MM)."),
):
    """
    Adjusts the details of a specific time entry.
    """
    db = next(get_db())
    entry = time_entry_service.get_time_entry_by_id(db, entry_id)
    if not entry:
        console.print(f"Time entry with ID {entry_id} not found.")
        raise typer.Exit(1)

    updates = {}
    if duration:
        seconds = parse_duration_string(duration)
        updates["end_time"] = entry.start_time + timedelta(seconds=seconds)
    if desc is not None:
        updates["description"] = desc
    if start:
        updates["start_time"] = parse_date_string(start)
    if end:
        updates["end_time"] = parse_date_string(end)

    if not updates:
        console.print("No changes specified. Use options like --duration, --desc, etc.")
        raise typer.Exit()

    time_entry_service.update_time_entry(db, entry_id, **updates)
    console.print(f"Time entry {entry_id} has been updated.")


@app.command("delete")
def delete_entry(
    entry_id: int = typer.Argument(..., help="The ID of the time entry to delete."),
):
    """
    Deletes a specific time entry.
    """
    db = next(get_db())
    if not time_entry_service.get_time_entry_by_id(db, entry_id):
        console.print(f"Time entry with ID {entry_id} not found.")
        raise typer.Exit(1)

    if typer.confirm(f"Are you sure you want to delete time entry {entry_id}?"):
        time_entry_service.delete_time_entry(db, entry_id)
        console.print(f"Time entry {entry_id} has been deleted.")
    else:
        console.print("Deletion cancelled.")

@app.command("show-all")
def show_all_entries(
    head: Optional[int] = typer.Option(None, "--head", "-n", help="Show only the first N entries."),
    tail: Optional[int] = typer.Option(None, "--tail", "-m", help="Show only the last M entries."),
):
    """
    Shows all time entries in the database, with optional head/tail filtering.
    """
    db = next(get_db())
    
    if head is not None and tail is not None:
        console.print("[bold red]Error:[/bold red] Cannot use --head and --tail together.")
        raise typer.Exit(code=1)

    entries = []
    if head is not None:
        entries = time_entry_service.list_time_entries(db, limit=head)
    elif tail is not None:
        total_entries = len(time_entry_service.list_time_entries(db)) # Get total count
        if total_entries > 0:
            offset = max(0, total_entries - tail)
            entries = time_entry_service.list_time_entries(db, offset=offset, limit=tail)
    else:
        entries = time_entry_service.list_time_entries(db)

    if not entries:
        console.print("No time entries found.")
        raise typer.Exit()

    table = Table(title="All Time Entries")
    table.add_column("ID", style="cyan")
    table.add_column("Project")
    table.add_column("Description")
    table.add_column("Start Time", style="magenta")
    table.add_column("End Time", style="magenta")
    table.add_column("Duration", style="green")

    for entry in entries:
        duration = (entry.end_time - entry.start_time).total_seconds() if entry.end_time else 0
        table.add_row(
            str(entry.id),
            entry.project.name if entry.project else "N/A",
            entry.description or "",
            entry.start_time.strftime("%Y-%m-%d %H:%M"),
            entry.end_time.strftime("%Y-%m-%d %H:%M") if entry.end_time else "Running...",
            format_duration(duration),
        )
    
    console.print(table)
