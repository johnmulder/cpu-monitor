# CPU Utilization Monitor

[![CI/CD Pipeline](https://github.com/johnmulder/cpu-monitor/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/johnmulder/cpu-monitor/actions)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Real-time CPU usage monitor with per-core charts and a Tkinter interface.

## Features

- Live updates with configurable intervals and history windows
- Overall and per-core CPU charts
- Pause, clear, view toggle, and quit controls
- Cross-platform CPU readings through `psutil`

## Screenshots

### Overall CPU Usage View

![Overall CPU Usage](docs/images/cpu-monitor-overall.png)

### Per-Core CPU Usage View

![Per-Core CPU Usage](docs/images/cpu-monitor-per-core.png)

## Quick Start

```bash
git clone https://github.com/johnmulder/cpu-monitor.git
cd cpu-monitor
pip install -e .
cpu-monitor
```

For development:

```bash
pip install -e .[dev]
pre-commit install
```

## Usage

```bash
# Overall CPU view
cpu-monitor

# Per-core view with fast updates
cpu-monitor --per-core --interval 250

# Limit to first 4 cores with extended history
cpu-monitor --per-core --max-cores 4 --time-window 120
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --interval` | Update interval in milliseconds | 500 |
| `-t, --time-window` | History window in seconds | 60 |
| `--per-core` | Start in per-core view | False |
| `--max-cores` | Max cores to display, 0 means all | 0 |

## Development

After explicit development setup, use the existing environment for check-only
verification:

```bash
pytest
ruff check src tests
ruff format --check src tests
mypy src
```

Formatting repair and hooks are separate operations:

```bash
ruff format src tests
pre-commit run --all-files
```

Hooks may fix source or Markdown and install missing type packages. Preserve
their security and documentation checks, inspect any resulting diff, and rerun
verification after repairs. CI runs these hooks separately from pytest.

The build/security job audits the complete installed development, build and
scanner inventory with `pip-audit`, then builds with that checked toolchain. It
also installs the wheel in a separate runtime-only environment, checks the CLI,
and audits that environment's inventory. The project's own package is excluded
from dependency inventories because its source is checked by Bandit. Both
dependency audits and Bandit must pass; reports and inventories are retained
even on failure. Security tooling runs on Python 3.13 without changing the
application's Python 3.8 support or its test matrix.

## Project Structure

```text
src/cpu_monitor/
├── __init__.py
├── main.py
├── cli/
│   ├── __init__.py
│   └── argument_parser.py
├── core/
│   ├── __init__.py
│   ├── cpu_reader.py
│   └── data_models.py
└── ui/
    ├── __init__.py
    ├── chart_renderer.py
    ├── colors.py
    └── main_window.py
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
