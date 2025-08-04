from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.tick_app.database import Base
from src.tick_app.services import time_entry_service, project_service

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def test_start_and_stop_timer():
    db = next(override_get_db())
    project = project_service.create_project(db, "Test Project")
    
    start_time = datetime.utcnow()
    entry = time_entry_service.start_timer(db, project.id, "Test Description")
    assert entry.project_id == project.id
    assert entry.description == "Test Description"
    assert entry.end_time is None

    stopped_entry = time_entry_service.stop_timer(db, entry.id)
    assert stopped_entry.end_time is not None
