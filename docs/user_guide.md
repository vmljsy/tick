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

Starts a new timer for a project. If `PROJECT_NAME` is not provided, you will be prompted to select an existing project or create a new one.

```bash
tick start "Project Name" -d "What I am working on" -t "tag1" -t "tag2"
# Or, for interactive project selection:
tick start
```

*   `PROJECT_NAME` (Optional): The name of the project.
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

Logs a completed time entry without using the timer. If `PROJECT_NAME` is not provided, you will be prompted to select an existing project or create a new one. If duration details (`--duration`, `--start`, `--end`) are missing, you will be prompted to enter the duration.

```bash
tick log "Project Name" --duration "1h30m" -d "Task I forgot to time"
# Or, for interactive project and duration selection:
tick log
```

*   `PROJECT_NAME` (Optional): The name of the project.
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

Modifies an existing time entry. If `ENTRY_ID` is not provided, you will be prompted to select an entry from a list of recent entries. If no modification options are given, you will be prompted to choose which field to adjust.

```bash
tick entry adjust 123 --desc "A more detailed description"
# Or, for interactive entry and field selection:
tick entry adjust
```

*   `ENTRY_ID` (Optional): The ID of the entry to change.
*   `--duration`, `--desc`, `--start`, `--end`: The attribute to modify.

### `tick entry delete`

Deletes a time entry. If `ENTRY_ID` is not provided, you will be prompted to select an entry from a list of recent entries.

```bash
tick entry delete 123
# Or, for interactive entry selection:
tick entry delete
```

### `tick entry show-all`

Shows all entries in the database, with optional slicing.

```bash
# Show the 5 most recent entries
tick entry show-all --tail 5
```

## 5. Managing Projects (`tick project`)

This command group helps you manage your projects.

### `tick project list`

Lists all projects.

```bash
tick project list
```

*   `--archived`: Include archived projects.

### `tick project add`

Adds a new project. If `NAME` is not provided, you will be prompted to enter it.

```bash
tick project add "New Project" --parent "My Parent Project"
# Or, for interactive name entry:
tick project add
```

*   `NAME` (Optional): The name of the new project.
*   `--parent`: The name of the parent project.

### `tick project edit`

Edits a project's details. If `PROJECT_ID_OR_NAME` is not provided, you will be prompted to select a project from a list.

```bash
tick project edit <ID or Name> --name "Renamed Project"
# Or, for interactive project selection:
tick project edit
```

*   `PROJECT_ID_OR_NAME` (Optional): The ID or name of the project to edit.
*   `--name`: The new name for the project.
*   `--parent`: The new parent for the project.
*   `--add-tag`: A tag to add to the project.
*   `--remove-tag`: A tag to remove from the project.

### `tick project archive`

Archives a project. If `PROJECT_ID_OR_NAME` is not provided, you will be prompted to select a project from a list.

```bash
tick project archive <ID or Name>
# Or, for interactive project selection:
tick project archive
```

### `tick project delete`

Deletes a project. If `PROJECT_ID_OR_NAME` is not provided, you will be prompted to select a project from a list.

```bash
tick project delete <ID or Name>
# Or, for interactive project selection:
tick project delete
```

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
*   `--graph`: Displays a bar chart of the report results in the terminal.

### Note for Windows Users

To use the `--graph` feature on Windows, you may need to set an environment variable to ensure your terminal can correctly handle the characters used to draw the graph. You should run the command as follows:

```bash
set PYTHONIOENCODING=UTF-8 && uv run tick report generate --year --graph
```

## 7. Exporting Data (`tick export`)

This command group allows you to export various types of time tracking data to different formats.

### `tick export entries`

Exports raw time entries. You can filter entries by date, project, or tag.

```bash
tick export entries --format csv --output my_entries.csv
# Export today's entries to JSON and print to stdout:
tick export entries --today --format json
```

*   `--format` / `-f`: Output format: `csv` (default), `json`, `txt`.
*   `--output` / `-o`: Output file path. If not specified, prints to stdout.
*   `--date`, `--today`, `--yesterday`, `--week`, `--month`: Filter by common timeframes.
*   `--project`, `--tag`: Filter by project or tag name.

### `tick export projects`

Exports your list of projects.

```bash
tick export projects --format json --output my_projects.json
# Export archived projects to text and print to stdout:
tick export projects --archived --format txt
```

*   `--format` / `-f`: Output format: `csv` (default), `json`, `txt`.
*   `--output` / `-o`: Output file path. If not specified, prints to stdout.
*   `--archived`: Include archived projects in the export.

### `tick export report`

Exports an aggregated time report. This command supports the same filtering and grouping options as `tick report generate`.

```bash
tick export report --week --group-by project --format csv --output weekly_report.csv
# Export a monthly report to JSON and print to stdout:
tick export report --month --format json
```

*   `--format` / `-f`: Output format: `csv` (default), `json`, `txt`.
*   `--output` / `-o`: Output file path. If not specified, prints to stdout.
*   `--day`, `--week`, `--month`, `--year`: Specify the reporting period.
*   `--start-date`, `--end-date`: Define a custom date range.
*   `--project`, `--tag`: Filter the report for a specific project or tag.
*   `--group-by`: Group data by `project`, `day`, or `tag`.

## 8. Configuration (`tick config`)

Manage internal settings for `tick`. If `KEY` or `VALUE` are not provided for `set`, `get`, or `delete` commands, you will be prompted interactively.

### Logging Configuration

`tick` can save logs to a file with rotation. These settings are configurable:

*   `log_file_path`: The absolute path to the log file. Defaults to `~/.tick/.logs/app.log`.
*   `log_file_max_bytes`: Maximum size of a log file before rotation, in bytes. Defaults to `10485760` (10 MB).
*   `log_file_backup_count`: Number of backup log files to keep. Defaults to `5`.
*   `log_level`: The minimum logging level to capture (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). This overrides the `debug_mode` setting for file logging.`
*   `timezone`: The timezone to use for displaying and logging times (e.g., `America/New_York`, `Europe/London`). Defaults to system local timezone if not set.

To configure, use `tick config set <KEY> <VALUE>`.

### `tick config set`

Sets a configuration value.

```bash
tick config set my_key my_value
# Or, for interactive key/value entry:
tick config set
```

*   `KEY` (Optional): The configuration key.
*   `VALUE` (Optional): The configuration value.

### `tick config get`

Gets a configuration value.

```bash
tick config get my_key
# Or, for interactive key selection:
tick config get
```

*   `KEY` (Optional): The configuration key.

### `tick config list`

Lists all configuration values.

```bash
tick config list
```

### `tick config delete`

Deletes a configuration key.

```bash
tick config delete my_key
# Or, for interactive key selection:
tick config delete
```

*   `KEY` (Optional): The configuration key.

## 9. The Web UI

For a more visual overview, you can use the web interface.

1.  **Start the Server:**
    ```bash
    uvicorn api.main:app --reload
    ```
2.  **Open in Browser:** Navigate to `http://127.0.0.1:8000`.

The web UI provides a dashboard, a log viewer, and project management tools.

## 10. Database Location

All your data is stored in a local SQLite database file (`tick.db`) at:

*   **Windows:** `C:\Users\YourUsername\.tick\tick.db`
*   **macOS/Linux:** `~/.tick/tick.db`