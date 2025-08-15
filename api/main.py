from fastapi import FastAPI, Depends, Query
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta

from src.tick_app.database import SessionLocal, get_db
from src.tick_app.services import time_entry_service, project_service, tag_service
from src.tick_app.utils import get_current_datetime, convert_utc_to_local, get_start_of_day, get_start_of_week, get_start_of_month, parse_date_string, convert_local_to_utc
from .schemas import ReportQueryParams, ReportResponse
from fastapi import HTTPException

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="!secret")
app.mount("/static", StaticFiles(directory="api/static"), name="static")

# Import and include routers
from .routers import web
app.include_router(web.router)

@app.get("/api/reports", response_model=ReportResponse)
def get_reports(
    db: Session = Depends(get_db),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    day: bool = Query(False),
    week: bool = Query(False),
    month: bool = Query(False),
    year: bool = Query(False),
    project_name: Optional[str] = Query(None),
    tag_name: Optional[str] = Query(None),
    group_by: str = Query("project"),
):
    now_utc = get_current_datetime()
    now_local = convert_utc_to_local(now_utc)

    start, end = None, None

    if start_date:
        start = parse_date_string(start_date, as_local=True)
    elif day:
        start = convert_local_to_utc(get_start_of_day(now_local))
    elif week:
        start = convert_local_to_utc(get_start_of_week(now_local))
    elif month:
        start = convert_local_to_utc(get_start_of_month(now_local))
    elif year:
        start = convert_local_to_utc(now_local.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0))
    
    if end_date:
        end = parse_date_string(end_date, as_local=True) + timedelta(days=1)
    elif day:
        end = convert_local_to_utc(get_start_of_day(now_local) + timedelta(days=1))
    elif week:
        end = convert_local_to_utc(get_start_of_week(now_local) + timedelta(weeks=1))
    elif month:
        next_month = now_local.month % 12 + 1
        next_year = now_local.year + (1 if now_local.month == 12 else 0)
        end = convert_local_to_utc(now_local.replace(year=next_year, month=next_month, day=1, hour=0, minute=0, second=0, microsecond=0))
    elif year:
        end = convert_local_to_utc(now_local.replace(year=now_local.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0))

    if start is None:
        start = convert_local_to_utc(get_start_of_day(now_local))
    if end is None:
        end = now_utc

    project_id = None
    if project_name:
        project = project_service.get_project_by_name(db, project_name)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found.")
        project_id = project.id

    tag_id = None
    if tag_name:
        tag = tag_service.get_tag_by_name(db, tag_name)
        if not tag:
            raise HTTPException(status_code=404, detail=f"Tag '{tag_name}' not found.")
        tag_id = tag.id

    report_data = time_entry_service.generate_report(
        db, start_date=start, end_date=end, group_by=group_by, project_id=project_id, tag_id=tag_id
    )
    return report_data
