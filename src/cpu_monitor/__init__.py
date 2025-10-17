"""
CPU Utilization Monitor

Real-time CPU monitoring application with overall and per-core analysis.

Package Structure:
- config: Application configuration and settings
- core: CPU monitoring business logic
- ui: User interface and visualization
- cli: Command line interface
"""

__version__ = "2.0.0"
__author__ = "CPU Monitor Team"

from .cli import parse_arguments
from .config import AppConfig
from .core import CPUCoreData, CPUReader, CPUReaderError, CPUStatistics
from .ui import ChartColors, ChartLayout, ChartRenderer, CPUGraphApp

__all__ = [
    "AppConfig",
    "CPUReader",
    "CPUReaderError",
    "CPUStatistics",
    "CPUCoreData",
    "CPUGraphApp",
    "ChartRenderer",
    "ChartColors",
    "ChartLayout",
    "parse_arguments",
]
