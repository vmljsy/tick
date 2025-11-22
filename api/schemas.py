from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

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

class ProjectCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    tags: List[str] = []

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    add_tags: List[str] = []
    remove_tags: List[str] = []

class TimeEntryCreate(BaseModel):
    project_id: int
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[str] = None
    tags: List[str] = []

class TimeEntryUpdate(BaseModel):
    project_id: Optional[int] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[str] = None

class ConfigSet(BaseModel):
    key: str
    value: str

class ReportRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    period: Optional[str] = None # day, week, month, year
    project_id: Optional[int] = None
    tag: Optional[str] = None
    group_by: str = 'project'

