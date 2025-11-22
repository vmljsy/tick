import typer
from rich.console import Console
from typing import Optional, List
from datetime import datetime, timedelta, UTC
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from .database import get_db_manager, get_db
from .services import time_entry_service, project_service
from .utils import (format_duration, parse_duration_string, convert_utc_to_local, 
                    convert_local_to_utc, get_current_datetime, parse_date_string,
                    prompt_for_project, get_project_by_id_or_name)
from .cli_time_entries import app as entry_app
from .cli_projects import app as project_app
from .cli_reports import app as report_app
from .cli_config import app as config_app
from .cli_export import app as export_app

app = typer.Typer(rich_markup_mode="markdown")
app.add_typer(entry_app, name="entry")
app.add_typer(project_app, name="project")
app.add_typer(report_app, name="report")
app.add_typer(config_app, name="config")
app.add_typer(export_app, name="export")
console = Console()

@app.callback()
def callback():
    """
    Tick: A command-line time tracking tool.
    """
    get_db_manager().init_db()

@app.command("start")
def start_timer(
    project_name: Optional[str] = typer.Argument(None, help="The name of the project to start the timer for."),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="A description of the time entry."),
    tags: Optional[List[str]] = typer.Option(None, "--tag", "-t", help="Tags to associate with the time entry.")
):
    """
    Starts a new time entry for a project.
    """
    db = next(get_db())
    
    if project_name:
        project = project_service.get_project_by_name(db, project_name)
        if not project:
            if inquirer.confirm(message=f"Project '{project_name}' not found. Do you want to create it?", default=True).execute():
                project = project_service.create_project(db, project_name)
                console.print(f"Project '[bold green]{project.name}[/bold green]' created.")
            else:
                raise typer.Exit(code=1)
    else:
        project = prompt_for_project(db, allow_create=True)

    running_entry = time_entry_service.get_current_running_entry(db)
    if running_entry:
        console.print(f"[bold yellow]Warning:[/bold yellow] A timer is already running for project '{running_entry.project.name}'.")
        if inquirer.confirm(message="Do you want to stop the current timer and start a new one?", default=True).execute():
            time_entry_service.stop_timer(db, running_entry.id)
            console.print(f"Timer for '{running_entry.project.name}' stopped.")
        else:
            console.print("Operation cancelled.")
            raise typer.Exit(code=1)

    time_entry = time_entry_service.start_timer(db, project.id, description, tags or [])
    console.print(f"Timer started for project [bold green]'{project.name}'[/bold green] at {convert_utc_to_local(time_entry.start_time).strftime('%H:%M:%S')}.")

@app.command("stop")
def stop_timer():
    """
    Stops the currently running time entry.
    """
    db = next(get_db())
    stopped_entry = time_entry_service.stop_timer(db)
    if not stopped_entry:
        console.print("No timer is currently running.")
        raise typer.Exit(code=1)
    
    duration = (stopped_entry.end_time - stopped_entry.start_time).total_seconds()
    console.print(f"Timer stopped for project [bold green]'{stopped_entry.project.name}'[/bold green].")
    console.print(f"Logged {format_duration(duration)}.")

@app.command("status")
def status():
    """
    Shows the status of the current running timer.
    """
    db = next(get_db())
    running_entry = time_entry_service.get_current_running_entry(db)
    if not running_entry:
        console.print("No timer is currently running.")
        raise typer.Exit()
    
    duration = (get_current_datetime() - running_entry.start_time).total_seconds()
    console.print(f"A timer is running for project [bold green]'{running_entry.project.name}'[/bold green].")
    console.print(f"Started at: {convert_utc_to_local(running_entry.start_time).strftime('%H:%M:%S')}")
    console.print(f"Current duration: {format_duration(duration)}")
    if running_entry.description:
        console.print(f"Description: {running_entry.description}")

@app.command("log")
def log_time(
    project_name: Optional[str] = typer.Argument(None, help="The name of the project to log time for."),
    duration: Optional[str] = typer.Option(None, "--duration", "-D", help="The duration of the time entry (e.g., '1h30m')."),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start time of the entry (YYYY-MM-DD HH:MM)."),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End time of the entry (YYYY-MM-DD HH:MM)."),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="A description of the time entry."),
    tags: Optional[List[str]] = typer.Option(None, "--tag", "-t", help="Tags to associate with the time entry.")
):
    """
    Logs a completed time entry.
    """
    db = next(get_db())
    
    if project_name:
        project = project_service.get_project_by_name(db, project_name)
        if not project:
            if inquirer.confirm(message=f"Project '{project_name}' not found. Do you want to create it?", default=True).execute():
                project = project_service.create_project(db, project_name)
                console.print(f"Project '[bold green]{project.name}[/bold green]' created.")
            else:
                raise typer.Exit(code=1)
    else:
        project = prompt_for_project(db, allow_create=True)

    if duration and (start or end):
        console.print("[bold red]Error:[/bold red] Cannot use --duration with --start or --end.")
        raise typer.Exit(code=1)
    if (start and not end) or (end and not start):
        console.print("[bold red]Error:[/bold red] Both --start and --end must be provided if one is used.")
        raise typer.Exit(code=1)

    if not duration and not (start and end):
        duration = inquirer.text(message="Enter duration (e.g., '1h 30m'):").execute()
        if not duration:
            console.print("Operation cancelled.")
            raise typer.Exit()

    if start and end:
        start_time = parse_date_string(start, as_local=True)
        end_time = parse_date_string(end, as_local=True)
        if start_time >= end_time:
            console.print("[bold red]Error:[/bold red] Start time cannot be after or equal to end time.")
            raise typer.Exit(code=1)
        seconds = (end_time - start_time).total_seconds()
    elif duration:
        seconds = parse_duration_string(duration)
        end_time = get_current_datetime()
        start_time = end_time - timedelta(seconds=seconds)
    else:
        # This case should not be reached due to the prompt above
        console.print("[bold red]Error:[/bold red] Duration or start/end times are required.")
        raise typer.Exit(code=1)

    time_entry_service.log_time(db, project.id, start_time, end_time, description, tags or [])
    console.print(f"Logged {format_duration(seconds)} for project [bold green]'{project.name}'[/bold green].")


if __name__ == "__main__":
    app()
