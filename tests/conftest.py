import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock, patch

from src.tick_app.database import Base, get_db_manager, DatabaseManager

@pytest.fixture(scope="function", autouse=True)
def reset_db_manager(monkeypatch):
    """Reset the global database manager before each test"""
    import src.tick_app.database as db_module
    db_module._db_manager = None
    yield
    db_module._db_manager = None

@pytest.fixture(name="db_session")
def db_session_fixture(monkeypatch, reset_db_manager):
    # Use an in-memory SQLite database for testing
    test_db_url = "sqlite:///:memory:"

    # Create a test database manager
    test_manager = DatabaseManager(test_db_url)
    
    # Re-create engine with StaticPool for in-memory DB
    test_manager.engine = create_engine(
        test_db_url, 
        connect_args={"check_same_thread": False}, 
        poolclass=StaticPool
    )
    test_manager.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_manager.engine)
    
    # Create tables
    test_manager.init_db()

    # Monkeypatch the global get_db_manager to return our test manager
    monkeypatch.setattr("src.tick_app.database.get_db_manager", lambda db_url=None: test_manager)
    
    # Also set the global _db_manager directly
    import src.tick_app.database as db_module
    db_module._db_manager = test_manager

    # Get a session
    db = next(test_manager.get_db())
    try:
        yield db
    finally:
        db.close()
        # Clean up
        Base.metadata.drop_all(bind=test_manager.engine)
        test_manager.engine.dispose()

@pytest.fixture(name="cli_runner")
def cli_runner_fixture(db_session, monkeypatch):
    from typer.testing import CliRunner
    runner = CliRunner()
    
    # Monkeypatch get_db to return the test database session
    def get_test_db_override():
        yield db_session

    monkeypatch.setattr("src.tick_app.database.get_db", get_test_db_override)
    
    # Mock InquirerPy prompts to avoid Windows console issues
    # We'll mock the functions to return sensible defaults
    mock_confirm = MagicMock(return_value=MagicMock(execute=MagicMock(return_value=True)))
    mock_text = MagicMock(return_value=MagicMock(execute=MagicMock(return_value="")))
    mock_select = MagicMock(return_value=MagicMock(execute=MagicMock(return_value=None)))
    
    monkeypatch.setattr("InquirerPy.inquirer.confirm", mock_confirm)
    monkeypatch.setattr("InquirerPy.inquirer.text", mock_text)
    monkeypatch.setattr("InquirerPy.inquirer.select", mock_select)

    yield runner