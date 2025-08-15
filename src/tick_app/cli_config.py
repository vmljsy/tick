import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from .services.config_service import config_service

app = typer.Typer(rich_markup_mode="markdown", name="config")
console = Console()

@app.command("set")
def set_config(
    key: Optional[str] = typer.Argument(None, help="The configuration key."),
    value: Optional[str] = typer.Argument(None, help="The configuration value."),
):
    """
    Sets a configuration value.
    """
    if key is None:
        key = inquirer.text(message="Enter the configuration key:").execute()
        if not key:
            console.print("[bold red]Error:[/bold red] Key cannot be empty.")
            raise typer.Exit(1)
    
    if value is None:
        value = inquirer.text(message=f"Enter the value for '{key}':").execute()

    config_service.set(key, value)
    console.print(f"Configuration key '[bold green]{key}[/bold green]' set to '[bold green]{value}[/bold green]'.")

@app.command("get")
def get_config(
    key: Optional[str] = typer.Argument(None, help="The configuration key."),
):
    """
    Gets a configuration value.
    """
    if key is None:
        keys = config_service.all().keys()
        if not keys:
            console.print("No configuration keys set.")
            raise typer.Exit()
        key = inquirer.select(
            message="Select a configuration key to view:",
            choices=list(keys)
        ).execute()

    value = config_service.get(key)
    if value is not None:
        console.print(f"[bold green]{key}[/bold green] = {value}")
    else:
        console.print(f"Configuration key '[bold red]{key}[/bold red]' not found.")
        raise typer.Exit(code=1)

@app.command("list")
def list_config():
    """
    Lists all configuration values.
    """
    config_values = config_service.all()
    if not config_values:
        console.print("No configuration values set.")
        return

    table = Table(title="Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    for key, value in config_values.items():
        table.add_row(key, str(value))
    
    console.print(table)

@app.command("delete")
def delete_config(
    key: Optional[str] = typer.Argument(None, help="The configuration key to delete."),
):
    """
    Deletes a configuration key.
    """
    if key is None:
        keys = config_service.all().keys()
        if not keys:
            console.print("No configuration keys set.")
            raise typer.Exit()
        key = inquirer.select(
            message="Select a configuration key to delete:",
            choices=list(keys)
        ).execute()

    if config_service.get(key) is not None:
        if inquirer.confirm(message=f"Are you sure you want to delete the key '{key}'?", default=False).execute():
            config_service.delete(key)
            console.print(f"Configuration key '[bold green]{key}[/bold green]' deleted.")
        else:
            console.print("Deletion cancelled.")
    else:
        console.print(f"Configuration key '[bold red]{key}[/bold red]' not found.")
        raise typer.Exit(code=1)
