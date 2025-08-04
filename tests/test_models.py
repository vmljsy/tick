from src.tick_app.models import Project, TimeEntry, Tag

def test_project_model():
    project = Project(name="Test Project")
    assert project.name == "Test Project"

def test_time_entry_model():
    time_entry = TimeEntry(description="Test Entry")
    assert time_entry.description == "Test Entry"

def test_tag_model():
    tag = Tag(name="Test Tag")
    assert tag.name == "Test Tag"
