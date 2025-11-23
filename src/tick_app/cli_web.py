import typer
import uvicorn
import webbrowser
from rich.console import Console
from typing import Optional

from .config import get_config_value

app = typer.Typer(rich_markup_mode="markdown", name="web", no_args_is_help=True)
console = Console()

@app.command("start")
def start_web(
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Port to run the web server on."),
):
    """
    Starts the web interface.
    """
    if port is None:
        config_port = get_config_value("web_port")
        if config_port:
            try:
                port = int(config_port)
            except ValueError:
                console.print(f"[bold red]Error:[/bold red] Invalid port in config: {config_port}. Using default 8000.")
                port = 8000
        else:
            port = 8000

    url = f"http://localhost:{port}"
    console.print(f"Starting web interface at [bold green]{url}[/bold green]...")
    
    # Open browser in a separate thread/process or just before blocking call
    webbrowser.open(url)
    
    # Run the server
    # We use "api.main:app" string to enable reload if needed, but here we import directly or use string
    # Using string requires running from root or having api in pythonpath
    # Since we are in cli, we might need to adjust pythonpath or import app directly
    
    try:
        uvicorn.run("tick_app.api.main:app", host="0.0.0.0", port=port, reload=False)
    except Exception as e:
        console.print(f"[bold red]Error starting server:[/bold red] {e}")
