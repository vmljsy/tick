import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from .services.config_service import config_service, DEFAULT_CONFIGS

app = typer.Typer(rich_markup_mode="markdown", name="config")
console = Console()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Manage configuration settings.
    """
    if ctx.invoked_subcommand is None:
        ctx.show_help()

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
        # Also include default keys for selection
        all_keys = list(set(keys) | set(DEFAULT_CONFIGS.keys()))
        if not all_keys:
            console.print("No configuration keys set or available.")
            raise typer.Exit()
        key = inquirer.select(
            message="Select a configuration key to view:",
            choices=all_keys
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
    Lists all configuration values, including defaults.
    """
    all_set_configs = config_service.all()

    table = Table(title="Configuration Values")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Default Value", style="yellow")
    table.add_column("Description", style="dim")

    for key, details in DEFAULT_CONFIGS.items():
        current_value = all_set_configs.get(key, "") # Get set value or empty string
        default_value = details["value"]
        description = details["description"]
        
        # If current_value is empty, it means it's using the default, so display default in Value column
        display_value = current_value if current_value != "" else default_value

        table.add_row(key, str(display_value), str(default_value), description)
    
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
        # Also include default keys for selection
        all_keys = list(set(keys) | set(DEFAULT_CONFIGS.keys()))
        if not all_keys:
            console.print("No configuration keys set or available.")
            raise typer.Exit()
        key = inquirer.select(
            message="Select a configuration key to delete:",
            choices=all_keys
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
