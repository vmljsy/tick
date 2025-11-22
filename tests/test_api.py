from fastapi.testclient import TestClient
from api.main import app
from src.tick_app.database import get_db
import pytest

client = TestClient(app)

@pytest.fixture
def override_get_db(db_session):
    def _get_db():
        yield db_session
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides = {}

def test_create_project(override_get_db):
    response = client.post(
        "/api/v1/projects",
        json={"name": "Test Project", "tags": ["tag1", "tag2"]}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["id"] is not None

def test_list_projects(override_get_db):
    client.post("/api/v1/projects", json={"name": "Project A"})
    client.post("/api/v1/projects", json={"name": "Project B"})
    
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_get_project(override_get_db):
    response = client.post("/api/v1/projects", json={"name": "Project C"})
    project_id = response.json()["id"]
    
    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Project C"

def test_update_project(override_get_db):
    response = client.post("/api/v1/projects", json={"name": "Project D"})
    project_id = response.json()["id"]
    
    response = client.put(f"/api/v1/projects/{project_id}", json={"name": "Project D Updated"})
    assert response.status_code == 200
    assert response.json()["name"] == "Project D Updated"

def test_delete_project(override_get_db):
    response = client.post("/api/v1/projects", json={"name": "Project E"})
    project_id = response.json()["id"]
    
    response = client.delete(f"/api/v1/projects/{project_id}")
    assert response.status_code == 204
    
    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 404

def test_log_time_entry(override_get_db):
    p_response = client.post("/api/v1/projects", json={"name": "Time Project"})
    project_id = p_response.json()["id"]
    
    response = client.post(
        "/api/v1/entries",
        json={
            "project_id": project_id,
            "start_time": "2023-10-27T10:00:00",
            "end_time": "2023-10-27T11:00:00",
            "description": "Test Entry"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Test Entry"
    assert data["project"]["id"] == project_id

def test_start_stop_timer(override_get_db):
    p_response = client.post("/api/v1/projects", json={"name": "Timer Project"})
    project_id = p_response.json()["id"]
    
    # Start
    response = client.post(
        "/api/v1/entries/start",
        json={"project_id": project_id, "description": "Running Timer"}
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Running Timer"
    
    # Check current
    response = client.get("/api/v1/entries/current")
    assert response.status_code == 200
    assert response.json()["description"] == "Running Timer"
    
    # Stop
    response = client.post("/api/v1/entries/stop")
    assert response.status_code == 200
    assert response.json()["end_time"] is not None

def test_config_endpoints(override_get_db):
    # Set
    response = client.post("/api/v1/config", json={"key": "test_key", "value": "test_val"})
    assert response.status_code == 200
    
    # Get
    response = client.get("/api/v1/config")
    assert response.status_code == 200
    assert response.json()["test_key"] == "test_val"
    
    # Delete
    response = client.delete("/api/v1/config/test_key")
    assert response.status_code == 204
    
    response = client.get("/api/v1/config")
    assert "test_key" not in response.json()
