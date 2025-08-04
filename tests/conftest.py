import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.tick_app.database import Base, get_db
from src.tick_app.cli import app as cli_app

@pytest.fixture(name="db_session")
def db_session_fixture():
    # Use an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables to ensure a clean slate for the next test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="cli_runner")
def cli_runner_fixture(db_session, monkeypatch):
    from typer.testing import CliRunner
    runner = CliRunner()

    # Monkeypatch get_db to return the test database session
    def get_test_db():
        yield db_session

    monkeypatch.setattr("src.tick_app.database.get_db", get_test_db)

    yield runner
