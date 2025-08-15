from pydantic import BaseModel, RootModel
from typing import Optional, List, Any
from datetime import datetime, date

class Tag(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class Project(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    tags: List[Tag] = []

    class Config:
        orm_mode = True

class TimeEntry(BaseModel):
    id: int
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    project: Project

    class Config:
        orm_mode = True

# Report Schemas
class ReportQueryParams(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    day: bool = False
    week: bool = False
    month: bool = False
    year: bool = False
    project_name: Optional[str] = None
    tag_name: Optional[str] = None
    group_by: str = "project"

class ReportRow(BaseModel):
    group_key: Any # Can be date or string
    total_duration: float

class ReportResponse(RootModel):
    root: List[ReportRow]
