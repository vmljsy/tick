import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from datetime import datetime, timedelta, UTC

from .database import get_db
from .services import time_entry_service, project_service, tag_service
from .utils import get_start_of_day, get_start_of_week, get_start_of_month, parse_date_string, format_duration

app = typer.Typer(rich_markup_mode="markdown", name="report")
console = Console()

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
    now = datetime.now(UTC)
    
    if start_date:
        start = parse_date_string(start_date)
    elif day:
        start = get_start_of_day(now)
    elif week:
        start = get_start_of_week(now)
    elif month:
        start = get_start_of_month(now)
    elif year:
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start = get_start_of_day(now)

    if end_date:
        end = parse_date_string(end_date) + timedelta(days=1)
    elif day:
        end = get_start_of_day(now) + timedelta(days=1)
    elif week:
        end = get_start_of_week(now) + timedelta(weeks=1)
    elif month:
        year_for_next_month = now.year
        month_for_next_month = now.month + 1
        if month_for_next_month > 12:
            month_for_next_month = 1
            year_for_next_month += 1
        end = datetime(year_for_next_month, month_for_next_month, 1, 0, 0, 0, 0)
    elif year:
        end = datetime(now.year + 1, 1, 1, 0, 0, 0, 0)
    else:
        end = now

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
        table.add_row(str(row['group_key']), format_duration(duration_seconds))
        total_overall_duration += duration_seconds
    
    table.add_section()
    table.add_row("[bold]TOTAL[/bold]", f"[bold]{format_duration(total_overall_duration)}[/bold]")

    console.print(table)