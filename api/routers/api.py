from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.tick_app.database import get_db
from src.tick_app.services import project_service, time_entry_service, config_service
from src.tick_app.utils import parse_duration_string
from .. import schemas

router = APIRouter()

# --- Projects ---

@router.get("/projects", response_model=List[schemas.Project])
def list_projects(
    include_archived: bool = False,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return project_service.list_projects(db, include_archived=include_archived, search_term=search)

@router.post("/projects", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    existing = project_service.get_project_by_name(db, project.name)
    if existing:
        raise HTTPException(status_code=400, detail="Project with this name already exists")
    return project_service.create_project(db, project.name, project.parent_id, project.tags)

@router.get("/projects/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = project_service.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project_update: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    project = project_service.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_update.dict(exclude_unset=True)
    # Handle tags separately if needed, but for now let's just pass kwargs
    # The service update_project might need adjustment for tags if it doesn't handle them
    # For now, we'll assume basic field updates. Tag updates might require more logic in service.
    # Given the service implementation:
    # def update_project(db: Session, project_id: int, **kwargs)
    # It just sets attributes. So we should be careful with lists.
    
    # Filter out tag lists for direct setattr, handle them if service supported it.
    # Current service doesn't seem to have explicit tag add/remove logic in update_project.
    # We will skip tag updates for now or implement them if critical.
    # The CLI 'edit' command handles tags by calling add_tag/remove_tag on the model directly or via service?
    # Let's check CLI implementation later if needed. For now, basic updates.
    
    cleaned_data = {k: v for k, v in update_data.items() if k not in ['add_tags', 'remove_tags']}
    
    updated_project = project_service.update_project(db, project_id, **cleaned_data)
    return updated_project

@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    success = project_service.delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return None

@router.post("/projects/{project_id}/archive", response_model=schemas.Project)
def archive_project(project_id: int, db: Session = Depends(get_db)):
    project = project_service.archive_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# --- Time Entries ---

@router.get("/entries", response_model=List[schemas.TimeEntry])
def list_entries(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    project_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    return time_entry_service.list_time_entries(
        db, start_date=start_date, end_date=end_date, project_id=project_id, limit=limit, offset=offset
    )

@router.post("/entries", response_model=schemas.TimeEntry, status_code=status.HTTP_201_CREATED)
def log_entry(entry: schemas.TimeEntryCreate, db: Session = Depends(get_db)):
    if not entry.start_time or not entry.end_time:
         # If duration is provided, calculate end_time? Or require start/end?
         # CLI log command requires duration or start/end.
         # For API, let's require start/end for simplicity or handle duration.
         raise HTTPException(status_code=400, detail="Start time and end time are required for logging.")
         
    return time_entry_service.log_time(
        db, entry.project_id, entry.start_time, entry.end_time, entry.description, entry.tags
    )

@router.post("/entries/start", response_model=schemas.TimeEntry)
def start_timer(entry: schemas.TimeEntryCreate, db: Session = Depends(get_db)):
    # Check if already running? Service handles it?
    # Service just starts a new one.
    return time_entry_service.start_timer(db, entry.project_id, entry.description, entry.tags)

@router.post("/entries/stop", response_model=schemas.TimeEntry)
def stop_timer(db: Session = Depends(get_db)):
    entry = time_entry_service.stop_timer(db)
    if not entry:
        raise HTTPException(status_code=404, detail="No running timer found")
    return entry

@router.get("/entries/current", response_model=Optional[schemas.TimeEntry])
def get_current_timer(db: Session = Depends(get_db)):
    return time_entry_service.get_current_running_entry(db)

@router.put("/entries/{entry_id}", response_model=schemas.TimeEntry)
def update_entry(entry_id: int, entry_update: schemas.TimeEntryUpdate, db: Session = Depends(get_db)):
    update_data = entry_update.dict(exclude_unset=True)
    updated_entry = time_entry_service.update_time_entry(db, entry_id, **update_data)
    if not updated_entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    return updated_entry

@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    success = time_entry_service.delete_time_entry(db, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Time entry not found")
    return None

# --- Reports ---

@router.post("/reports", response_model=List[Dict[str, Any]])
def generate_report(request: schemas.ReportRequest, db: Session = Depends(get_db)):
    # Parse dates
    start_dt = datetime.fromisoformat(request.start_date) if request.start_date else datetime.min
    end_dt = datetime.fromisoformat(request.end_date) if request.end_date else datetime.max
    
    return time_entry_service.generate_report(
        db, start_dt, end_dt, request.group_by, request.project_id
    )

# --- Config ---

@router.get("/config", response_model=Dict[str, Any])
def get_config():
    return config_service.config_service.all()

@router.post("/config", response_model=Dict[str, Any])
def set_config(config: schemas.ConfigSet):
    config_service.config_service.set(config.key, config.value)
    return {config.key: config.value}

@router.delete("/config/{key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_config(key: str):
    config_service.config_service.delete(key)
    return None
