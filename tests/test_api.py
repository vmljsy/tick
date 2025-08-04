from fastapi.testclient import TestClient
from src.tick_app.database import get_db, Base
from src.tick_app.services import project_service, time_entry_service
from api.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

# Setup in-memory SQLite for API tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="api_db_session")
def api_db_session_fixture():
    # Create tables for each test
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after each test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="test_client")
def test_client_fixture(api_db_session):
    def override_get_db():
        yield api_db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear() # Clear overrides after the test

# Update tests to use test_client fixture
def test_dashboard_page(test_client: TestClient):
    response = test_client.get("/")
    assert response.status_code == 200
    assert "Tick" in response.text
    assert "Current Timer" in response.text
    assert "Recent Logs" in response.text

def test_start_timer_web(test_client: TestClient, api_db_session):
    # Create a project first using the session from the fixture
    project = project_service.create_project(api_db_session, "WebProject")

    response = test_client.post("/start-timer", data={"project_id": project.id, "description": "Web task"})
    assert response.status_code == 303 # Redirect
    assert response.headers["location"] == "/"

    # Verify timer started using the same session
    running_entry = time_entry_service.get_current_running_entry(api_db_session)
    assert running_entry is not None
    assert running_entry.project.name == "WebProject"

def test_stop_timer_web(test_client: TestClient, api_db_session):
    # Start a timer first
    project = project_service.create_project(api_db_session, "StopWebProject")
    time_entry_service.start_timer(api_db_session, project.id)

    response = test_client.post("/stop-timer")
    assert response.status_code == 303 # Redirect
    assert response.headers["location"] == "/"

    # Verify timer stopped
    running_entry = time_entry_service.get_current_running_entry(api_db_session)
    assert running_entry is None

def test_list_logs_web(test_client: TestClient, api_db_session):
    response = test_client.get("/logs")
    assert response.status_code == 200
    assert "Time Logs" in response.text

def test_list_projects_web(test_client: TestClient, api_db_session):
    response = test_client.get("/projects")
    assert response.status_code == 200
    assert "Projects" in response.text

def test_add_project_web(test_client: TestClient, api_db_session):
    response = test_client.post("/projects/add", data={"name": "NewWebProject"})
    assert response.status_code == 303
    assert response.headers["location"] == "/projects"

    project = project_service.get_project_by_name(api_db_session, "NewWebProject")
    assert project is not None

def test_edit_project_web(test_client: TestClient, api_db_session):
    project = project_service.create_project(api_db_session, "EditWebProject")

    response = test_client.post(f"/projects/edit/{project.id}", data={"name": "EditedWebProject"})
    assert response.status_code == 303
    assert response.headers["location"] == "/projects"

    edited_project = project_service.get_project_by_id(api_db_session, project.id)
    assert edited_project.name == "EditedWebProject"

def test_reports_web(test_client: TestClient, api_db_session):
    response = test_client.get("/reports")
    assert response.status_code == 200
    assert "Reports" in response.text