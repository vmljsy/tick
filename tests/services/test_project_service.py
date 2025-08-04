from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.tick_app.database import Base
from src.tick_app.services import project_service

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

def test_create_project():
    db = next(override_get_db())
    project = project_service.create_project(db, "Test Project")
    assert project.name == "Test Project"
    assert project.id is not None
