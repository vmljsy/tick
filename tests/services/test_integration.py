import pytest
from datetime import datetime, UTC, timedelta
from src.tick_app.services import time_entry_service, project_service, tag_service

def test_start_timer_with_tags(db_session):
    """Test that tags are correctly associated with time entries"""
    # Create a project
    project = project_service.create_project(db_session, "TagProject")
    
    # Start timer with tags
    entry = time_entry_service.start_timer(
        db_session, 
        project.id, 
        description="Testing tags",
        tags=["urgent", "feature"]
    )
    
    assert entry.id is not None
    assert len(entry.tags) == 2
    tag_names = {tag.name for tag in entry.tags}
    assert "urgent" in tag_names
    assert "feature" in tag_names

def test_log_time_with_tags(db_session):
    """Test that tags work with log_time"""
    project = project_service.create_project(db_session, "LogProject")
    
    start_time = datetime.now(UTC) - timedelta(hours=2)
    end_time = datetime.now(UTC)
    
    entry = time_entry_service.log_time(
        db_session,
        project.id,
        start_time,
        end_time,
        description="Logged with tags",
        tags=["review", "testing"]
    )
    
    assert len(entry.tags) == 2
    tag_names = {tag.name for tag in entry.tags}
    assert "review" in tag_names
    assert "testing" in tag_names

def test_tags_are_reused(db_session):
    """Test that existing tags are reused, not duplicated"""
    project = project_service.create_project(db_session, "ReuseProject")
    
    # Create first entry with tag
    entry1 = time_entry_service.start_timer(
        db_session,
        project.id,
        tags=["shared"]
    )
    time_entry_service.stop_timer(db_session, entry1.id)
    
    # Create second entry with same tag
    entry2 = time_entry_service.start_timer(
        db_session,
        project.id,
        tags=["shared"]
    )
    
    # Both entries should reference the same tag
    assert entry1.tags[0].id == entry2.tags[0].id
    
    # Should only be ONE tag named "shared" in the database
    all_tags = tag_service.list_tags(db_session)
    shared_tags = [t for t in all_tags if t.name == "shared"]
    assert len(shared_tags) == 1

def test_archive_project(db_session):
    """Test project archiving functionality"""
    project = project_service.create_project(db_session, "ToArchive")
    
    # Verify project is not archived initially
    assert project.archived == 0
    
    # Archive the project
    archived_project = project_service.archive_project(db_session, project.id)
    
    assert archived_project is not None
    assert archived_project.archived == 1

def test_list_projects_excludes_archived(db_session):
    """Test that archived projects are excluded by default"""
    # Create regular project
    project1 = project_service.create_project(db_session, "ActiveProject")
    
    # Create and archive another project
    project2 = project_service.create_project(db_session, "ArchivedProject")
    project_service.archive_project(db_session, project2.id)
    
    # List projects (should not include archived)
    active_projects = project_service.list_projects(db_session, include_archived=False)
    
    project_names = {p.name for p in active_projects}
    assert "ActiveProject" in project_names
    assert "ArchivedProject" not in project_names

def test_list_projects_includes_archived_when_requested(db_session):
    """Test that archived projects can be included when requested"""
    # Create and archive a project
    project = project_service.create_project(db_session, "ArchivedProject")
    project_service.archive_project(db_session, project.id)
    
    # List with include_archived=True
    all_projects = project_service.list_projects(db_session, include_archived=True)
    
    project_names = {p.name for p in all_projects}
    assert "ArchivedProject" in project_names

def test_multiple_running_timers_scenario(db_session):
    """Test edge case of checking for running timers"""
    project = project_service.create_project(db_session, "TimerProject")
    
    # Start a timer
    entry1 = time_entry_service.start_timer(db_session, project.id)
    
    # Check current running entry
    running = time_entry_service.get_current_running_entry(db_session)
    assert running is not None
    assert running.id == entry1.id
    
    # Stop the timer
    time_entry_service.stop_timer(db_session)
    
    # No timer should be running now
    running = time_entry_service.get_current_running_entry(db_session)
    assert running is None

def test_update_time_entry_description(db_session):
    """Test updating time entry description"""
    project = project_service.create_project(db_session, "UpdateProject")
    start_time = datetime.now(UTC) - timedelta(hours=1)
    end_time = datetime.now(UTC)
    
    entry = time_entry_service.log_time(
        db_session,
        project.id,
        start_time,
        end_time,
        description="Original description"
    )
    
    # Update description
    updated = time_entry_service.update_time_entry(
        db_session,
        entry.id,
        description="Updated description"
    )
    
    assert updated.description == "Updated description"

def test_update_time_entry_times(db_session):
    """Test updating time entry start and end times"""
    project = project_service.create_project(db_session, "TimeUpdateProject")
    start_time = datetime.now(UTC) - timedelta(hours=2)
    end_time = datetime.now(UTC) - timedelta(hours=1)
    
    entry = time_entry_service.log_time(
        db_session,
        project.id,
        start_time,
        end_time
    )
    
    # Update times
    new_start = datetime.now(UTC) - timedelta(hours=3)
    new_end = datetime.now(UTC)
    
    updated = time_entry_service.update_time_entry(
        db_session,
        entry.id,
        start_time=new_start,
        end_time=new_end
    )
    
    assert updated.start_time == new_start
    assert updated.end_time == new_end

def test_delete_time_entry(db_session):
    """Test deleting a time entry"""
    project = project_service.create_project(db_session, "DeleteProject")
    start_time = datetime.now(UTC) - timedelta(hours=1)
    end_time = datetime.now(UTC)
    
    entry = time_entry_service.log_time(
        db_session,
        project.id,
        start_time,
        end_time
    )
    
    entry_id = entry.id
    
    # Delete the entry
    result = time_entry_service.delete_time_entry(db_session, entry_id)
    assert result is True
    
    # Verify it's deleted
    deleted_entry = time_entry_service.get_time_entry_by_id(db_session, entry_id)
    assert deleted_entry is None

def test_delete_nonexistent_entry(db_session):
    """Test deleting a non-existent entry returns False"""
    result = time_entry_service.delete_time_entry(db_session, 99999)
    assert result is False

def test_project_crud_operations(db_session):
    """Test complete project CRUD cycle"""
    # Create
    project = project_service.create_project(db_session, "CRUDProject")
    assert project.id is not None
    assert project.name == "CRUDProject"
    
    # Read
    retrieved = project_service.get_project_by_id(db_session, project.id)
    assert retrieved.name == "CRUDProject"
    
    retrieved_by_name = project_service.get_project_by_name(db_session, "CRUDProject")
    assert retrieved_by_name.id == project.id
    
    # Update
    updated = project_service.update_project(db_session, project.id, name="UpdatedCRUD")
    assert updated.name == "UpdatedCRUD"
    
    # Delete
    result = project_service.delete_project(db_session, project.id)
    assert result is True
    
    # Verify deleted
    deleted_project = project_service.get_project_by_id(db_session, project.id)
    assert deleted_project is None

def test_tag_crud_operations(db_session):
    """Test complete tag CRUD cycle"""
    # Create
    tag = tag_service.create_tag(db_session, "test-tag")
    assert tag.id is not None
    assert tag.name == "test-tag"
    
    # Read
    retrieved = tag_service.get_tag_by_name(db_session, "test-tag")
    assert retrieved.id == tag.id
    
    # List
    all_tags = tag_service.list_tags(db_session)
    tag_names = {t.name for t in all_tags}
    assert "test-tag" in tag_names
    
    # Rename
    renamed = tag_service.rename_tag(db_session, "test-tag", "renamed-tag")
    assert renamed.name == "renamed-tag"
    
    # Delete
    result = tag_service.delete_tag(db_session, renamed.id)
    assert result is True
    
    # Verify deleted
    deleted_tag = tag_service.get_tag_by_name(db_session, "renamed-tag")
    assert deleted_tag is None
