"""
Application configuration settings and data structures.

Contains configuration classes and constants for the CPU monitoring application.
"""

from dataclasses import dataclass


@dataclass
class AppConfig:
    """Main application configuration.

    Contains user-configurable settings for display, timing, and core limits.
    """

    interval_ms: int = 500
    history_secs: int = 60
    canvas_width: int = 900
    canvas_height: int = 320
    show_per_core: bool = False
    max_cores_display: int = 0  # 0 = show all cores


@dataclass
class UIConfig:
    """UI configuration constants."""

    DEFAULT_CANVAS_SIZE = (900, 320)
    WINDOW_TITLE = "CPU Utilization Monitor"
    INITIAL_STATUS_MESSAGE = "Initializing CPU monitor..."

    BUTTON_PAUSE = "Pause"
    BUTTON_RESUME = "Resume"
    BUTTON_CLEAR = "Clear"
    BUTTON_QUIT = "Quit"
    BUTTON_PER_CORE = "Per-Core"
    BUTTON_OVERALL = "Overall"
