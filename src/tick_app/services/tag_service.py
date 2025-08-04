from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models

def create_tag(db: Session, name: str) -> models.Tag:
    db_tag = models.Tag(name=name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def get_tag_by_name(db: Session, tag_name: str) -> Optional[models.Tag]:
    return db.query(models.Tag).filter(models.Tag.name == tag_name).first()

def list_tags(db: Session) -> List[models.Tag]:
    return db.query(models.Tag).all()

def rename_tag(db: Session, old_name: str, new_name: str) -> Optional[models.Tag]:
    db_tag = get_tag_by_name(db, old_name)
    if db_tag:
        db_tag.name = new_name
        db.commit()
        db.refresh(db_tag)
    return db_tag

def delete_tag(db: Session, tag_id: int) -> bool:
    db_tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if db_tag:
        db.delete(db_tag)
        db.commit()
        return True
    return False
