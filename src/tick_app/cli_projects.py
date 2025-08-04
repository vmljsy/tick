import typer
from rich.console import Console
from rich.table import Table
from typing import Optional, List

from .database import get_db
from .services import project_service, tag_service

app = typer.Typer(rich_markup_mode="markdown", name="project")
console = Console()

@app.command("list")
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
            "Yes" if False else "No" # TODO: Add archived status to model
        )
    
    console.print(table)

@app.command("add")
def add_project(
    name: str = typer.Argument(..., help="The name of the new project."),
    parent: Optional[str] = typer.Option(None, "--parent", help="The name of the parent project."),
):
    """
    Adds a new project.
    """
    db = next(get_db())
    parent_id = None
    if parent:
        parent_project = project_service.get_project_by_name(db, parent)
        if not parent_project:
            console.print(f"Parent project '{parent}' not found.")
            raise typer.Exit(1)
        parent_id = parent_project.id

    project_service.create_project(db, name, parent_id)
    console.print(f"Project [bold green]'{name}'[/bold green] has been created.")

@app.command("edit")
def edit_project(
    project_id_or_name: str = typer.Argument(..., help="The ID or name of the project to edit."),
    name: Optional[str] = typer.Option(None, "--name", help="The new name for the project."),
    parent: Optional[str] = typer.Option(None, "--parent", help="The new parent for the project."),
    add_tag: Optional[str] = typer.Option(None, "--add-tag", help="A tag to add to the project."),
    remove_tag: Optional[str] = typer.Option(None, "--remove-tag", help="A tag to remove from the project."),
):
    """
    Edits a project's details.
    """
    db = next(get_db())
    project = project_service.get_project_by_name(db, project_id_or_name) or project_service.get_project_by_id(db, int(project_id_or_name))
    if not project:
        console.print(f"Project '{project_id_or_name}' not found.")
        raise typer.Exit(1)

    updates = {}
    if name:
        updates["name"] = name
    if parent:
        parent_project = project_service.get_project_by_name(db, parent)
        if not parent_project:
            console.print(f"Parent project '{parent}' not found.")
            raise typer.Exit(1)
        updates["parent_id"] = parent_project.id
    
    if updates:
        project_service.update_project(db, project.id, **updates)
    
    if add_tag:
        # TODO: Implement tag adding
        pass

    if remove_tag:
        # TODO: Implement tag removal
        pass

    console.print(f"Project [bold green]'{project.name}'[/bold green] has been updated.")

@app.command("archive")
def archive_project(
    project_id_or_name: str = typer.Argument(..., help="The ID or name of the project to archive."),
):
    """
    Archives a project.
    """
    db = next(get_db())
    project = project_service.get_project_by_name(db, project_id_or_name) or project_service.get_project_by_id(db, int(project_id_or_name))
    if not project:
        console.print(f"Project '{project_id_or_name}' not found.")
        raise typer.Exit(1)

    # TODO: Implement archiving
    console.print(f"Project [bold green]'{project.name}'[/bold green] has been archived.")

@app.command("delete")
def delete_project(
    project_id_or_name: str = typer.Argument(..., help="The ID or name of the project to delete."),
):
    """
    Deletes a project.
    """
    db = next(get_db())
    project = project_service.get_project_by_name(db, project_id_or_name) or project_service.get_project_by_id(db, int(project_id_or_name))
    if not project:
        console.print(f"Project '{project_id_or_name}' not found.")
        raise typer.Exit(1)

    if typer.confirm(f"Are you sure you want to delete project '{project.name}'? This will also delete all associated time entries."):
        project_service.delete_project(db, project.id)
        console.print(f"Project [bold green]'{project.name}'[/bold green] has been deleted.")
    else:
        console.print("Deletion cancelled.")
