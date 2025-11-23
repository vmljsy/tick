from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.engine import Engine
from typing import Generator

from .config import DATABASE_PATH

Base = declarative_base()

class DatabaseManager:
    def __init__(self, db_url: str = None):
        self.db_url = db_url or f"sqlite:///{DATABASE_PATH}"
        self.engine: Engine = create_engine(
            self.db_url, connect_args={"check_same_thread": False}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_db(self) -> Generator[Session, None, None]:
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def init_db(self):
        # Import models to ensure they are registered with Base.metadata
        from . import models
        Base.metadata.create_all(bind=self.engine)

# Singleton instance for backward compatibility if needed, 
# but prefer dependency injection where possible.
# We will initialize this in the main CLI entry point.
_db_manager = None

def get_db_manager(db_url: str = None) -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_url)
    return _db_manager

# Helper for FastAPI dependency
def get_db():
    if _db_manager is None:
        # Fallback or default initialization
        get_db_manager()
    yield from _db_manager.get_db()