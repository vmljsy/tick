from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from src.tick_app.database import get_db
from src.tick_app.services import project_service, time_entry_service

router = APIRouter()
templates = Jinja2Templates(directory="api/templates")

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    running_entry = time_entry_service.get_current_running_entry(db)
    recent_entries = time_entry_service.list_time_entries(db, limit=5)
    projects = project_service.list_projects(db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "running_entry": running_entry,
        "recent_entries": recent_entries,
        "projects": projects
    })

@router.post("/start-timer", response_class=RedirectResponse)
def start_timer_form(project_id: int = Form(...), description: Optional[str] = Form(None), db: Session = Depends(get_db)):
    time_entry_service.start_timer(db, project_id, description)
    return RedirectResponse(url="/", status_code=303)

@router.post("/stop-timer", response_class=RedirectResponse)
def stop_timer_form(db: Session = Depends(get_db)):
    time_entry_service.stop_timer(db)
    return RedirectResponse(url="/", status_code=303)

@router.get("/logs", response_class=HTMLResponse)
def list_logs_web(request: Request, db: Session = Depends(get_db)):
    entries = time_entry_service.list_time_entries(db)
    return templates.TemplateResponse("logs.html", {"request": request, "entries": entries})

@router.get("/projects", response_class=HTMLResponse)
def list_projects_web(request: Request, db: Session = Depends(get_db)):
    projects = project_service.list_projects(db)
    return templates.TemplateResponse("projects.html", {"request": request, "projects": projects})

@router.get("/projects/add", response_class=HTMLResponse)
def add_project_form(request: Request, db: Session = Depends(get_db)):
    projects = project_service.list_projects(db)
    return templates.TemplateResponse("add_project.html", {"request": request, "projects": projects})

@router.post("/projects/add", response_class=RedirectResponse)
def add_project_web(name: str = Form(...), parent_id: Optional[int] = Form(None), db: Session = Depends(get_db)):
    project_service.create_project(db, name, parent_id)
    return RedirectResponse(url="/projects", status_code=303)

@router.get("/projects/edit/{project_id}", response_class=HTMLResponse)
def edit_project_form(project_id: int, request: Request, db: Session = Depends(get_db)):
    project = project_service.get_project_by_id(db, project_id)
    projects = project_service.list_projects(db)
    return templates.TemplateResponse("edit_project.html", {"request": request, "project": project, "projects": projects})

@router.post("/projects/edit/{project_id}", response_class=RedirectResponse)
def edit_project_web(project_id: int, name: str = Form(...), parent_id: Optional[int] = Form(None), db: Session = Depends(get_db)):
    project_service.update_project(db, project_id, name=name, parent_id=parent_id)
    return RedirectResponse(url="/projects", status_code=303)

@router.get("/reports", response_class=HTMLResponse)
def reports_web(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})
