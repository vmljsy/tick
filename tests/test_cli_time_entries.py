from typer.testing import CliRunner
from src.tick_app.cli import app
from src.tick_app.services import project_service, time_entry_service
from datetime import datetime, timedelta, UTC
import pytz
from src.tick_app.config import get_user_timezone
from src.tick_app.utils import convert_utc_to_local, convert_local_to_utc

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

def test_logs_output_timezone_aware(cli_runner: CliRunner, db_session):
    p1 = project_service.create_project(db_session, "TZLogProject")
    # Log an entry in UTC
    time_entry_service.log_time(db_session, p1.id, datetime(2025, 8, 1, 9, 0, tzinfo=UTC), datetime(2025, 8, 1, 10, 0, tzinfo=UTC), "TZ Task")

    # Set a specific timezone for testing
    cli_runner.invoke(app, ["config", "set", "timezone", "America/Los_Angeles"])

    result = cli_runner.invoke(app, ["entry", "logs", "--project", "TZLogProject"])
    assert result.exit_code == 0

    # Expected local time (UTC 9:00-10:00 is PDT 2:00-3:00 on Aug 1)
    local_tz = pytz.timezone("America/Los_Angeles")
    expected_start_time = datetime(2025, 8, 1, 2, 0, tzinfo=local_tz).strftime("%Y-%m-%d %H:%M")
    expected_end_time = datetime(2025, 8, 1, 3, 0, tzinfo=local_tz).strftime("%Y-%m-%d %H:%M")

    assert expected_start_time[:13] in result.stdout
    assert expected_end_time[:13] in result.stdout

    # Reset timezone
    cli_runner.invoke(app, ["config", "set", "timezone", "UTC"])

def test_logs_date_filter_timezone_aware(cli_runner: CliRunner, db_session):
    p1 = project_service.create_project(db_session, "TZFilterProject")
    # Log an entry that spans across a day boundary in a different timezone
    # UTC: Aug 1 22:00 - Aug 2 02:00
    time_entry_service.log_time(db_session, p1.id, datetime(2025, 8, 1, 22, 0, tzinfo=UTC), datetime(2025, 8, 2, 2, 0, tzinfo=UTC), "Overnight Task")

    # Set timezone to America/New_York (UTC-4 in summer)
    # Local time: Aug 1 18:00 - Aug 1 22:00
    cli_runner.invoke(app, ["config", "set", "timezone", "America/New_York"])

    # Filter for Aug 1st (local time)
    result = cli_runner.invoke(app, ["entry", "logs", "--date", "2025-08-01", "--project", "TZFilterProject"])
    assert result.exit_code == 0
    assert "Overnight Task" in result.stdout # Should be included as it starts on Aug 1 local

    # Filter for Aug 2nd (local time)
    result = cli_runner.invoke(app, ["entry", "logs", "--date", "2025-08-02", "--project", "TZFilterProject"])
    assert result.exit_code == 0
    assert "No time entries found for the given criteria." in result.stdout # Should not be included as it ends on Aug 1 local

    # Reset timezone
    cli_runner.invoke(app, ["config", "set", "timezone", "UTC"])


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
    entry = time_entry_service.log_time(db_session, p1.id, datetime(2025, 8, 1, 9, 0, tzinfo=UTC), datetime(2025, 8, 1, 10, 0, tzinfo=UTC), "Original Desc")
    result = cli_runner.invoke(app, ["entry", "adjust", str(entry.id), "--desc", "New Description", "--duration", "2h"])
    assert result.exit_code == 0
    assert f"Time entry {entry.id} has been updated." in result.stdout.strip()
    updated_entry = time_entry_service.get_time_entry_by_id(db_session, entry.id)
    db_session.refresh(updated_entry) # Explicitly refresh the object
    assert updated_entry.description == "New Description"
    assert (updated_entry.end_time - updated_entry.start_time).total_seconds() == 7200 # 2 hours

def test_adjust_entry_timezone_aware(cli_runner: CliRunner, db_session):
    p1 = project_service.create_project(db_session, "AdjustTZProject")
    # Log an entry in UTC
    entry = time_entry_service.log_time(db_session, p1.id, datetime(2025, 8, 1, 12, 0, tzinfo=UTC), datetime(2025, 8, 1, 13, 0, tzinfo=UTC), "Original TZ Desc")

    # Set timezone to America/New_York (UTC-4 in summer)
    cli_runner.invoke(app, ["config", "set", "timezone", "America/New_York"])

    # Adjust using local times (e.g., 9 AM to 10 AM New York time)
    local_start_str = "2025-08-01 09:00"
    local_end_str = "2025-08-01 10:00"
    result = cli_runner.invoke(app, ["entry", "adjust", str(entry.id), "--start", local_start_str, "--end", local_end_str])
    assert result.exit_code == 0
    assert f"Time entry {entry.id} has been updated." in result.stdout.strip()

    updated_entry = time_entry_service.get_time_entry_by_id(db_session, entry.id)
    db_session.refresh(updated_entry)

    # Expected UTC times (New York 9 AM is UTC 1 PM, New York 10 AM is UTC 2 PM)
    expected_utc_start = datetime(2025, 8, 1, 13, 0)
    expected_utc_end = datetime(2025, 8, 1, 14, 0)

    assert updated_entry.start_time == expected_utc_start
    assert updated_entry.end_time == expected_utc_end

    # Reset timezone
    cli_runner.invoke(app, ["config", "set", "timezone", "UTC"])


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
