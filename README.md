# `tick` - A Personal Time Tracking Application

`tick` is a lightweight, personal time tracking application designed for developers and individuals who prefer a local, file-based solution without cloud synchronization. It offers a powerful Command Line Interface (CLI) for quick time logging and management, complemented by an intuitive Web User Interface (Web UI) for a visual overview and easier data manipulation.

## Features

*   **CLI-first Design:** Quickly start/stop timers, log time, and manage projects directly from your terminal.
*   **Web UI:** A clean, functional web interface for dashboard overview, detailed logs, project management, and reports.
*   **Local Data Storage:** All data is stored locally in a SQLite database (`tick.db`), ensuring privacy and offline access.
*   **Project Management:** Create, list, edit, and delete projects.
*   **Time Entry Management:** Log, adjust, and delete individual time entries.
*   **Reporting:** Generate reports grouped by day or project for insights into your time usage.

## Installation

To get `tick` up and running on your system, follow these steps:

### Prerequisites

*   Python 3.8+
*   `uv` (or `Poetry`/`Rye` if you prefer, but `uv` is used in these instructions)

### Steps

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd tick
    ```
    *(Replace `<your-repository-url>` with the actual URL of your Git repository.)*

2.  **Create and activate a virtual environment using `uv`:**
    ```bash
    uv venv
    .venv\Scripts\activate  # On Windows
    # source .venv/bin/activate # On macOS/Linux
    ```

3.  **Install project dependencies:**
    ```bash
    uv pip install -e .
    ```
    This command installs all necessary packages and makes the `tick` CLI command available.

## Usage

### Command Line Interface (CLI)

Once installed, you can use the `tick` command directly from your terminal.

**General Help:**
```bash
tick --help
```

**Starting a Timer:**
```bash
tick start "My New Project" -d "Working on a new feature"
# If "My New Project" doesn't exist, it will prompt you to create it.
# If another timer is running, it will prompt to stop it and start the new one.
```

**Stopping the Current Timer:**
```bash
tick stop
```

**Checking Current Timer Status:**
```bash
tick status
```

**Logging a Past Time Entry:**
```bash
tick log "Existing Project" "1h30m" -d "Finished the report"
# Duration can be in hours (h), minutes (m), or seconds (s), e.g., "2h", "45m", "1h15m30s"
```

**Listing Time Entries:**
```bash
tick entry logs
# Filter by date:
# tick entry logs --date 2025-07-28
# tick entry logs --today
# tick entry logs --yesterday
# tick entry logs --week
# tick entry logs --month
# Filter by project:
# tick entry logs --project "My New Project"
```

**Showing All Entries (with head/tail):**
```bash
tick entry show-all
# Show first 5 entries:
# tick entry show-all --head 5
# Show last 10 entries:
# tick entry show-all --tail 10
```

**Project Management:**
```bash
tick project list
tick project add "New Client Project" --parent "My New Project"
tick project edit <PROJECT_ID_OR_NAME> --name "Renamed Project"
tick project delete <PROJECT_ID_OR_NAME>
```

**Generating Reports:**
```bash
tick report generate --day
# Group by project (default):
# tick report generate --week --group-by project
# Group by day:
# tick report generate --month --group-by day
# Filter by date range:
# tick report generate --start-date 2025-07-01 --end-date 2025-07-31
```

### Web User Interface (Web UI)

To start the web interface, run the following command from the project root:

```bash
uvicorn api.main:app --reload
```

Open your web browser and navigate to `http://127.0.0.1:8000` (or the address shown in your terminal). The `--reload` flag will automatically restart the server when you make changes to the code.

## Database

`tick` uses a local SQLite database. The database file (`tick.db`) is located in your user's home directory under a hidden folder:

*   **Windows:** `%USERPROFILE%\.tick\tick.db` (e.g., `C:\Users\YourUsername\.tick\tick.db`)
*   **macOS/Linux:** `~/.tick/tick.db`

## Development and Testing

### Running Tests

To run the test suite, ensure your virtual environment is activated and execute `pytest`:

```bash
.venv\Scripts\activate # On Windows
# source .venv/bin/activate # On macOS/Linux
pytest
```

## Future Enhancements

*   Implement tag management and filtering in reports.
*   More advanced reporting options and visualizations.
*   Export/import data functionality.
*   Improved error handling and user feedback.
*   Further UI/UX refinements for both CLI and Web interfaces.
