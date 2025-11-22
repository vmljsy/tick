from typer.testing import CliRunner
from src.tick_app.cli import app
from src.tick_app.services.config_service import config_service
from src.tick_app import config as app_config # Import the config module
import os
import tempfile
from pathlib import Path

def test_config_set_get_list_delete(cli_runner: CliRunner, monkeypatch):
    # Use a temporary config file for testing
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        temp_config_path = Path(tmp_file.name)
    
    # Monkeypatch the CONFIG_PATH in the actual config module
    monkeypatch.setattr(app_config, 'CONFIG_PATH', temp_config_path)

    # Re-initialize config_service to load the new path
    monkeypatch.setattr(config_service, '_config', config_service._load_config())

    # Test set command
    result = cli_runner.invoke(app, ["config", "set", "timezone", "America/New_York"])
    assert result.exit_code == 0
    assert "Configuration key 'timezone' set to 'America/New_York'." in result.stdout.strip()
    assert config_service.get("timezone") == "America/New_York"

    # Test get command
    result = cli_runner.invoke(app, ["config", "get", "timezone"])
    assert result.exit_code == 0
    assert "timezone = America/New_York" in result.stdout.strip()

    # Test list command
    result = cli_runner.invoke(app, ["config", "list"])
    assert result.exit_code == 0
    assert "timezone" in result.stdout.strip()
    assert "America/New_York" in result.stdout.strip()

    # Test delete command
    result = cli_runner.invoke(app, ["config", "delete", "timezone"])
    assert result.exit_code == 0
    assert "Configuration key 'timezone' deleted." in result.stdout.strip()
    assert config_service.get("timezone") is None

    # Test get non-existent key
    result = cli_runner.invoke(app, ["config", "get", "non_existent_key"])
    assert result.exit_code == 1
    assert "Configuration key 'non_existent_key' not found." in result.stdout.strip()

    # Test delete non-existent key
    result = cli_runner.invoke(app, ["config", "delete", "non_existent_key"])
    assert result.exit_code == 1
    assert "Configuration key 'non_existent_key' not found." in result.stdout.strip()

    # Clean up the temporary file
    os.unlink(temp_config_path)