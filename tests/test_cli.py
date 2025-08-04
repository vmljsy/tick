from typer.testing import CliRunner
from src.tick_app.cli import app
from src.tick_app.services import project_service, time_entry_service
from datetime import datetime, timedelta

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

def test_start_timer_already_running(cli_runner: CliRunner, db_session):
    project_service.create_project(db_session, "ProjectA")
    project_service.create_project(db_session, "ProjectB")
    cli_runner.invoke(app, ["start", "ProjectA"])
    result = cli_runner.invoke(app, ["start", "ProjectB"], input="n\n") # Decline to stop
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
    result = cli_runner.invoke(app, ["log", "LoggedProject", "1h30m", "-d", "Manual log entry"])
    assert result.exit_code == 0
    assert "Logged 1h 30m 0s for project 'LoggedProject'." in result.stdout.strip()
    entries = time_entry_service.list_time_entries(db_session, project_id=project_service.get_project_by_name(db_session, "LoggedProject").id)
    assert len(entries) == 1
    assert entries[0].description == "Manual log entry"
    assert (entries[0].end_time - entries[0].start_time).total_seconds() == 5400 # 1h30m in seconds

def test_log_time_new_project(cli_runner: CliRunner, db_session):
    result = cli_runner.invoke(app, ["log", "NewLoggedProject", "2h", "-d", "Another log"], input="y\n")
    assert result.exit_code == 0
    assert "Project 'NewLoggedProject' created." in result.stdout.strip()
    assert "Logged 2h 0m 0s for project 'NewLoggedProject'." in result.stdout.strip()
    project = project_service.get_project_by_name(db_session, "NewLoggedProject")
    assert project is not None
    entries = time_entry_service.list_time_entries(db_session, project_id=project.id)
    assert len(entries) == 1
    assert (entries[0].end_time - entries[0].start_time).total_seconds() == 7200 # 2h in seconds
