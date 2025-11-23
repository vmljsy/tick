import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from tick_app.cli import app

runner = CliRunner()

@patch("tick_app.cli_web.uvicorn.run")
@patch("tick_app.cli_web.webbrowser.open")
@patch("tick_app.cli_web.get_config_value")
def test_web_start_default(mock_get_config, mock_browser, mock_uvicorn):
    mock_get_config.return_value = None
    result = runner.invoke(app, ["web", "start"])
    assert result.exit_code == 0
    assert "Starting web interface at http://localhost:8000" in result.stdout
    mock_browser.assert_called_once_with("http://localhost:8000")
    mock_uvicorn.assert_called_once_with("tick_app.api.main:app", host="0.0.0.0", port=8000, reload=False)

@patch("tick_app.cli_web.uvicorn.run")
@patch("tick_app.cli_web.webbrowser.open")
@patch("tick_app.cli_web.get_config_value")
def test_web_start_config_port(mock_get_config, mock_browser, mock_uvicorn):
    mock_get_config.return_value = "9090"
    result = runner.invoke(app, ["web", "start"])
    assert result.exit_code == 0
    assert "Starting web interface at http://localhost:9090" in result.stdout
    mock_browser.assert_called_once_with("http://localhost:9090")
    mock_uvicorn.assert_called_once_with("tick_app.api.main:app", host="0.0.0.0", port=9090, reload=False)

@patch("tick_app.cli_web.uvicorn.run")
@patch("tick_app.cli_web.webbrowser.open")
@patch("tick_app.cli_web.get_config_value")
def test_web_start_override_port(mock_get_config, mock_browser, mock_uvicorn):
    mock_get_config.return_value = "9090"
    result = runner.invoke(app, ["web", "start", "--port", "7000"])
    assert result.exit_code == 0
    assert "Starting web interface at http://localhost:7000" in result.stdout
    mock_browser.assert_called_once_with("http://localhost:7000")
    mock_uvicorn.assert_called_once_with("tick_app.api.main:app", host="0.0.0.0", port=7000, reload=False)

@patch("tick_app.cli_web.uvicorn.run")
@patch("tick_app.cli_web.webbrowser.open")
@patch("tick_app.cli_web.get_config_value")
def test_web_start_invalid_config_port(mock_get_config, mock_browser, mock_uvicorn):
    mock_get_config.return_value = "invalid"
    result = runner.invoke(app, ["web", "start"])
    assert result.exit_code == 0
    assert "Invalid port in config: invalid. Using default 8000." in result.stdout
    mock_browser.assert_called_once_with("http://localhost:8000")
    mock_uvicorn.assert_called_once_with("tick_app.api.main:app", host="0.0.0.0", port=8000, reload=False)
