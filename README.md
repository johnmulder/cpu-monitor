# CPU Utilization Monitor

Real-time CPU usage monitor with per-core charts and an interactive Tkinter interface.
Cross-platform, lightweight, and built with Python 3.8+.

## Features

- Live Updates: Configurable intervals (100 ms–10 s) and history (10 s–1 h)
- Per-Core View: Auto-detects all cores; color-coded visualization
- Interactive UI: Dark theme, pause/clear/toggle controls, smooth charts
- Cross-Platform: Works on macOS, Linux, and Windows via psutil

## Quick Start

```bash
git clone <repo-url>
cd cpu_util
pip install psutil
python main.py
```

## Example Use

```bash
python main.py --per-core
python main.py --max-cores 4 --interval 250
python main.py --time-window 120
```

## Requirements

- Python 3.8 or higher
- tkinter (often built-in)
- psutil (recommended)

## License

MIT License - see LICENSE file.
