# Gemini CLI Documentation

This file provides documentation for interacting with the Gemini CLI in this project.

## About the Project

This project appears to be a time-tracking application called "TickTick". It includes a command-line interface (CLI), an API, and a web interface.
CLI is the main focus of project
the python project is manged using uv - so use it for whereever possible 
when new changes are made update the README.md and GEMINI.md with relevent details repectivey 


make sure to write elent test cases when a new funtion/feature is cnged or added

## Development Workflow

*   **Automatic Commits:** Changes will be committed to the repository automatically after they are completed and approved.
*   **Feature Branches:** Large new features will be developed in a dedicated feature branch. The branch name will be descriptive of the feature (e.g., `feature/user-authentication`).

## Interacting with the Gemini CLI

You can interact with the Gemini CLI by issuing commands in natural language. The CLI can perform a variety of tasks, such as:

*   **Running tests:** "run the tests"
*   **Listing files:** "list all files in the `src` directory"
*   **Reading files:** "show me the contents of `main.py`"
*   **Writing files:** "create a new file called `new_feature.py`"

## Project Structure

The project is organized into the following main directories:

*   `api/`: Contains the source code for the FastAPI application.
    *   `main.py`: The main entry point for the FastAPI application.
    *   `routers/`: Contains the API routers.
    *   `schemas.py`: Contains the Pydantic schemas for the API.
    *   `static/`: Contains the static files for the web interface.
    *   `templates/`: Contains the HTML templates for the web interface.
*   `src/`: Contains the source code for the CLI application.
    *   `tick_app/`: The main package for the CLI application.
        *   `cli.py`: The main entry point for the CLI application.
        *   `services/`: Contains the business logic for the application.
        *   `models.py`: Contains the SQLAlchemy models for the database.
        *   `database.py`: Contains the database connection and session management logic.
*   `tests/`: Contains the tests for the project.
    *   `test_cli.py`: Tests for the main CLI application.
    *   `services/`: Contains tests for the business logic.
*   `main.py`: The main entry point for the application.
*   `pyproject.toml`: The project configuration file.
*   `README.md`: The project documentation.


## Running Tests

To run the tests for this project, you can use the following command:

"run all the tests"

## CLI Commands

The CLI is organized into a main command and several subcommands. Here's a breakdown of the available commands and their parameters:

### Main Commands

*   `start`: Starts a new time entry for a project.
    *   `project_name`: The name of the project to start the timer for (required).
    *   `--description` or `-d`: A description of the time entry.
    *   `--tag` or `-t`: Tags to associate with the time entry (can be used multiple times).
*   `stop`: Stops the currently running time entry.
*   `status`: Shows the status of the current running timer.
*   `log`: Logs a completed time entry.
    *   `project_name`: The name of the project to log time for (required).
    *   `--duration` or `-D`: The duration of the time entry (e.g., '1h30m').
    *   `--start` or `-s`: Start time of the entry (YYYY-MM-DD HH:MM).
    *   `--end` or `-e`: End time of the entry (YYYY-MM-DD HH:MM).
    *   `--description` or `-d`: A description of the time entry.
    *   `--tag` or `-t`: Tags to associate with the time entry (can be used multiple times).

### `entry` Subcommand

*   `logs`: Lists time entries with various filters.
    *   `--date`: Filter by a specific date (YYYY-MM-DD).
    *   `--today`: Filter for entries logged today.
    *   `--yesterday`: Filter for entries logged yesterday.
    *   `--week`: Filter for entries logged this week.
    *   `--month`: Filter for entries logged this month.
    *   `--project`: Filter by project name.
    *   `--tag`: Filter by tag name.
*   `adjust`: Adjusts the details of a specific time entry.
    *   `entry_id`: The ID of the time entry to adjust (required).
    *   `--duration`: New duration (e.g., '1h30m').
    *   `--desc`: New description.
    *   `--start`: New start time (YYYY-MM-DD HH:MM).
    *   `--end`: New end time (YYYY-MM-DD HH:MM).
*   `delete`: Deletes a specific time entry.
    *   `entry_id`: The ID of the time entry to delete (required).
*   `show-all`: Shows all time entries in the database.
    *   `--head` or `-n`: Show only the first N entries.
    *   `--tail` or `-m`: Show only the last M entries.

### `project` Subcommand

*   `list`: Lists all projects.
    *   `--archived`: Include archived projects.
*   `add`: Adds a new project.
    *   `name`: The name of the new project (required).
    *   `--parent`: The name of the parent project.
*   `edit`: Edits a project's details.
    *   `project_id_or_name`: The ID or name of the project to edit (required).
    *   `--name`: The new name for the project.
    *   `--parent`: The new parent for the project.
    *   `--add-tag`: A tag to add to the project.
    *   `--remove-tag`: A tag to remove from the project.
*   `archive`: Archives a project.
    *   `project_id_or_name`: The ID or name of the project to archive (required).
*   `delete`: Deletes a project.
    *   `project_id_or_name`: The ID or name of the project to delete (required).

### `report` Subcommand

*   `generate`: Generates a time tracking report.
    *   `--start-date`: Start date for the report (YYYY-MM-DD).
    *   `--end-date`: End date for the report (YYYY-MM-DD).
    *   `--day`: Generate a report for the current day.
    *   `--week`: Generate a report for the current week.
    *   `--month`: Generate a report for the current month.
    *   `--year`: Generate a report for the current year.
    *   `--project`: Filter by project name.
    *   `--tag`: Filter by tag name.
    *   `--group-by`: Group the report by: 'day', 'project', or 'tag' (defaults to 'project').

### `config` Subcommand

*   `set`: Sets a configuration value.
    *   `key`: The configuration key (required).
    *   `value`: The configuration value (required).
*   `get`: Gets a configuration value.
    *   `key`: The configuration key (required).
*   `list`: Lists all configuration values.
*   `delete`: Deletes a configuration key.
    *   `key`: The configuration key to delete (required).