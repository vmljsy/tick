from typer.testing import CliRunner
from src.tick_app.cli import app
from src.tick_app.services import project_service, time_entry_service
from datetime import datetime, timedelta, UTC

def setup_entries(db_session):
    p1 = project_service.create_project(db_session, "ProjectA")
    p2 = project_service.create_project(db_session, "ProjectB")
    time_entry_service.log_time(db_session, p1.id, datetime(2025, 8, 1, 9, 0), datetime(2025, 8, 1, 10, 0), "Task 1")
    time_entry_service.log_time(db_session, p2.id, datetime(2025, 8, 1, 10, 0), datetime(2025, 8, 1, 11, 30), "Task 2")
    time_entry_service.log_time(db_session, p1.id, datetime(2025, 8, 2, 14, 0), datetime(2025, 8, 2, 15, 0), "Task 3")
    time_entry_service.log_time(db_session, p2.id, datetime(2025, 8, 3, 9, 0), datetime(2025, 8, 3, 10, 0), "Task 4")

def test_logs_all(cli_runner: CliRunner, db_session):
    setup_entries(db_session)
    result = cli_runner.invoke(app, ["entry", "logs"])
    assert result.exit_code == 0
    assert "Task 1" in result.stdout.strip()
    assert "Task 4" in result.stdout.strip()
    assert "ProjectA" in result.stdout.strip()
    assert "ProjectB" in result.stdout.strip()

def test_logs_filter_date(cli_runner: CliRunner, db_session):
    setup_entries(db_session)
    result = cli_runner.invoke(app, ["entry", "logs", "--date", "2025-08-01"])
    assert result.exit_code == 0
    assert "Task 1" in result.stdout.strip()
    assert "Task 2" in result.stdout.strip()
    assert "Task 3" not in result.stdout.strip()

def test_logs_filter_project(cli_runner: CliRunner, db_session):
    setup_entries(db_session)
    result = cli_runner.invoke(app, ["entry", "logs", "--project", "ProjectA"])
    assert result.exit_code == 0
    assert "Task 1" in result.stdout.strip()
    assert "Task 3" in result.stdout.strip()
    assert "Task 2" not in result.stdout.strip()

def test_adjust_entry(cli_runner: CliRunner, db_session):
    p1 = project_service.create_project(db_session, "AdjustProject")
    entry = time_entry_service.log_time(db_session, p1.id, datetime(2025, 8, 1, 9, 0), datetime(2025, 8, 1, 10, 0), "Original Desc")
    result = cli_runner.invoke(app, ["entry", "adjust", str(entry.id), "--desc", "New Description", "--duration", "2h"])
    assert result.exit_code == 0
    assert f"Time entry {entry.id} has been updated." in result.stdout.strip()
    updated_entry = time_entry_service.get_time_entry_by_id(db_session, entry.id)
    db_session.refresh(updated_entry) # Explicitly refresh the object
    assert updated_entry.description == "New Description"
    assert (updated_entry.end_time - updated_entry.start_time).total_seconds() == 7200 # 2 hours

def test_delete_entry(cli_runner: CliRunner, db_session):
    p1 = project_service.create_project(db_session, "DeleteProject")
    entry = time_entry_service.log_time(db_session, p1.id, datetime(2025, 8, 1, 9, 0), datetime(2025, 8, 1, 10, 0), "To Delete")
    result = cli_runner.invoke(app, ["entry", "delete", str(entry.id)], input="y\n")
    assert result.exit_code == 0
    assert f"Time entry {entry.id} has been deleted." in result.stdout.strip()
    assert time_entry_service.get_time_entry_by_id(db_session, entry.id) is None

def test_show_all_head(cli_runner: CliRunner, db_session):
    setup_entries(db_session)
    result = cli_runner.invoke(app, ["entry", "show-all", "--head", "2"])
    assert result.exit_code == 0
    assert "Task 1" in result.stdout.strip()
    assert "Task 2" in result.stdout.strip()
    assert "Task 3" not in result.stdout.strip()

def test_show_all_tail(cli_runner: CliRunner, db_session):
    setup_entries(db_session)
    result = cli_runner.invoke(app, ["entry", "show-all", "--tail", "2"])
    assert result.exit_code == 0
    assert "Task 3" in result.stdout.strip()
    assert "Task 4" in result.stdout.strip()
    assert "Task 1" not in result.stdout.strip()

def test_show_all_head_and_tail_error(cli_runner: CliRunner, db_session):
    result = cli_runner.invoke(app, ["entry", "show-all", "--head", "1", "--tail", "1"])
    assert result.exit_code == 1
    assert "Cannot use --head and --tail together." in result.stdout.strip()
