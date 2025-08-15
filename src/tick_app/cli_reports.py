import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from datetime import datetime, timedelta, UTC

from .database import get_db
from .services import time_entry_service, project_service, tag_service
from .utils import get_start_of_day, get_start_of_week, get_start_of_month, parse_date_string, format_duration, convert_utc_to_local, get_current_datetime, convert_local_to_utc

app = typer.Typer(rich_markup_mode="markdown", name="report", help="Generates time tracking reports.")
console = Console()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Generate a report. Defaults to the current week if no subcommand is called.
    """
    if ctx.invoked_subcommand is None:
        console.print("No subcommand specified. Defaulting to weekly report.")
        ctx.invoke(generate_report, week=True)

@app.command("generate")
def generate_report(
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
    Generates a time tracking report.
    """
    db = next(get_db())
    now_utc = get_current_datetime() # This is already UTC
    now_local = convert_utc_to_local(now_utc) # Get current time in local timezone

    start, end = None, None

    # Determine start date
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
    
    # Determine end date
    if end_date:
        end = parse_date_string(end_date, as_local=True) + timedelta(days=1)
    elif day:
        end = convert_local_to_utc(get_start_of_day(now_local) + timedelta(days=1))
    elif week:
        end = convert_local_to_utc(get_start_of_week(now_local) + timedelta(weeks=1))
    elif month:
        # Correctly calculate the start of the next month
        next_month = now_local.month % 12 + 1
        next_year = now_local.year + (1 if now_local.month == 12 else 0)
        end = convert_local_to_utc(now_local.replace(year=next_year, month=next_month, day=1, hour=0, minute=0, second=0, microsecond=0))
    elif year:
        end = convert_local_to_utc(now_local.replace(year=now_local.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0))

    # If no date range is specified at all, default to today for 'generate' command
    if start is None:
        start = convert_local_to_utc(get_start_of_day(now_local))
    if end is None:
        end = now_utc

    print(f"Debug: Report start={start}, end={end}")

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
        raise typer.Exit()

    table = Table(title=f"Time Report (Grouped by {group_by})")
    table.add_column("Category", style="cyan")
    table.add_column("Total Duration", style="green")

    total_overall_duration = 0
    for row in report_data:
        duration_seconds = row['total_duration']
        group_key_display = row['group_key']
        if group_by == 'day':
            # group_key is already a date object, convert it to datetime for timezone conversion
            group_key_dt = datetime.combine(group_key_display, datetime.min.time())
            group_key_display = convert_utc_to_local(group_key_dt).strftime('%Y-%m-%d')
        table.add_row(str(group_key_display), format_duration(duration_seconds))
        total_overall_duration += duration_seconds
    
    table.add_section()
    table.add_row("[bold]TOTAL[/bold]", f"[bold]{format_duration(total_overall_duration)}[/bold]")

    console.print(table)