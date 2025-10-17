"""
UI color schemes and layout configuration.

Centralizes visual styling constants for consistent theming.
"""


class ChartColors:
    """Color scheme for the CPU utilization chart.

    Provides a dark theme optimized for readability with distinct colors for multi-core visualization.
    """

    BACKGROUND = "#0f1115"
    BORDER = "#2a2f3a"
    GRID = "#1c2029"
    TEXT = "#9aa0aa"
    TITLE = "#d7dde7"
    LINE = "#6fa8ff"
    FILL = "#264b8a"

    CORE_PALETTE = [
        "#6fa8ff",
        "#ff6b6b",
        "#4ecdc4",
        "#45b7d1",
        "#96ceb4",
        "#feca57",
        "#ff9ff3",
        "#54a0ff",
        "#5f27cd",
        "#00d2d3",
        "#ff9f43",
        "#10ac84",
        "#a55eea",
        "#26de81",
        "#fd79a8",
        "#fdcb6e",
        "#6c5ce7",
        "#fd9644",
        "#e17055",
        "#74b9ff",
    ]

    @classmethod
    def get_core_color(cls, core_index: int) -> str:
        """Get color for a specific core, cycling through available colors if needed."""
        return cls.CORE_PALETTE[core_index % len(cls.CORE_PALETTE)]


class ChartLayout:
    """Chart layout and spacing configuration.

    Defines spacing, margins, and layout constants for consistent chart appearance.
    """

    MARGINS = {"left": 45, "right": 10, "top": 10, "bottom": 28}
    Y_AXIS_TICKS = (0, 25, 50, 75, 100)
    LEGEND_ITEM_WIDTH = 70  # Pixels per legend item
    LEGEND_ROW_HEIGHT = 15  # Pixels per legend row
