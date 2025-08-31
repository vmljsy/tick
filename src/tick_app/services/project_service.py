from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models
from ..profiling import profile_time

@profile_time
def create_project(db: Session, name: str, parent_id: Optional[int] = None, tags: List[str] = []) -> models.Project:
    db_project = models.Project(name=name, parent_id=parent_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@profile_time
def get_project_by_id(db: Session, project_id: int) -> Optional[models.Project]:
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    return project

@profile_time
def get_project_by_name(db: Session, project_name: str) -> Optional[models.Project]:
    project = db.query(models.Project).filter(models.Project.name == project_name).first()
    return project

@profile_time
def list_projects(db: Session, include_archived: bool = False, search_term: Optional[str] = None) -> List[models.Project]:
    query = db.query(models.Project)
    # TODO: Handle archived projects
    if search_term:
        query = query.filter(models.Project.name.contains(search_term))
    return query.all()

@profile_time
def update_project(db: Session, project_id: int, **kwargs) -> Optional[models.Project]:
    db_project = get_project_by_id(db, project_id)
    if db_project:
        for key, value in kwargs.items():
            setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
    return db_project

def archive_project(db: Session, project_id: int) -> Optional[models.Project]:
    # TODO: Implement soft delete
    pass

@profile_time
def delete_project(db: Session, project_id: int) -> bool:
    db_project = get_project_by_id(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False
