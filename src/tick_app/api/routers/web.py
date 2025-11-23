from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import json

from tick_app.database import get_db
from tick_app.services import project_service, time_entry_service
from tick_app.utils import (
    convert_utc_to_local, 
    convert_local_to_utc,
    parse_date_string,
    parse_duration_string,
    format_duration,
    get_start_of_day,
    get_start_of_week,
    get_start_of_month,
    get_current_datetime
)

from pathlib import Path
router = APIRouter()
base_path = Path(__file__).parent.parent
templates = Jinja2Templates(directory=base_path / "templates")

# Register utility functions as Jinja2 globals so they're available in all templates
templates.env.globals['format_duration'] = format_duration
templates.env.globals['convert_utc_to_local'] = convert_utc_to_local

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    running_entry = time_entry_service.get_current_running_entry(db)
    recent_entries = time_entry_service.list_time_entries(db, limit=5)
    projects = project_service.list_projects(db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "running_entry": running_entry,
        "recent_entries": recent_entries,
        "projects": projects,
        "convert_utc_to_local": convert_utc_to_local
    })

@router.post("/start-timer", response_class=RedirectResponse)
def start_timer_form(
    project_id: int = Form(...), 
    description: Optional[str] = Form(None), 
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Parse tags from comma-separated string
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    time_entry_service.start_timer(db, project_id, description, tag_list)
    return RedirectResponse(url="/", status_code=303)

@router.post("/stop-timer", response_class=RedirectResponse)
def stop_timer_form(db: Session = Depends(get_db)):
    time_entry_service.stop_timer(db)
    return RedirectResponse(url="/", status_code=303)

# Manual Time Logging
@router.get("/log-time", response_class=HTMLResponse)
def log_time_form(request: Request, db: Session = Depends(get_db)):
    projects = project_service.list_projects(db)
    return templates.TemplateResponse("log_time.html", {"request": request, "projects": projects})

@router.post("/log-time", response_class=RedirectResponse)
def log_time_web(
    project_id: int = Form(...),
    duration: Optional[str] = Form(None),
    start_time: Optional[str] = Form(None),
    end_time: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    
    if start_time and end_time:
        start = parse_date_string(start_time, as_local=True)
        end = parse_date_string(end_time, as_local=True)
    elif duration:
        seconds = parse_duration_string(duration)
        end = get_current_datetime()
        start = end - timedelta(seconds=seconds)
    else:
        # Default to 1 hour
        end = get_current_datetime()
        start = end - timedelta(hours=1)
    
    time_entry_service.log_time(db, project_id, start, end, description, tag_list)
    return RedirectResponse(url="/logs", status_code=303)

# Entry Management
@router.get("/logs", response_class=HTMLResponse)
def list_logs_web(request: Request, db: Session = Depends(get_db)):
    entries = time_entry_service.list_time_entries(db, limit=100)
    return templates.TemplateResponse("logs.html", {
        "request": request, 
        "entries": entries, 
        "convert_utc_to_local": convert_utc_to_local,
        "format_duration": format_duration
    })

@router.get("/entries/edit/{entry_id}", response_class=HTMLResponse)
def edit_entry_form(entry_id: int, request: Request, db: Session = Depends(get_db)):
    entry = time_entry_service.get_time_entry_by_id(db, entry_id)
    projects = project_service.list_projects(db)
    return templates.TemplateResponse("edit_entry.html", {
        "request": request, 
        "entry": entry, 
        "projects": projects,
        "convert_utc_to_local": convert_utc_to_local
    })

@router.post("/entries/edit/{entry_id}", response_class=RedirectResponse)
def edit_entry_web(
    entry_id: int,
    description: Optional[str] = Form(None),
    start_time: Optional[str] = Form(None),
    end_time: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    kwargs = {}
    if description is not None:
        kwargs['description'] = description
    if start_time:
        kwargs['start_time'] = parse_date_string(start_time, as_local=True)
    if end_time:
        kwargs['end_time'] = parse_date_string(end_time, as_local=True)
    
    time_entry_service.update_time_entry(db, entry_id, **kwargs)
    return RedirectResponse(url="/logs", status_code=303)

@router.post("/entries/delete/{entry_id}", response_class=RedirectResponse)
def delete_entry_web(entry_id: int, db: Session = Depends(get_db)):
    time_entry_service.delete_time_entry(db, entry_id)
    return RedirectResponse(url="/logs", status_code=303)

# Project Management
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

@router.post("/projects/archive/{project_id}", response_class=RedirectResponse)
def archive_project_web(project_id: int, db: Session = Depends(get_db)):
    project_service.archive_project(db, project_id)
    return RedirectResponse(url="/projects", status_code=303)

@router.post("/projects/delete/{project_id}", response_class=RedirectResponse)
def delete_project_web(project_id: int, db: Session = Depends(get_db)):
    project_service.delete_project(db, project_id)
    return RedirectResponse(url="/projects", status_code=303)

# Reports
@router.get("/reports", response_class=HTMLResponse)
def reports_web(request: Request, db: Session = Depends(get_db)):
    projects = project_service.list_projects(db)
    return templates.TemplateResponse("reports.html", {"request": request, "projects": projects})

@router.post("/reports/generate", response_class=HTMLResponse)
def generate_report_web(
    request: Request,
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    period: Optional[str] = Form(None),
    project_id: Optional[str] = Form(None),
    group_by: str = Form("project"),
    db: Session = Depends(get_db)
):
    # Convert empty string to None for project_id
    project_id_int = None
    if project_id and project_id.strip():
        try:
            project_id_int = int(project_id)
        except ValueError:
            pass  # Invalid project_id, treat as None
    
    now_utc = get_current_datetime()
    now_local = convert_utc_to_local(now_utc)
    
    # Determine date range
    if period == "day":
        start = convert_local_to_utc(get_start_of_day(now_local))
        end = convert_local_to_utc(get_start_of_day(now_local) + timedelta(days=1))
    elif period == "week":
        start = convert_local_to_utc(get_start_of_week(now_local))
        end = convert_local_to_utc(get_start_of_week(now_local) + timedelta(weeks=1))
    elif period == "month":
        start = convert_local_to_utc(get_start_of_month(now_local))
        next_month = now_local.month % 12 + 1
        next_year = now_local.year + (1 if now_local.month == 12 else 0)
        end = convert_local_to_utc(now_local.replace(year=next_year, month=next_month, day=1, hour=0, minute=0, second=0, microsecond=0))
    elif start_date and end_date:
        start = parse_date_string(start_date, as_local=True)
        end = parse_date_string(end_date, as_local=True) + timedelta(days=1)
    else:
        # Default to current week
        start = convert_local_to_utc(get_start_of_week(now_local))
        end = now_utc
    
    report_data = time_entry_service.generate_report(
        db, 
        start_date=start, 
        end_date=end, 
        group_by=group_by, 
        project_id=project_id_int
    )
    
    projects = project_service.list_projects(db)
    
    # Prepare chart data for JavaScript
    chart_labels = []
    chart_values = []
    if report_data:
        for row in report_data:
            if group_by == 'day' and row['group_key']:
                # Format date for display
                chart_labels.append(row['group_key'].strftime('%Y-%m-%d') if hasattr(row['group_key'], 'strftime') else str(row['group_key']))
            else:
                chart_labels.append(row['group_key'] or 'Unknown')
            # Convert duration from seconds to hours for better chart readability
            chart_values.append(round(row['total_duration'] / 3600, 2) if row['total_duration'] else 0)
    
    chart_data_json = json.dumps({
        'labels': chart_labels,
        'values': chart_values,
        'groupBy': group_by
    })
    
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "report_data": report_data,
        "projects": projects,
        "format_duration": format_duration,
        "convert_utc_to_local": convert_utc_to_local,
        "group_by": group_by,
        "selected_project_id": project_id_int,
        "selected_period": period,
        "chart_data": chart_data_json
    })
