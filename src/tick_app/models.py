from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

project_tag_association = Table(
    'project_tag', Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id')),
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

class TimeEntry(Base):
    __tablename__ = 'time_entries'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relationship('Project', back_populates='time_entries')

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    projects = relationship('Project', secondary=project_tag_association, back_populates='tags')
