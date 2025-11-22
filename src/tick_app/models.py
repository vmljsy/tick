from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, TypeDecorator
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone

class UTCDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            else:
                return value.astimezone(timezone.utc)
        return value

project_tag_association = Table(
    'project_tag', Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

time_entry_tag_association = Table(
    'time_entry_tag', Base.metadata,
    Column('time_entry_id', Integer, ForeignKey('time_entries.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    parent_id = Column(Integer, ForeignKey('projects.id'))
    parent = relationship('Project', remote_side=[id])
    time_entries = relationship('TimeEntry', back_populates='project')
    tags = relationship('Tag', secondary=project_tag_association, back_populates='projects')
    archived = Column(Integer, default=0) # 0 for active, 1 for archived. Using Integer for SQLite boolean compatibility if needed, though Boolean works too.

class TimeEntry(Base):
    __tablename__ = 'time_entries'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    start_time = Column(UTCDateTime)
    end_time = Column(UTCDateTime)
    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relationship('Project', back_populates='time_entries')
    tags = relationship('Tag', secondary=time_entry_tag_association, back_populates='time_entries')

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    projects = relationship('Project', secondary=project_tag_association, back_populates='tags')
    time_entries = relationship('TimeEntry', secondary=time_entry_tag_association, back_populates='tags')
