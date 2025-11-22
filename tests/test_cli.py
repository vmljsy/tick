from typer.testing import CliRunner
from src.tick_app.cli import app
from src.tick_app.services import project_service, time_entry_service
from datetime import datetime, timedelta, UTC
import pytz
from src.tick_app.config import get_user_timezone
from src.tick_app.utils import convert_utc_to_local

def test_app_help(cli_runner: CliRunner):
    result = cli_runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Tick: A command-line time tracking tool." in result.stdout

def test_start_timer_new_project(cli_runner: CliRunner, db_session):
    result = cli_runner.invoke(app, ["start", "NewProject"], input="y\n")
    assert result.exit_code == 0
    assert "Project 'NewProject' created." in result.stdout.strip()
    assert "Timer started for project 'NewProject'" in result.stdout.strip()
    project = project_service.get_project_by_name(db_session, "NewProject")
    assert project is not None
    running_entry = time_entry_service.get_current_running_entry(db_session)
    assert running_entry is not None
    assert running_entry.project_id == project.id

def test_start_timer_existing_project(cli_runner: CliRunner, db_session):
    project_service.create_project(db_session, "ExistingProject")
    result = cli_runner.invoke(app, ["start", "ExistingProject"])
    assert result.exit_code == 0
    assert "Timer started for project 'ExistingProject'" in result.stdout.strip()

def test_start_timer_already_running(cli_runner: CliRunner, db_session, monkeypatch):
    from unittest.mock import MagicMock
    project_service.create_project(db_session, "ProjectA")
    project_service.create_project(db_session, "ProjectB")
    cli_runner.invoke(app, ["start", "ProjectA"])
    
    # Mock confirm to return False (decline to stop)
    mock_confirm = MagicMock(return_value=MagicMock(execute=MagicMock(return_value=False)))
    monkeypatch.setattr("InquirerPy.inquirer.confirm", mock_confirm)
    
    result = cli_runner.invoke(app, ["start", "ProjectB"]) # Input is ignored by mock
    assert result.exit_code == 1
    assert "A timer is already running for project 'ProjectA'" in result.stdout.strip()
    assert "Operation cancelled." in result.stdout.strip()

def test_start_timer_stop_and_start_new(cli_runner: CliRunner, db_session):
    project_service.create_project(db_session, "ProjectX")
    project_service.create_project(db_session, "ProjectY")
    cli_runner.invoke(app, ["start", "ProjectX"])
    result = cli_runner.invoke(app, ["start", "ProjectY"], input="y\n") # Confirm to stop
    assert result.exit_code == 0
    assert "Timer for 'ProjectX' stopped." in result.stdout.strip()
    assert "Timer started for project 'ProjectY'" in result.stdout.strip()
    assert time_entry_service.get_current_running_entry(db_session).project.name == "ProjectY"

def test_stop_timer(cli_runner: CliRunner, db_session):
    project = project_service.create_project(db_session, "StopProject")
    time_entry_service.start_timer(db_session, project.id)
    result = cli_runner.invoke(app, ["stop"])
    assert result.exit_code == 0
    assert "Timer stopped for project 'StopProject'." in result.stdout.strip()
    assert time_entry_service.get_current_running_entry(db_session) is None

def test_stop_timer_no_running(cli_runner: CliRunner):
    result = cli_runner.invoke(app, ["stop"])
    assert result.exit_code == 1
    assert "No timer is currently running." in result.stdout.strip()

def test_status_running(cli_runner: CliRunner, db_session):
    project = project_service.create_project(db_session, "StatusProject")
    time_entry_service.start_timer(db_session, project.id, "Doing something")
    result = cli_runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "A timer is running for project 'StatusProject'." in result.stdout.strip()
    assert "Description: Doing something" in result.stdout.strip()

def test_status_no_running(cli_runner: CliRunner):
    result = cli_runner.invoke(app, ["status"])
    assert result.exit_code == 0 # Exit code 0 for no running timer is acceptable
    assert "No timer is currently running." in result.stdout.strip()

def test_log_time(cli_runner: CliRunner, db_session):
    project_service.create_project(db_session, "LoggedProject")
    result = cli_runner.invoke(app, ["log", "LoggedProject", "--duration", "1h30m", "-d", "Manual log entry"])
    assert result.exit_code == 0
    assert "Logged 1h 30m 0s for project 'LoggedProject'." in result.stdout.strip()
    entries = time_entry_service.list_time_entries(db_session, project_id=project_service.get_project_by_name(db_session, "LoggedProject").id)
    assert len(entries) == 1
    assert entries[0].description == "Manual log entry"
    assert (entries[0].end_time - entries[0].start_time).total_seconds() == 5400 # 1h30m in seconds

def test_log_time_new_project(cli_runner: CliRunner, db_session):
    result = cli_runner.invoke(app, ["log", "NewLoggedProject", "--duration", "2h", "-d", "Another log"], input="y\n")
    assert result.exit_code == 0
    assert "Project 'NewLoggedProject' created." in result.stdout.strip()
    assert "Logged 2h 0m 0s for project 'NewLoggedProject'." in result.stdout.strip()
    project = project_service.get_project_by_name(db_session, "NewLoggedProject")
    assert project is not None
    entries = time_entry_service.list_time_entries(db_session, project_id=project.id)
    assert len(entries) == 1
    assert (entries[0].end_time - entries[0].start_time).total_seconds() == 7200 # 2h in seconds

def test_config_set_and_get_timezone(cli_runner: CliRunner, db_session):
    # Set a timezone
    result = cli_runner.invoke(app, ["config", "set", "timezone", "America/New_York"])
    assert result.exit_code == 0
    assert "Configuration key 'timezone' set to 'America/New_York'." in result.stdout

    # Get the timezone
    result = cli_runner.invoke(app, ["config", "get", "timezone"])
    assert result.exit_code == 0
    assert "timezone = America/New_York" in result.stdout

    # Reset to default (or another timezone)
    result = cli_runner.invoke(app, ["config", "set", "timezone", "UTC"])
    assert result.exit_code == 0
    assert "Configuration key 'timezone' set to 'UTC'." in result.stdout

def test_start_timer_output_timezone_aware(cli_runner: CliRunner, db_session):
    project_service.create_project(db_session, "TZProject")
    
    # Set a specific timezone for testing
    cli_runner.invoke(app, ["config", "set", "timezone", "America/Los_Angeles"])

    result = cli_runner.invoke(app, ["start", "TZProject"])
    assert result.exit_code == 0
    
    # Get the current time in the configured timezone
    local_tz = pytz.timezone("America/Los_Angeles")
    expected_time_str = datetime.now(local_tz).strftime('%H:%M:%S')
    
    # Check if the output contains the timezone-aware time
    assert f"Timer started for project 'TZProject' at {expected_time_str[:5]}" in result.stdout # Check first few chars due to potential second differences

    # Reset timezone
    cli_runner.invoke(app, ["config", "set", "timezone", "UTC"])

def test_stop_timer_output_timezone_aware(cli_runner: CliRunner, db_session):
    project = project_service.create_project(db_session, "StopTZProject")
    time_entry_service.start_timer(db_session, project.id)

    # Set a specific timezone for testing
    cli_runner.invoke(app, ["config", "set", "timezone", "Europe/Berlin"])

    result = cli_runner.invoke(app, ["stop"])
    assert result.exit_code == 0
    assert "Timer stopped for project 'StopTZProject'." in result.stdout
    assert "Logged" in result.stdout # Check for duration

    # Reset timezone
    cli_runner.invoke(app, ["config", "set", "timezone", "UTC"])

def test_status_output_timezone_aware(cli_runner: CliRunner, db_session):
    project = project_service.create_project(db_session, "StatusTZProject")
    time_entry_service.start_timer(db_session, project.id)

    # Set a specific timezone for testing
    cli_runner.invoke(app, ["config", "set", "timezone", "Asia/Tokyo"])

    result = cli_runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "A timer is running for project 'StatusTZProject'." in result.stdout
    
    # Get the current time in the configured timezone
    local_tz = pytz.timezone("Asia/Tokyo")
    expected_time_str = datetime.now(local_tz).strftime('%H:%M:%S')

    assert f"Started at: {expected_time_str[:7]}" in result.stdout # Check first few chars due to potential second differences

    # Reset timezone
    cli_runner.invoke(app, ["config", "set", "timezone", "UTC"])

def test_log_time_output_timezone_aware(cli_runner: CliRunner, db_session):
    project_service.create_project(db_session, "LogTZProject")

    # Set a specific timezone for testing
    cli_runner.invoke(app, ["config", "set", "timezone", "America/New_York"])

    result = cli_runner.invoke(app, ["log", "LogTZProject", "--duration", "1h"])
    assert result.exit_code == 0
    assert "Logged 1h 0m 0s for project 'LogTZProject'." in result.stdout

    # Test with explicit start/end times
    start_dt_str = "2025-01-01 09:00"
    end_dt_str = "2025-01-01 10:00"
    result = cli_runner.invoke(app, ["log", "LogTZProject", "--start", start_dt_str, "--end", end_dt_str])
    assert result.exit_code == 0
    assert "Logged 1h 0m 0s for project 'LogTZProject'." in result.stdout

    # Reset timezone
    cli_runner.invoke(app, ["config", "set", "timezone", "UTC"])

def test_cli_commands_run_without_error(cli_runner: CliRunner, db_session):
    # Test project add
    result = cli_runner.invoke(app, ["project", "add", "TestProjectFromCLI"], input="y\n")
    assert result.exit_code == 0, f"project add failed: {result.stdout}"
    assert "Project 'TestProjectFromCLI' has been created." in result.stdout

    # Test start timer
    result = cli_runner.invoke(app, ["start", "TestProjectFromCLI"])
    assert result.exit_code == 0, f"start failed: {result.stdout}"
    assert "Timer started for project 'TestProjectFromCLI'" in result.stdout

    # Test status
    result = cli_runner.invoke(app, ["status"])
    assert result.exit_code == 0, f"status failed: {result.stdout}"
    assert "A timer is running for project 'TestProjectFromCLI'" in result.stdout

    # Test stop timer
    result = cli_runner.invoke(app, ["stop"])
    assert result.exit_code == 0, f"stop failed: {result.stdout}"
    assert "Timer stopped for project 'TestProjectFromCLI'." in result.stdout

    # Test log time (new project creation)
    result = cli_runner.invoke(app, ["log", "AnotherProjectFromCLI", "--duration", "1h", "-d", "Logged from test"], input="y\n")
    assert result.exit_code == 0, f"log new project failed: {result.stdout}"
    assert "Project 'AnotherProjectFromCLI' created." in result.stdout
    assert "Logged 1h 0m 0s for project 'AnotherProjectFromCLI'." in result.stdout

    # Test project list
    result = cli_runner.invoke(app, ["project", "list"])
    assert result.exit_code == 0, f"project list failed: {result.stdout}"
    assert "TestProjectFromCLI" in result.stdout
    assert "AnotherProjectFromCLI" in result.stdout

    # Test config set
    result = cli_runner.invoke(app, ["config", "set", "test_key", "test_value"])
    assert result.exit_code == 0, f"config set failed: {result.stdout}"
    assert "Configuration key 'test_key' set to 'test_value'." in result.stdout

    # Test config get
    result = cli_runner.invoke(app, ["config", "get", "test_key"])
    assert result.exit_code == 0, f"config get failed: {result.stdout}"
    assert "test_key = test_value" in result.stdout

    # Test config list
    result = cli_runner.invoke(app, ["config", "list"])
    assert result.exit_code == 0, f"config list failed: {result.stdout}"
    assert "test_key" in result.stdout
    assert "test_value" in result.stdout

    # Test config delete
    result = cli_runner.invoke(app, ["config", "delete", "test_key"])
    assert result.exit_code == 0, f"config delete failed: {result.stdout}"
    assert "Configuration key 'test_key' deleted." in result.stdout

    # Test report generate (default grouping)
    result = cli_runner.invoke(app, ["report", "generate", "--day"])
    assert result.exit_code == 0, f"report generate --day failed: {result.stdout}"
    assert "Time Report (Grouped by project)" in result.stdout # Default grouping
    assert "TestProjectFromCLI" in result.stdout or "AnotherProjectFromCLI" in result.stdout

    # Test report generate (explicit day grouping)
    result = cli_runner.invoke(app, ["report", "generate", "--day", "--group-by", "day"])
    assert result.exit_code == 0, f"report generate --day --group-by day failed: {result.stdout}"
    assert "Time Report (Grouped by day)" in result.stdout
    assert datetime.now(UTC).strftime("%Y-%m-%d") in result.stdout # Check for current date in report
