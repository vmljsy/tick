from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True

class ProjectBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

class ProjectCreate(ProjectBase):
    tags: List[str] = []

class Project(ProjectBase):
    id: int
    tags: List[Tag] = []

    class Config:
        orm_mode = True

class TimeEntryBase(BaseModel):
    description: Optional[str] = None
    project_id: int

class TimeEntryCreate(TimeEntryBase):
    start_time: datetime
    end_time: datetime
    tags: List[str] = []

class TimeEntry(TimeEntryBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None

    class Config:
        orm_mode = True
