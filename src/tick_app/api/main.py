from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from tick_app.database import get_db

from pathlib import Path

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="!secret")
base_path = Path(__file__).parent
app.mount("/static", StaticFiles(directory=base_path / "static"), name="static")

# Import and include routers
from .routers import web, api
app.include_router(web.router)
app.include_router(api.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
