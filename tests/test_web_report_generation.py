"""Test to verify web report generation handles empty project_id correctly."""
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


def test_report_generation_with_empty_project_id(client):
    """Test that report generation works when project_id is empty string."""
    # First create a project and time entry
    db = next(get_db())
    
    # Create a project
    project = project_service.create_project(db, "Test Project")
    
    # Create a completed time entry
    start = datetime.now(UTC) - timedelta(hours=2)
    end = datetime.now(UTC) - timedelta(hours=1)
    time_entry_service.log_time(db, project.id, start, end, "Test entry")
    
    # Submit report generation with empty project_id (simulating form submission)
    response = client.post("/reports/generate", data={
        "period": "week",
        "project_id": "",  # Empty string, simulating unselected dropdown
        "group_by": "project"
    })
    
    # Should not return 422 error
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Verify the page content contains expected elements
    assert "Test Project" in response.text
    
    print("✅ Report generation works with empty project_id!")


def test_report_generation_with_valid_project_id(client):
    """Test that report generation works when project_id is provided."""
    # First create a project and time entry
    db = next(get_db())
    
    # Create a project
    project = project_service.create_project(db, "Test Project")
    
    # Create a completed time entry
    start = datetime.now(UTC) - timedelta(hours=2)
    end = datetime.now(UTC) - timedelta(hours=1)
    time_entry_service.log_time(db, project.id, start, end, "Test entry")
    
    # Submit report generation with valid project_id
    response = client.post("/reports/generate", data={
        "period": "week",
        "project_id": str(project.id),
        "group_by": "project"
    })
    
    # Should return 200
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Verify the page content contains expected elements
    assert "Test Project" in response.text
    
    print("✅ Report generation works with valid project_id!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
