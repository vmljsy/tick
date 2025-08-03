import typer
from rich.console import Console
from typing import Optional, List
from datetime import datetime, timedelta, UTC

from .database import init_db, get_db
from .services import time_entry_service, project_service
from .utils import format_duration, parse_duration_string
from .cli_time_entries import app as entry_app
from .cli_projects import app as project_app
from .cli_reports import app as report_app
from .cli_config import app as config_app

app = typer.Typer(rich_markup_mode="markdown")
app.add_typer(entry_app, name="entry")
app.add_typer(project_app, name="project")
app.add_typer(report_app, name="report")
app.add_typer(config_app, name="config")
console = Console()

@app.callback()
def callback():
    """
    Tick: A command-line time tracking tool.
    """
    init_db()

@app.command("start")
def start_timer(
    project_name: str = typer.Argument(..., help="The name of the project to start the timer for."),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="A description of the time entry."),
    tags: Optional[List[str]] = typer.Option(None, "--tag", "-t", help="Tags to associate with the time entry.")
):
    """
    Starts a new time entry for a project.
    """
    db = next(get_db())
    project = project_service.get_project_by_name(db, project_name)
    if not project:
        if typer.confirm(f"Project '{project_name}' not found. Do you want to create it?"):
            project = project_service.create_project(db, project_name)
            console.print(f"Project '[bold green]{project.name}[/bold green]' created.")
        else:
            raise typer.Exit(code=1)
    
    running_entry = time_entry_service.get_current_running_entry(db)
    if running_entry:
        console.print(f"[bold yellow]Warning:[/bold yellow] A timer is already running for project '{running_entry.project.name}'.")
        if typer.confirm("Do you want to stop the current timer and start a new one?"):
            time_entry_service.stop_timer(db, running_entry.id)
            console.print(f"Timer for '{running_entry.project.name}' stopped.")
        else:
            console.print("Operation cancelled.")
            raise typer.Exit(code=1)

    time_entry = time_entry_service.start_timer(db, project.id, description, tags or [])
    console.print(f"Timer started for project [bold green]'{project.name}'[/bold green] at {time_entry.start_time.strftime('%H:%M:%S')}.")

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
    
    duration = (datetime.now(UTC) - running_entry.start_time.replace(tzinfo=UTC)).total_seconds()
    console.print(f"A timer is running for project [bold green]'{running_entry.project.name}'[/bold green].")
    console.print(f"Started at: {running_entry.start_time.strftime('%H:%M:%S')}")
    console.print(f"Current duration: {format_duration(duration)}")
    if running_entry.description:
        console.print(f"Description: {running_entry.description}")

@app.command("log")
def log_time(
    project_name: str = typer.Argument(..., help="The name of the project to log time for."),
    duration: str = typer.Argument(..., help="The duration of the time entry (e.g., '1h30m')."),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="A description of the time entry."),
    tags: Optional[List[str]] = typer.Option(None, "--tag", "-t", help="Tags to associate with the time entry.")
):
    """
    Logs a completed time entry.
    """
    db = next(get_db())
    project = project_service.get_project_by_name(db, project_name)
    if not project:
        if typer.confirm(f"Project '{project_name}' not found. Do you want to create it?"):
            project = project_service.create_project(db, project_name)
            console.print(f"Project '[bold green]{project.name}[/bold green]' created.")
        else:
            raise typer.Exit(code=1)

    seconds = parse_duration_string(duration)
    end_time = datetime.now(UTC)
    start_time = end_time - timedelta(seconds=seconds)

    time_entry_service.log_time(db, project.id, start_time, end_time, description, tags or [])
    console.print(f"Logged {format_duration(seconds)} for project [bold green]'{project.name}'[/bold green].")


if __name__ == "__main__":
    app()