"""Test to verify web templates render correctly with Jinja2 globals."""
from fastapi.testclient import TestClient
from tick_app.api.main import app
from tick_app.database import get_db, Base, engine
from tick_app.services import project_service, time_entry_service
from datetime import datetime, timedelta, UTC
import pytest


@pytest.fixture
def client():
    """Create a test client."""
    # Setup test database
    Base.metadata.create_all(bind=engine)
    
    client = TestClient(app)
    yield client
    
    # Teardown
    Base.metadata.drop_all(bind=engine)


def test_logs_page_renders_with_format_duration(client):
    """Test that the logs page renders correctly with format_duration."""
    # First create a project and time entry
    db = next(get_db())
    
    # Create a project
    project = project_service.create_project(db, "Test Project")
    
    # Create a completed time entry
    start = datetime.now(UTC) - timedelta(hours=2)
    end = datetime.now(UTC) - timedelta(hours=1)
    time_entry_service.log_time(db, project.id, start, end, "Test entry")
    
    # Now test the logs page
    response = client.get("/logs")
    
    # Verify the response is successful
    assert response.status_code == 200
    
    # Verify the page content contains expected elements
    assert "Test Project" in response.text
    assert "Test entry" in response.text
    
    # The page should not show undefined error
    assert "UndefinedError" not in response.text
    assert "'format_duration' is undefined" not in response.text
    
    print("✅ Logs page renders successfully with format_duration!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
