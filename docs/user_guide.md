# Tick - The Comprehensive User Guide

Welcome to `tick`, your personal time tracking assistant. This guide provides a complete overview of how to install, use, and manage `tick` for effective time tracking.

## 1. Introduction

`tick` is a lightweight, personal time tracking application designed for developers and individuals who prefer a local, file-based solution without cloud synchronization. It offers a powerful Command Line Interface (CLI) for speed and efficiency, and an intuitive Web User Interface (Web UI) for visualization and management.

### Features

*   **CLI-first Design:** Quickly start/stop timers, log time, and manage projects directly from your terminal.
*   **Web UI:** A clean, functional web interface for a dashboard overview, detailed logs, project management, and reports.
*   **Local Data Storage:** All data is stored locally in a SQLite database (`tick.db`), ensuring privacy and offline access.
*   **Project & Tag Management:** Organize your time with projects, sub-projects, and tags.
*   **Reporting:** Generate reports to gain insights into your time usage, grouped by day, project, or tag.

## 2. Installation

There are two primary ways to install `tick`, depending on your needs.

### For End-Users (Recommended)

This method is for users who simply want to use the application without modifying the source code.

1.  **Download a Release:** Go to the project's GitHub releases page and download the latest `.whl` file.
2.  **Install with `pip`:** Open your terminal or command prompt and run:
    ```bash
    pip install /path/to/downloaded/ticktick-0.1.0-py3-none-any.whl
    ```

### For Developers

This method is for developers who want to contribute to the project or modify it.

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd tick
    ```
2.  **Set up Virtual Environment:**
    ```bash
    uv venv
    .venv\Scripts\activate  # On Windows
    # source .venv/bin/activate # On macOS/Linux
    ```
3.  **Install in Editable Mode:**
    ```bash
    uv pip install -e .
    ```

## 3. Core CLI Commands

These are the main commands for daily time tracking.

### `tick start`

Starts a new timer for a project.

```bash
tick start "Project Name" -d "What I am working on" -t "tag1" -t "tag2"
```

*   `PROJECT_NAME` (Required): The name of the project.
*   `--description` / `-d`: An optional description of the task.
*   `--tag` / `-t`: Add one or more tags to the entry.

### `tick stop`

Stops the currently running time entry.

```bash
tick stop
```

### `tick status`

Shows the details of the currently running timer, if any.

```bash
tick status
```

### `tick log`

Logs a completed time entry without using the timer.

```bash
tick log "Project Name" --duration "1h30m" -d "Task I forgot to time"
```

*   `PROJECT_NAME` (Required): The name of the project.
*   `--duration` / `-D`: The duration of the entry (e.g., '2h', '45m').
*   `--start` / `-s`: Specify a precise start time (YYYY-MM-DD HH:MM).
*   `--end` / `-e`: Specify a precise end time (YYYY-MM-DD HH:MM).
*   `--description` / `-d`: An optional description.
*   `--tag` / `-t`: Add one or more tags.

## 4. Managing Time Entries (`tick entry`)

This command group helps you manage past time entries.

### `tick entry logs`

Lists time entries. **Defaults to showing today's entries.**

```bash
# Shows today's entries
tick entry logs

# Show this week's entries
tick entry logs --week

# Show entries for a specific project
tick entry logs --project "Project Name"
```

*   `--today`, `--yesterday`, `--week`, `--month`: Filter by common timeframes.
*   `--date YYYY-MM-DD`: Filter for a specific date.
*   `--project`, `--tag`: Filter by project or tag name.

### `tick entry adjust`

Modifies an existing time entry.

```bash
tick entry adjust 123 --desc "A more detailed description"
```

*   `ENTRY_ID` (Required): The ID of the entry to change.
*   `--duration`, `--desc`, `--start`, `--end`: The attribute to modify.

### `tick entry delete`

Deletes a time entry.

```bash
tick entry delete 123
```

### `tick entry show-all`

Shows all entries in the database, with optional slicing.

```bash
# Show the 5 most recent entries
tick entry show-all --tail 5
```

## 5. Managing Projects (`tick project`)

This command group helps you manage your projects.

*   `tick project list`: Lists all active projects.
*   `tick project add "New Project"`: Adds a new project.
*   `tick project edit <ID or Name>`: Edits a project's name or parent.
*   `tick project archive <ID or Name>`: Archives a project.
*   `tick project delete <ID or Name>`: Deletes a project.

## 6. Reporting (`tick report`)

Generates reports from your time entries. **Defaults to a weekly report.**

```bash
# Generate a report for the current week, grouped by project
tick report

# Generate a report for the current month, grouped by day
tick report --month --group-by day
```

*   `--day`, `--week`, `--month`, `--year`: Specify the reporting period.
*   `--start-date`, `--end-date`: Define a custom date range.
*   `--project`, `--tag`: Filter the report for a specific project or tag.
*   `--group-by`: Group data by `project`, `day`, or `tag`.

## 7. Configuration (`tick config`)

Manage internal settings for `tick`.

*   `tick config list`: Shows all current settings.
*   `tick config get <KEY>`: Retrieves a specific value.
*   `tick config set <KEY> <VALUE>`: Sets a configuration value.
*   `tick config delete <KEY>`: Deletes a key.

## 8. The Web UI

For a more visual overview, you can use the web interface.

1.  **Start the Server:**
    ```bash
    uvicorn api.main:app --reload
    ```
2.  **Open in Browser:** Navigate to `http://127.0.0.1:8000`.

The web UI provides a dashboard, a log viewer, and project management tools.

## 9. Database Location

All your data is stored in a local SQLite database file (`tick.db`) at:

*   **Windows:** `C:\Users\YourUsername\.tick\tick.db`
*   **macOS/Linux:** `~/.tick/tick.db`
