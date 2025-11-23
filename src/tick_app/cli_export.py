import typer
from rich.console import Console
from typing import Optional, List, TextIO
from datetime import datetime, timedelta
import csv
import json

from .services import time_entry_service, project_service
from .utils import format_duration, parse_date_string, get_start_of_day, get_start_of_week, get_start_of_month, convert_utc_to_local, get_current_datetime, convert_local_to_utc

app = typer.Typer(rich_markup_mode="markdown", name="export", help="Export time tracking data.")
console = Console()

# Helper function to write output
def _write_output(output_file: Optional[TextIO], content: str):
    if output_file:
        output_file.write(content)
        output_file.close()
    else:
        console.print(content)

# Helper to get output stream
def _get_output_stream(output_path: Optional[str]):
    if output_path:
        try:
            return open(output_path, 'w', newline='', encoding='utf-8')
        except IOError as e:
            console.print(f"[bold red]Error:[/bold red] Could not open file {output_path}: {e}")
            raise typer.Exit(1)
    return None # Indicates stdout

@app.command("entries")
def export_entries(
    format: str = typer.Option("csv", "--format", "-f", help="Output format: csv, json, txt."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path. Prints to stdout if not specified."),
    date: Optional[str] = typer.Option(None, "--date", help="Filter by a specific date (YYYY-MM-DD)."),
    today: bool = typer.Option(False, "--today", help="Filter for entries logged today."),
    yesterday: bool = typer.Option(False, "--yesterday", help="Filter for entries logged yesterday."),
    week: bool = typer.Option(False, "--week", help="Filter for entries logged this week."),
    month: bool = typer.Option(False, "--month", help="Filter for entries logged this month."),
    project_name: Optional[str] = typer.Option(None, "--project", help="Filter by project name."),
    tag_name: Optional[str] = typer.Option(None, "--tag", help="Filter by tag name."),
):
    """
    Exports raw time entries.
    """
    from .database import get_db

    db = next(get_db())
    start_date, end_date = None, None
    now_utc = get_current_datetime()
    now_local = convert_utc_to_local(now_utc)

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
        next_month_val = local_start_of_month.month % 12 + 1
        next_year_val = local_start_of_month.year + (1 if local_start_of_month.month == 12 else 0)
        end_of_month = local_start_of_month.replace(year=next_year_val, month=next_month_val, day=1)
        start_date = convert_local_to_utc(local_start_of_month)
        end_date = convert_local_to_utc(end_of_month)

    project_id = None
    if project_name:
        project = project_service.get_project_by_name(db, project_name)
        if not project:
            console.print(f"Project '{project_name}' not found.")
            raise typer.Exit(1)
        project_id = project.id

    entries = time_entry_service.list_time_entries(
        db, start_date=start_date, end_date=end_date, project_id=project_id
    )

    if not entries:
        console.print("No time entries found for the given criteria.")
        return

    output_stream = _get_output_stream(output)

    if format == "csv":
        writer = csv.writer(output_stream if output_stream else console.file)
        writer.writerow(["ID", "Project", "Description", "Start Time", "End Time", "Duration (s)"])
        for entry in entries:
            duration_s = (entry.end_time - entry.start_time).total_seconds() if entry.end_time else 0
            writer.writerow([
                entry.id,
                entry.project.name,
                entry.description or "",
                convert_utc_to_local(entry.start_time).isoformat(),
                convert_utc_to_local(entry.end_time).isoformat() if entry.end_time else "",
                duration_s
            ])
    elif format == "json":
        data = []
        for entry in entries:
            data.append({
                "id": entry.id,
                "project": entry.project.name,
                "description": entry.description or "",
                "start_time": convert_utc_to_local(entry.start_time).isoformat(),
                "end_time": convert_utc_to_local(entry.end_time).isoformat() if entry.end_time else None,
                "duration_seconds": (entry.end_time - entry.start_time).total_seconds() if entry.end_time else 0
            })
        _write_output(output_stream, json.dumps(data, indent=2))
    elif format == "txt":
        content = []
        for entry in entries:
            duration_str = format_duration((entry.end_time - entry.start_time).total_seconds() if entry.end_time else 0)
            content.append(f"ID: {entry.id}, Project: {entry.project.name}, Desc: {entry.description or ''}, Start: {convert_utc_to_local(entry.start_time).strftime('%Y-%m-%d %H:%M')}, End: {convert_utc_to_local(entry.end_time).strftime('%Y-%m-%d %H:%M') if entry.end_time else 'Running...'}, Duration: {duration_str}")
        _write_output(output_stream, "\n".join(content))
    else:
        console.print(f"[bold red]Error:[/bold red] Unsupported format: {format}")
        raise typer.Exit(1)

    if output_stream:
        console.print(f"[bold green]Time entries exported to {output} in {format} format.[/bold green]")

@app.command("projects")
def export_projects(
    format: str = typer.Option("csv", "--format", "-f", help="Output format: csv, json, txt."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path. Prints to stdout if not specified."),
    archived: bool = typer.Option(False, "--archived", help="Include archived projects."),
):
    """
    Exports project list.
    """
    from .database import get_db

    db = next(get_db())
    projects = project_service.list_projects(db, include_archived=archived)

    if not projects:
        console.print("No projects found.")
        return

    output_stream = _get_output_stream(output)

    if format == "csv":
        writer = csv.writer(output_stream if output_stream else console.file)
        writer.writerow(["ID", "Name", "Parent", "Archived"])
        for project in projects:
            writer.writerow([
                project.id,
                project.name,
                project.parent.name if project.parent else "",
                "Yes" if project.archived else "No"
            ])
    elif format == "json":
        data = []
        for project in projects:
            data.append({
                "id": project.id,
                "name": project.name,
                "parent": project.parent.name if project.parent else None,
                "archived": project.archived
            })
        _write_output(output_stream, json.dumps(data, indent=2))
    elif format == "txt":
        content = []
        for project in projects:
            content.append(f"ID: {project.id}, Name: {project.name}, Parent: {project.parent.name if project.parent else ''}, Archived: {{'Yes' if project.archived else 'No'}}")
        _write_output(output_stream, "\n".join(content))
    else:
        console.print(f"[bold red]Error:[/bold red] Unsupported format: {format}")
        raise typer.Exit(1)

    if output_stream:
        console.print(f"[bold green]Projects exported to {output} in {format} format.[/bold green]")

@app.command("report")
def export_report(
    format: str = typer.Option("csv", "--format", "-f", help="Output format: csv, json, txt."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path. Prints to stdout if not specified."),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="Start date for the report (YYYY-MM-DD)."),
    end_date: Optional[str] = typer.Option(None, "--end-date", help="End date for the report (YYYY-MM-DD)."),
    day: bool = typer.Option(False, "--day", help="Generate a report for the current day."),
    week: bool = typer.Option(False, "--week", help="Generate a report for the current week."),
    month: bool = typer.Option(False, "--month", help="Generate a report for the current month."),
    year: bool = typer.Option(False, "--year", help="Generate a report for the current year."),
    project_name: Optional[str] = typer.Option(None, "--project", help="Filter by project name."),
    tag_name: Optional[str] = typer.Option(None, "--tag", help="Filter by tag name."),
    group_by: str = typer.Option("project", "--group-by", help="Group the report by: 'day', 'project', or 'tag'."),
):
    """
    Exports a time tracking report.
    """
    from .database import get_db

    db = next(get_db())
    now_utc = get_current_datetime()
    now_local = convert_utc_to_local(now_utc)

    start, end = None, None

    if start_date:
        start = parse_date_string(start_date, as_local=True)
    elif day:
        start = convert_local_to_utc(get_start_of_day(now_local))
    elif week:
        start = convert_local_to_utc(get_start_of_week(now_local))
    elif month:
        start = convert_local_to_utc(get_start_of_month(now_local))
    elif year:
        start = convert_local_to_utc(now_local.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0))
    
    if end_date:
        end = parse_date_string(end_date, as_local=True) + timedelta(days=1)
    elif day:
        end = convert_local_to_utc(get_start_of_day(now_local) + timedelta(days=1))
    elif week:
        end = convert_local_to_utc(get_start_of_week(now_local) + timedelta(weeks=1))
    elif month:
        next_month = now_local.month % 12 + 1
        next_year = now_local.year + (1 if now_local.month == 12 else 0)
        end = convert_local_to_utc(now_local.replace(year=next_year, month=next_month, day=1, hour=0, minute=0, second=0, microsecond=0))
    elif year:
        end = convert_local_to_utc(now_local.replace(year=now_local.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0))

    if start is None:
        start = convert_local_to_utc(get_start_of_day(now_local))
    if end is None:
        end = now_utc

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

    report_data = time_entry_service.generate_report(
        db, start_date=start, end_date=end, group_by=group_by, project_id=project_id, tag_id=tag_id
    )

    if not report_data:
        console.print("No data found for the given report criteria.")
        return

    output_stream = _get_output_stream(output)

    if format == "csv":
        writer = csv.writer(output_stream if output_stream else console.file)
        writer.writerow(["Category", "Total Duration (s)"])
        for row in report_data:
            writer.writerow([row['group_key'], row['total_duration']])
    elif format == "json":
        data = []
        for row in report_data:
            data.append({
                "category": str(row['group_key']),
                "total_duration_seconds": row['total_duration']
            })
        _write_output(output_stream, json.dumps(data, indent=2))
    elif format == "txt":
        content = []
        for row in report_data:
            content.append(f"Category: {row['group_key']}, Total Duration: {format_duration(row['total_duration'])}")
        _write_output(output_stream, "\n".join(content))
    else:
        console.print(f"[bold red]Error:[/bold red] Unsupported format: {format}")
        raise typer.Exit(1)

    if output_stream:
        console.print(f"[bold green]Report exported to {output} in {format} format.[/bold green]")
