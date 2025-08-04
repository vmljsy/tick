from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from src.tick_app.database import SessionLocal, get_db, init_db



app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="!secret")
app.mount("/static", StaticFiles(directory="api/static"), name="static")

# Import and include routers
from .routers import web
app.include_router(web.router)
