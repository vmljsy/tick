from typer.testing import CliRunner
from src.tick_app.cli import app
from src.tick_app.services import project_service, time_entry_service
from datetime import datetime, timedelta, UTC
import pytz
from src.tick_app.config import get_user_timezone
from src.tick_app.utils import convert_utc_to_local

def setup_report_entries(db_session):
    p1 = project_service.create_project(db_session, "ReportProject1")
    p2 = project_service.create_project(db_session, "ReportProject2")
    # Entries for today
    time_entry_service.log_time(db_session, p1.id, datetime.now(UTC) - timedelta(minutes=30), datetime.now(UTC), "Today Task 1")
    time_entry_service.log_time(db_session, p2.id, datetime.now(UTC) - timedelta(minutes=60), datetime.now(UTC) - timedelta(minutes=30), "Today Task 2")
    # Entry for yesterday
    time_entry_service.log_time(db_session, p1.id, datetime.now(UTC) - timedelta(days=1, hours=2), datetime.now(UTC) - timedelta(days=1, hours=1), "Yesterday Task")

def test_report_generate_day(cli_runner: CliRunner, db_session):
    setup_report_entries(db_session)
    result = cli_runner.invoke(app, ["report", "generate", "--day", "--group-by", "day"])
    assert result.exit_code == 0
    assert "Time Report (Grouped by day)" in result.stdout.strip()
    assert datetime.now(UTC).strftime("%Y-%m-%d") in result.stdout.strip()
    assert "TOTAL" in result.stdout.strip()

def test_report_generate_project_grouping(cli_runner: CliRunner, db_session):
    setup_report_entries(db_session)
    result = cli_runner.invoke(app, ["report", "generate", "--group-by", "project"])
    assert result.exit_code == 0
    assert "Time Report (Grouped by project)" in result.stdout.strip()
    assert "ReportProject1" in result.stdout.strip()
    assert "ReportProject2" in result.stdout.strip()
    assert "TOTAL" in result.stdout.strip()

def test_report_generate_timezone_aware(cli_runner: CliRunner, db_session):
    p1 = project_service.create_project(db_session, "TZReportProject")
    # Log an entry in UTC
    time_entry_service.log_time(db_session, p1.id, datetime(2025, 8, 1, 12, 0, tzinfo=UTC), datetime(2025, 8, 1, 13, 0, tzinfo=UTC), "TZ Report Task")

    # Set timezone to America/New_York (UTC-4 in summer)
    cli_runner.invoke(app, ["config", "set", "timezone", "America/New_York"])

    # Generate report for the day (local time)
    result = cli_runner.invoke(app, ["report", "generate", "--start-date", "2025-08-01", "--end-date", "2025-08-01", "--group-by", "day"])
    assert result.exit_code == 0

    # Expected local date (UTC Aug 1 is PDT Aug 1)
    local_tz = pytz.timezone("America/New_York")
    expected_date_str = datetime(2025, 8, 1, tzinfo=local_tz).strftime("%Y-%m-%d")
    assert expected_date_str in result.stdout
    assert "TZ Report Task" in result.stdout # Should still show the task

    # Reset timezone
    cli_runner.invoke(app, ["config", "set", "timezone", "UTC"])

def test_report_generate_no_data(cli_runner: CliRunner, db_session):
    result = cli_runner.invoke(app, ["report", "generate", "--day", "--group-by", "day"])
    assert result.exit_code == 0 # Should exit with 0 if no data found
    assert "No data found for the given report criteria." in result.stdout.strip()
