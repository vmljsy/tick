import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.tick_app.database import Base, get_db, configure_db, engine, SessionLocal
from src.tick_app.cli import app as cli_app

@pytest.fixture(name="db_session")
def db_session_fixture(monkeypatch):
    # Use an in-memory SQLite database for testing
    test_db_url = "sqlite:///:memory:"

    # Create a test engine and session local for this fixture
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Create tables in the in-memory database
    Base.metadata.create_all(bind=test_engine)

    # Monkeypatch the global engine and SessionLocal in src.tick_app.database
    # so that all parts of the application use the test database
    monkeypatch.setattr("src.tick_app.database.engine", test_engine)
    monkeypatch.setattr("src.tick_app.database.SessionLocal", TestSessionLocal)

    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine) # Drop tables after each test
        test_engine.dispose()

@pytest.fixture(name="cli_runner")
def cli_runner_fixture(db_session, monkeypatch):
    from typer.testing import CliRunner
    runner = CliRunner()

    # Monkeypatch get_db to return the test database session
    def get_test_db():
        yield db_session

    monkeypatch.setattr("src.tick_app.database.get_db", get_test_db)

    yield runner