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
