from sqlalchemy import func, extract
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC

from .. import models

def start_timer(db: Session, project_id: int, description: Optional[str] = None, tags: List[str] = []) -> models.TimeEntry:
    # TODO: Handle tags
    db_time_entry = models.TimeEntry(
        project_id=project_id,
        description=description,
        start_time=datetime.now(UTC)
    )
    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry

def stop_timer(db: Session, entry_id: Optional[int] = None) -> Optional[models.TimeEntry]:
    if entry_id:
        db_time_entry = get_time_entry_by_id(db, entry_id)
    else:
        db_time_entry = get_current_running_entry(db)
    
    if db_time_entry:
        db_time_entry.end_time = datetime.now(UTC)
        db.commit()
        db.refresh(db_time_entry)
    return db_time_entry

def log_time(db: Session, project_id: int, start_time: datetime, end_time: datetime, description: Optional[str] = None, tags: List[str] = []) -> models.TimeEntry:
    # TODO: Handle tags
    db_time_entry = models.TimeEntry(
        project_id=project_id,
        start_time=start_time,
        end_time=end_time,
        description=description
    )
    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry

def get_current_running_entry(db: Session) -> Optional[models.TimeEntry]:
    return db.query(models.TimeEntry).filter(models.TimeEntry.end_time == None).first()

def list_time_entries(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, project_id: Optional[int] = None, tag_id: Optional[int] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> List[models.TimeEntry]:
    query = db.query(models.TimeEntry).options(joinedload(models.TimeEntry.project))
    if start_date:
        query = query.filter(models.TimeEntry.start_time >= start_date)
    if end_date:
        query = query.filter(models.TimeEntry.end_time <= end_date)
    if project_id:
        query = query.filter(models.TimeEntry.project_id == project_id)
    # TODO: Handle tag_id
    if limit:
        query = query.limit(limit)
    if offset:
        query = query.offset(offset)
    return query.all()

def get_time_entry_by_id(db: Session, entry_id: int) -> Optional[models.TimeEntry]:
    return db.query(models.TimeEntry).filter(models.TimeEntry.id == entry_id).first()

def update_time_entry(db: Session, entry_id: int, **kwargs) -> Optional[models.TimeEntry]:
    db_time_entry = get_time_entry_by_id(db, entry_id)
    if db_time_entry:
        for key, value in kwargs.items():
            setattr(db_time_entry, key, value)
        db.add(db_time_entry) # Ensure the object is in the session and tracked for changes
        db.commit()
        db.refresh(db_time_entry)
    return db_time_entry

def delete_time_entry(db: Session, entry_id: int) -> bool:
    db_time_entry = get_time_entry_by_id(db, entry_id)
    if db_time_entry:
        db.delete(db_time_entry)
        db.commit()
        return True
    return False

def generate_report(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    group_by: str = 'day',
    project_id: Optional[int] = None,
    tag_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    query = db.query(models.TimeEntry).filter(models.TimeEntry.end_time.isnot(None))

    if start_date:
        query = query.filter(models.TimeEntry.start_time >= start_date)
    if end_date:
        query = query.filter(models.TimeEntry.end_time <= end_date)
    if project_id:
        query = query.filter(models.TimeEntry.project_id == project_id)
    # TODO: Handle tag_id filtering for reports

    report_data = []

    if group_by == 'day':
        results = query.group_by(func.date(models.TimeEntry.start_time)).with_entities(
            func.date(models.TimeEntry.start_time).label('date'),
            func.sum(extract('epoch', models.TimeEntry.end_time) - extract('epoch', models.TimeEntry.start_time)).label('total_duration')
        ).all()
        for row in results:
            report_data.append({
                'group_key': datetime.strptime(row.date, '%Y-%m-%d').strftime('%Y-%m-%d'),
                'total_duration': row.total_duration
            })
    elif group_by == 'project':
        results = query.join(models.Project).group_by(models.Project.id).with_entities(
            models.Project.name.label('project_name'),
            func.sum(extract('epoch', models.TimeEntry.end_time) - extract('epoch', models.TimeEntry.start_time)).label('total_duration')
        ).all()
        for row in results:
            report_data.append({
                'group_key': row.project_name,
                'total_duration': row.total_duration
            })
    elif group_by == 'tag':
        # This requires joining with the association table and Tag model
        # For now, return empty or raise an error
        pass
    else: # Default to project grouping if an invalid group_by is provided
        results = query.join(models.Project).group_by(models.Project.id).with_entities(
            models.Project.name.label('project_name'),
            func.sum(extract('epoch', models.TimeEntry.end_time) - extract('epoch', models.TimeEntry.start_time)).label('total_duration')
        ).all()
        for row in results:
            report_data.append({
                'group_key': row.project_name,
                'total_duration': row.total_duration
            })

    return report_data
