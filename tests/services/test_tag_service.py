from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.tick_app.database import Base
from src.tick_app.services import tag_service

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

def test_create_tag():
    db = next(override_get_db())
    tag = tag_service.create_tag(db, "Test Tag")
    assert tag.name == "Test Tag"
    assert tag.id is not None
