import typer
from rich.console import Console
from rich.table import Table
from typing import Optional, List
from datetime import datetime, timedelta

app = typer.Typer(rich_markup_mode="markdown", name="entry")
console = Console()


@app.command("list")
def list_entries(
    date: Optional[str] = typer.Option(None, "--date", help="Filter by a specific date (YYYY-MM-DD)."),
    today: bool = typer.Option(False, "--today", help="Filter for entries logged today."),
    yesterday: bool = typer.Option(False, "--yesterday", help="Filter for entries logged yesterday."),
    week: bool = typer.Option(False, "--week", help="Filter for entries logged this week."),
    month: bool = typer.Option(False, "--month", help="Filter for entries logged this month."),
    project_name: Optional[str] = typer.Option(None, "--project", help="Filter by project name."),
    tag_name: Optional[str] = typer.Option(None, "--tag", help="Filter by tag name."),
    all_entries: bool = typer.Option(False, "--all", help="Show all entries (no date filter)."),
    limit: Optional[int] = typer.Option(None, "--limit", help="Limit number of entries shown."),
):
    """
    Lists time entries. Defaults to today's entries if no filters are specified.
    """
    from .services import time_entry_service, project_service, tag_service
    from .utils import (format_duration, get_start_of_day, get_start_of_week, 
                        get_start_of_month, parse_date_string, convert_utc_to_local, get_current_datetime, 
                        convert_local_to_utc)
    from .database import get_db

    db = next(get_db())
    start_date, end_date = None, None
    now_utc = get_current_datetime()
    now_local = convert_utc_to_local(now_utc)

    # If no options are provided, check if --all was specified
    no_filters = not any([date, today, yesterday, week, month, project_name, tag_name, all_entries])
    if no_filters and not all_entries:
        today = True

    if date:
        start_date = parse_date_string(date, as_local=True)
        end_date = start_date + timedelta(days=1)
    elif today:
        local_start_of_day = get_start_of_day(now_local)
        start_date = convert_local_to_utc(local_start_of_day)
        end_date = convert_local_to_utc(local_start_of_day + timedelta(days=1))
    elif yesterday:
        local_start_of_day = get_start_of_day(now_local - timedelta(days=1))
        start_date = convert_local_to_utc(local_start_of_day)
        end_date = convert_local_to_utc(local_start_of_day + timedelta(days=1))
    elif week:
        local_start_of_week = get_start_of_week(now_local)
        start_date = convert_local_to_utc(local_start_of_week)
        end_date = convert_local_to_utc(local_start_of_week + timedelta(weeks=1))
    elif month:
        local_start_of_month = get_start_of_month(now_local)
        # Correctly calculate the start of the next month
        next_month_val = local_start_of_month.month % 12 + 1
        next_year_val = local_start_of_month.year + (1 if local_start_of_month.month == 12 else 0)
        end_of_month = local_start_of_month.replace(year=next_year_val, month=next_month_val, day=1)
        start_date = convert_local_to_utc(local_start_of_month)
        end_date = convert_local_to_utc(end_of_month)

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
        db, start_date=start_date, end_date=end_date, project_id=project_id, tag_id=tag_id, limit=limit
    )

    if not entries:
        console.print("No time entries found for the given criteria.")
        raise typer.Exit()

    table = Table(title="Time Logs")
    table.add_column("ID", style="cyan")
    table.add_column("Project")
    table.add_column("Description")
    table.add_column("Tags", style="blue")
    table.add_column("Start Time", style="magenta")
    table.add_column("End Time", style="magenta")
    table.add_column("Duration", style="green")

    for entry in entries:
        duration = (entry.end_time - entry.start_time).total_seconds() if entry.end_time else 0
        tags_str = ", ".join([tag.name for tag in entry.tags])
        table.add_row(
            str(entry.id),
            entry.project.name,
            entry.description or "",
            tags_str,
            convert_utc_to_local(entry.start_time).strftime("%Y-%m-%d %H:%M"),
            convert_utc_to_local(entry.end_time).strftime("%Y-%m-%d %H:%M") if entry.end_time else "Running...",
            format_duration(duration),
        )
    
    console.print(table)


@app.command("adjust")
def adjust_entry(
    entry_id: Optional[int] = typer.Argument(None, help="The ID of the time entry to adjust."),
    duration: Optional[str] = typer.Option(None, "--duration", help="New duration (e.g., '1h30m')."),
    desc: Optional[str] = typer.Option(None, "--desc", help="New description."),
    start: Optional[str] = typer.Option(None, "--start", help="New start time (YYYY-MM-DD HH:MM)."),
    end: Optional[str] = typer.Option(None, "--end", help="New end time (YYYY-MM-DD HH:MM)."),
):
    """
    Adjusts the details of a specific time entry.
    """
    from InquirerPy import inquirer
    from .services import time_entry_service
    from .utils import (format_duration, parse_duration_string, parse_date_string, convert_utc_to_local, 
                        prompt_for_entry_selection)
    from .database import get_db

    db = next(get_db())
    if entry_id is None:
        entry_id = prompt_for_entry_selection(db)
        if entry_id is None:
            raise typer.Exit()

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
        updates["start_time"] = parse_date_string(start, as_local=True)
    if end:
        updates["end_time"] = parse_date_string(end, as_local=True)

    if not any([duration, desc, start, end]):
        field_to_edit = inquirer.select(
            message="Which field do you want to edit?",
            choices=["Description", "Duration", "Start Time", "End Time"],
        ).execute()

        if field_to_edit == "Description":
            new_desc = inquirer.text(message="Enter new description:", default=entry.description or "").execute()
            updates["description"] = new_desc
        elif field_to_edit == "Duration":
            new_duration_str = inquirer.text(message="Enter new duration (e.g., 1h 30m):", default=format_duration((entry.end_time - entry.start_time).total_seconds())).execute()
            seconds = parse_duration_string(new_duration_str)
            updates["end_time"] = entry.start_time + timedelta(seconds=seconds)
        elif field_to_edit == "Start Time":
            new_start_str = inquirer.text(message="Enter new start time (YYYY-MM-DD HH:MM):", default=convert_utc_to_local(entry.start_time).strftime("%Y-%m-%d %H:%M")).execute()
            updates["start_time"] = parse_date_string(new_start_str, as_local=True)
        elif field_to_edit == "End Time":
            new_end_str = inquirer.text(message="Enter new end time (YYYY-MM-DD HH:MM):", default=convert_utc_to_local(entry.end_time).strftime("%Y-%m-%d %H:%M")).execute()
            updates["end_time"] = parse_date_string(new_end_str, as_local=True)

    if not updates:
        console.print("No changes made.")
        raise typer.Exit()

    time_entry_service.update_time_entry(db, entry_id, **updates)
    console.print(f"Time entry {entry_id} has been updated.")


@app.command("delete")
def delete_entry(
    entry_id: Optional[int] = typer.Argument(None, help="The ID of the time entry to delete."),
):
    """
    Deletes a specific time entry.
    """
    from InquirerPy import inquirer
    from .services import time_entry_service
    from .utils import prompt_for_entry_selection
    from .database import get_db

    db = next(get_db())
    if entry_id is None:
        entry_id = prompt_for_entry_selection(db)
        if entry_id is None:
            raise typer.Exit()

    entry = time_entry_service.get_time_entry_by_id(db, entry_id)
    if not entry:
        console.print(f"Time entry with ID {entry_id} not found.")
        raise typer.Exit(1)

    if inquirer.confirm(message=f"Are you sure you want to delete time entry {entry.id} ('{entry.project.name}')?", default=False).execute():
        time_entry_service.delete_time_entry(db, entry_id)
        console.print(f"Time entry {entry_id} has been deleted.")
    else:
        console.print("Deletion cancelled.")
