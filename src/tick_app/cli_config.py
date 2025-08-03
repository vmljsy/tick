import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from .services.config_service import config_service

app = typer.Typer(rich_markup_mode="markdown", name="config")
console = Console()

@app.command("set")
def set_config(
    key: str = typer.Argument(..., help="The configuration key."),
    value: str = typer.Argument(..., help="The configuration value."),
):
    """
    Sets a configuration value.
    """
    config_service.set(key, value)
    console.print(f"Configuration key '[bold green]{key}[/bold green]' set to '[bold green]{value}[/bold green]'.")

@app.command("get")
def get_config(
    key: str = typer.Argument(..., help="The configuration key."),
):
    """
    Gets a configuration value.
    """
    value = config_service.get(key)
    if value is not None:
        console.print(f"Configuration key '[bold green]{key}[/bold green]': '[bold green]{value}[/bold green]'.")
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
    key: str = typer.Argument(..., help="The configuration key to delete."),
):
    """
    Deletes a configuration key.
    """
    if config_service.get(key) is not None:
        config_service.delete(key)
        console.print(f"Configuration key '[bold green]{key}[/bold green]' deleted.")
    else:
        console.print(f"Configuration key '[bold red]{key}[/bold red]' not found.")
        raise typer.Exit(code=1)
