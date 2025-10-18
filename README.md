# CPU Utilization Monitor

[![CI/CD Pipeline](https://github.com/johnmulder/cpu-monitor/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/johnmulder/cpu-monitor/actions)
[![Coverage](https://img.shields.io/badge/coverage-99.77%25-brightgreen)](https://github.com/johnmulder/cpu-monitor)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Real-time CPU usage monitor with per-core charts and an interactive Tkinter interface.

## Features

- **Live Updates**: Configurable intervals (100 ms–10 s) and history (10 s–1 h)
- **Per-Core View**: Auto-detects all cores; color-coded visualization with legend
- **Interactive UI**: Dark theme, pause/clear/toggle controls, smooth charts
- **Cross-Platform**: Works on macOS, Linux, and Windows via psutil
- **Robust Fallback**: Uses `/proc/stat` on Linux when psutil unavailable

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/johnmulder/cpu-monitor.git
cd cpu-monitor

# Install the package with dependencies
pip install -e .

# Or install with development dependencies
pip install -e .[dev]

# Run the application
cpu-monitor
```

### Usage Examples

```bash
# Basic usage - overall CPU view
cpu-monitor

# Per-core view with fast updates
cpu-monitor --per-core --interval 250

# Limit to first 4 cores with extended history
cpu-monitor --per-core --max-cores 4 --time-window 120

# Custom window size
cpu-monitor --width 1200 --height 600
```

## Installation from Source

```bash
# Clone and install in development mode
git clone https://github.com/johnmulder/cpu-monitor.git
cd cpu-monitor
pip install -e .[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit      # Unit tests only
pytest -m integration  # Integration tests only
```

## Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality and consistency.
The hooks include code formatting, linting, type checking, and security scanning.

### Setup

```bash
# Install development dependencies (includes pre-commit)
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Install commit message hooks (optional)
pre-commit install --hook-type commit-msg
```

### Running Hooks

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run all hooks on staged files only
pre-commit run

# Run specific hooks
pre-commit run black           # Format code with black
pre-commit run ruff            # Run ruff linter
pre-commit run mypy            # Type checking
pre-commit run bandit          # Security scanning
pre-commit run markdownlint    # Markdown formatting

# Skip hooks for a commit (use sparingly)
git commit --no-verify -m "commit message"
```

### Available Hooks

| Hook | Description | Auto-fixes |
|------|-------------|------------|
| `black` | Python code formatter | ✅ |
| `isort` | Import sorter | ✅ |
| `ruff` | Fast Python linter | ✅ (some rules) |
| `mypy` | Static type checker | ❌ |
| `trailing-whitespace` | Remove trailing whitespace | ✅ |
| `end-of-file-fixer` | Ensure files end with newline | ✅ |
| `mixed-line-ending` | Fix line endings | ✅ |
| `check-yaml` | Validate YAML syntax | ❌ |
| `check-toml` | Validate TOML syntax | ❌ |
| `check-json` | Validate JSON syntax | ❌ |
| `check-merge-conflict` | Detect merge conflicts | ❌ |
| `bandit` | Security vulnerability scanner | ❌ |
| `check-added-large-files` | Prevent large file commits | ❌ |
| `markdownlint` | Markdown linter/formatter | ✅ |

### Hook Configuration

Pre-commit configuration is defined in `.pre-commit-config.yaml`. Key settings:

- **Black**: Line length 88, Python 3.8+ compatible
- **Ruff**: Auto-fix enabled, comprehensive rule set
- **MyPy**: Ignore missing imports, exclude tests
- **Bandit**: Security scan with JSON report output
- **MarkdownLint**: Auto-fix common markdown issues

### Troubleshooting

```bash
# Update hook versions
pre-commit autoupdate

# Clear hook cache if issues occur
pre-commit clean

# Reinstall hooks
pre-commit uninstall
pre-commit install

# Run individual tools manually
black src/ tests/
ruff check --fix src/ tests/
mypy src/
bandit -r src/
```

## Requirements

- **Python**: 3.8 or higher
- **GUI**: tkinter (often included with Python)
- **System Monitoring**: psutil (recommended)
- **Fallback**: Linux `/proc/stat` support (Linux only)

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --interval` | Update interval in milliseconds | 500 |
| `-t, --time-window` | History window in seconds | 60 |
| `-w, --width` | Canvas width in pixels | 900 |
| `--height` | Canvas height in pixels | 345 |
| `--per-core` | Start in per-core view | False |
| `--max-cores` | Max cores to display (0=all) | 0 |

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/johnmulder/cpu-monitor.git
cd cpu-monitor

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Code Quality Tools

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Code formatting
black src/ tests/
isort src/ tests/

# Linting
ruff check src/ tests/
ruff check --fix src/ tests/  # Auto-fix issues

# Type checking
mypy src/

# Security scanning
bandit -r src/

# Run tests with coverage
pytest --cov=src --cov-report=html
```

### Project Structure

```text
src/cpu_monitor/
├── __init__.py        # Package initialization
├── main.py           # Application entry point
├── cli/              # Command line interface
│   ├── __init__.py
│   └── argument_parser.py
├── config/           # Configuration management
│   ├── __init__.py
│   └── settings.py
├── core/             # Core CPU monitoring logic
│   ├── __init__.py
│   ├── cpu_reader.py
│   └── data_models.py
└── ui/               # User interface components
    ├── __init__.py
    ├── chart_renderer.py
    ├── colors.py
    └── main_window.py
```

## License

This project is licensed under the MIT License -
see the [LICENSE](LICENSE) file for details.
