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

# Install dependencies
pip install psutil

# Run the application
python -m src.cpu_monitor.main
```

### Usage Examples

```bash
# Basic usage - overall CPU view
python -m src.cpu_monitor.main

# Per-core view with fast updates
python -m src.cpu_monitor.main --per-core --interval 250

# Limit to first 4 cores with extended history
python -m src.cpu_monitor.main --per-core --max-cores 4 --time-window 120

# Custom window size
python -m src.cpu_monitor.main --width 1200 --height 600
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

## Project Layout

```text
src/cpu_monitor/
├── cli/           # Command line argument parsing
├── config/        # Application configuration
├── core/          # CPU monitoring business logic
├── ui/            # User interface and visualization
└── main.py        # Application entry point
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
| `--height` | Canvas height in pixels | 320 |
| `--per-core` | Start in per-core view | False |
| `--max-cores` | Max cores to display (0=all) | 0 |

## Development

```bash
# Install development dependencies
pip install -e .[dev]

# Run pre-commit hooks
pre-commit install
pre-commit run --all-files

# Code formatting
black src/ tests/
ruff check src/ tests/

# Type checking
mypy src/
```

## License

This project is licensed under the MIT License -
see the [LICENSE](LICENSE) file for details.
