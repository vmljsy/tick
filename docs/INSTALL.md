# Installation Guide

## For Users

### Method 1: Install from GitHub (Recommended)

**Direct from GitHub repository:**

```bash
# With uv (fastest)
uv pip install git+https://github.com/yourusername/tick.git

# With pip
pip install git+https://github.com/yourusername/tick.git
```

### Method 2: Install Specific Version

```bash
# Install specific release
uv pip install git+https://github.com/yourusername/tick.git@v0.1.0

# Install from specific branch
uv pip install git+https://github.com/yourusername/tick.git@main
```

### Method 3: Install from Release Wheel

Download the `.whl` file from [Releases](https://github.com/yourusername/tick/releases), then:

```bash
uv pip install tick_time_tracker-0.1.0-py3-none-any.whl
```

### Method 4: Install with pipx (Isolated CLI)

```bash
pipx install git+https://github.com/yourusername/tick.git
```

## For Developers

### Quick Development Setup

```bash
# Clone
git clone https://github.com/yourusername/tick.git
cd tick

# Install with uv
uv venv
source .venv/bin/activate  # Linux/Mac
# Or: .venv\Scripts\Activate.ps1  # Windows

uv pip install -e .
```

### Full Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/tick.git
cd tick

# Create virtual environment
uv venv
# Or: python -m venv .venv

# Activate
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows

# Install in editable mode
uv pip install -e ".[dev]"

# Run tests
uv run pytest
```

## Verify Installation

```bash
tick --help
tick start "Test Project"
tick status
tick stop
```

## Update to Latest Version

```bash
# Update from GitHub
uv pip install --upgrade git+https://github.com/yourusername/tick.git

# Or reinstall specific version
uv pip install --force-reinstall git+https://github.com/yourusername/tick.git@v0.2.0
```

## Uninstall

```bash
uv pip uninstall tick-time-tracker
# Or: pip uninstall tick-time-tracker
# Or: pipx uninstall tick-time-tracker
```

## Troubleshooting

### "tick is not recognized" (Windows)

Use pipx for automatic PATH handling:
```bash
pipx install git+https://github.com/yourusername/tick.git
```

Or run directly:
```bash
python -m tick_app.cli --help
```

### Installation Fails

Try with verbose output:
```bash
uv pip install -v git+https://github.com/yourusername/tick.git
```

### uv command not found

Install uv:
```bash
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

## Requirements

- Python 3.9 or higher
- Git (for installing from GitHub)
- Windows, macOS, or Linux

## Why Install from GitHub?

- ✅ Always get the latest version
- ✅ No PyPI account needed for developers
- ✅ Direct access to source code
- ✅ Easy to contribute via pull requests
