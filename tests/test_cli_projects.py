from typer.testing import CliRunner
from src.tick_app.cli import app
from src.tick_app.services import project_service

def test_project_add(cli_runner: CliRunner, db_session):
    result = cli_runner.invoke(app, ["project", "add", "NewProject"])
    assert result.exit_code == 0
    assert "Project 'NewProject' has been created." in result.stdout.strip()
    project = project_service.get_project_by_name(db_session, "NewProject")
    assert project is not None

def test_project_add_with_parent(cli_runner: CliRunner, db_session):
    project_service.create_project(db_session, "ParentProject")
    result = cli_runner.invoke(app, ["project", "add", "ChildProject", "--parent", "ParentProject"])
    assert result.exit_code == 0
    assert "Project 'ChildProject' has been created." in result.stdout.strip()
    child_project = project_service.get_project_by_name(db_session, "ChildProject")
    parent_project = project_service.get_project_by_name(db_session, "ParentProject")
    assert child_project.parent_id == parent_project.id

def test_project_list(cli_runner: CliRunner, db_session):
    project_service.create_project(db_session, "Project1")
    project_service.create_project(db_session, "Project2")
    result = cli_runner.invoke(app, ["project", "list"])
    assert result.exit_code == 0
    assert "Project1" in result.stdout.strip()
    assert "Project2" in result.stdout.strip()

def test_project_edit_name(cli_runner: CliRunner, db_session):
    project = project_service.create_project(db_session, "OldName")
    result = cli_runner.invoke(app, ["project", "edit", str(project.id), "--name", "NewName"])
    assert result.exit_code == 0
    assert "Project 'NewName' has been updated." in result.stdout.strip()
    assert project_service.get_project_by_name(db_session, "OldName") is None
    assert project_service.get_project_by_name(db_session, "NewName") is not None

def test_project_delete(cli_runner: CliRunner, db_session):
    project = project_service.create_project(db_session, "ProjectToDelete")
    result = cli_runner.invoke(app, ["project", "delete", str(project.id)], input="y\n")
    assert result.exit_code == 0
    assert "Project 'ProjectToDelete' has been deleted." in result.stdout.strip()
    assert project_service.get_project_by_name(db_session, "ProjectToDelete") is None
