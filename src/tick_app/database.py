from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session as SQLASession

from .config import DATABASE_PATH

# Global variables for engine and SessionLocal
engine: Engine = None
SessionLocal: type[SQLASession] = None

Base = declarative_base()

def configure_db(db_url: str):
    global engine, SessionLocal
    engine = create_engine(
        db_url, connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db(db_url: str = None):
    # Import models to ensure they are registered with Base.metadata
    from . import models

    if db_url:
        # If a specific URL is provided, configure a temporary engine for init
        temp_engine = create_engine(db_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=temp_engine)
        temp_engine.dispose()
    else:
        # Otherwise, use the globally configured engine
        if engine is None:
            configure_db(f"sqlite:///{DATABASE_PATH}")
        Base.metadata.create_all(bind=engine)

# Configure the default database connection when the module is imported
configure_db(f"sqlite:///{DATABASE_PATH}")