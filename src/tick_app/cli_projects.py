import typer
from rich.console import Console
from rich.table import Table
from typing import Optional, List
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from .database import get_db
from .services import project_service, tag_service
from .utils import prompt_for_project, get_project_by_id_or_name

app = typer.Typer(rich_markup_mode="markdown", name="project", no_args_is_help=True )
console = Console()


@app.command("list" , )
def list_projects(
    archived: bool = typer.Option(False, "--archived", help="Include archived projects."),
):
    """
    Lists all projects.
    """
    db = next(get_db())
    projects = project_service.list_projects(db, include_archived=archived)
    
    table = Table(title="Projects")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Parent")
    table.add_column("Archived", style="red")

    for project in projects:
        table.add_row(
            str(project.id),
            project.name,
            project.parent.name if project.parent else "",
            "Yes" if project.archived else "No"
        )
    
    console.print(table)

@app.command("add")
def add_project(
    name: Optional[str] = typer.Argument(None, help="The name of the new project."),
    parent: Optional[str] = typer.Option(None, "--parent", help="The name of the parent project."),
):
    """
    Adds a new project.
    """
    db = next(get_db())
    if not name:
        name = inquirer.text(message="Enter the name for the new project:").execute()
        if not name:
            console.print("[bold red]Error:[/bold red] Project name cannot be empty.")
            raise typer.Exit(1)

    parent_id = None
    if parent:
        parent_project = get_project_by_id_or_name(db, parent)
        parent_id = parent_project.id

    project_service.create_project(db, name, parent_id)
    console.print(f"Project [bold green]'{name}'[/bold green] has been created.")

@app.command("edit")
def edit_project(
    project_id_or_name: Optional[str] = typer.Argument(None, help="The ID or name of the project to edit."),
    name: Optional[str] = typer.Option(None, "--name", help="The new name for the project."),
    parent: Optional[str] = typer.Option(None, "--parent", help="The new parent for the project."),
):
    """
    Edits a project's details.
    """
    db = next(get_db())
    if not project_id_or_name:
        project = prompt_for_project(db, "Select a project to edit:")
    else:
        project = get_project_by_id_or_name(db, project_id_or_name)

    updates = {}
    if name:
        updates["name"] = name
    if parent:
        parent_project = get_project_by_id_or_name(db, parent)
        updates["parent_id"] = parent_project.id
    
    if not any([name, parent]):
        console.print("No edit operations specified. Please use options like --name or --parent.")
        raise typer.Exit()

    if updates:
        project_service.update_project(db, project.id, **updates)

    console.print(f"Project [bold green]'{project.name}'[/bold green] has been updated.")

@app.command("archive")
def archive_project(
    project_id_or_name: Optional[str] = typer.Argument(None, help="The ID or name of the project to archive."),
):
    """
    Archives a project.
    """
    db = next(get_db())
    if not project_id_or_name:
        project = prompt_for_project(db, "Select a project to archive:")
    else:
        project = get_project_by_id_or_name(db, project_id_or_name)

    project_service.archive_project(db, project.id)
    console.print(f"Project [bold green]'{project.name}'[/bold green] has been archived.")

@app.command("delete")
def delete_project(
    project_id_or_name: Optional[str] = typer.Argument(None, help="The ID or name of the project to delete."),
):
    """
    Deletes a project.
    """
    db = next(get_db())
    if not project_id_or_name:
        project = prompt_for_project(db, "Select a project to delete:")
    else:
        project = get_project_by_id_or_name(db, project_id_or_name)

    if inquirer.confirm(f"Are you sure you want to delete project '{project.name}'? This will also delete all associated time entries.", default=False).execute():
        project_service.delete_project(db, project.id)
        console.print(f"Project [bold green]'{project.name}'[/bold green] has been deleted.")
    else:
        console.print("Deletion cancelled.")
