"""
Chart rendering system for CPU utilization visualization.

Handles drawing operations for overall system CPU usage and per-core monitoring with interactive legends.
"""

import tkinter as tk
from typing import List, Optional, Tuple

from .colors import ChartColors, ChartLayout


class ChartRenderer:
    """Professional chart rendering for CPU utilization data.

    Supports overall CPU usage (single line with fill) and per-core usage (multiple colored lines with legend).
    """

    def __init__(self, canvas: tk.Canvas, width: int, height: int):
        """Initialize the chart renderer.

        Args:
            canvas: Tkinter canvas for drawing
            width: Canvas width in pixels
            height: Canvas height in pixels
        """
        self.canvas = canvas
        self.width = width
        self.height = height

    @property
    def plot_boundaries(self) -> Tuple[int, int, int, int]:
        """Calculate the actual plotting area within canvas margins."""
        left = ChartLayout.MARGINS["left"]
        top = ChartLayout.MARGINS["top"]
        right = self.width - ChartLayout.MARGINS["right"]
        bottom = self.height - ChartLayout.MARGINS["bottom"]
        return left, top, right, bottom

    def clear_canvas(self) -> None:
        """Clear all elements from the canvas."""
        self.canvas.delete("all")

    def render_complete_chart(
        self,
        overall_data: List[float],
        interval_ms: int,
        per_core_data: Optional[List[List[float]]] = None,
        show_per_core: bool = False,
        max_cores: int = 0,
    ) -> None:
        """Render the complete CPU utilization chart.

        Args:
            overall_data: Overall CPU usage percentages over time
            interval_ms: Update interval for time axis calculation
            per_core_data: Per-core usage data (optional)
            show_per_core: Whether to show per-core view
            max_cores: Maximum cores to display (0 = all)
        """
        self.clear_canvas()
        boundaries = self.plot_boundaries

        self._draw_chart_infrastructure(boundaries, len(overall_data), interval_ms)

        if show_per_core and per_core_data:
            self._render_per_core_view(per_core_data, boundaries, max_cores)
        else:
            self._render_overall_view(overall_data, boundaries)

    def _draw_chart_infrastructure(
        self, boundaries: Tuple[int, int, int, int], data_points: int, interval_ms: int
    ) -> None:
        """Draw the basic chart structure (borders, grid, axes)."""
        self._draw_chart_border_and_grid(boundaries)
        self._draw_time_axis_labels(data_points, interval_ms, boundaries)

    def _draw_chart_border_and_grid(
        self, boundaries: Tuple[int, int, int, int]
    ) -> None:
        """Draw the main chart border and percentage grid lines."""
        left, top, right, bottom = boundaries
        plot_height = bottom - top

        self.canvas.create_rectangle(
            left, top, right, bottom, outline=ChartColors.BORDER
        )

        for percentage in ChartLayout.Y_AXIS_TICKS:
            y_position = bottom - (percentage / 100.0) * plot_height

            self.canvas.create_line(
                left, y_position, right, y_position, fill=ChartColors.GRID, dash=(2, 3)
            )
            # Percentage label
            self.canvas.create_text(
                left - 8,
                y_position,
                text=f"{percentage}%",
                fill=ChartColors.TEXT,
                anchor="e",
                font=("TkDefaultFont", 9),
            )

    def _draw_time_axis_labels(
        self, data_points: int, interval_ms: int, boundaries: Tuple[int, int, int, int]
    ) -> None:
        """Draw time axis with second markers and labels."""
        left, _top, right, bottom = boundaries
        plot_width = right - left

        total_seconds = data_points * interval_ms / 1000.0
        if total_seconds <= 0:
            return

        # Calculate reasonable step size for time labels
        time_step = max(5, int(total_seconds // 10) or 1)

        for seconds in range(0, int(total_seconds) + 1, time_step):
            # Calculate x position (newest on right, oldest on left)
            x_position = right - (seconds / total_seconds) * plot_width

            # Draw tick mark and label
            self.canvas.create_line(
                x_position, bottom, x_position, bottom + 4, fill=ChartColors.BORDER
            )
            self.canvas.create_text(
                x_position,
                bottom + 14,
                text=f"{seconds}s",
                fill=ChartColors.TEXT,
                anchor="n",
                font=("TkDefaultFont", 9),
            )

    def _render_per_core_view(
        self,
        per_core_data: List[List[float]],
        boundaries: Tuple[int, int, int, int],
        max_cores: int,
    ) -> None:
        """Render the per-core CPU usage view."""
        # Draw all core lines
        self._draw_all_core_lines(per_core_data, boundaries, max_cores)

        # Draw legend
        self._draw_core_legend(len(per_core_data), max_cores, boundaries)

        # Set title
        cores_displayed = (
            len(per_core_data) if max_cores == 0 else min(len(per_core_data), max_cores)
        )
        title = f"CPU Utilization - Per Core ({cores_displayed} cores)"
        self._draw_chart_title(title, boundaries)

    def _render_overall_view(
        self, overall_data: List[float], boundaries: Tuple[int, int, int, int]
    ) -> None:
        """Render the overall CPU usage view."""
        # Draw main usage line
        line_points = self._draw_cpu_usage_line(overall_data, boundaries)

        # Draw filled area under curve
        self._draw_fill_under_curve(line_points, boundaries)

        # Set title
        self._draw_chart_title("CPU Utilization (%) - Overall", boundaries)

    def _draw_cpu_usage_line(
        self,
        usage_data: List[float],
        boundaries: Tuple[int, int, int, int],
        color: Optional[str] = None,
    ) -> List[float]:
        """Draw a single CPU usage line on the chart."""
        if len(usage_data) <= 1:
            return []

        left, top, right, bottom = boundaries
        plot_width = right - left
        plot_height = bottom - top
        data_count = len(usage_data)

        # Calculate line coordinates
        line_points = []
        for i, cpu_percent in enumerate(usage_data):
            # X: oldest on left, newest on right
            x = left + (i / (data_count - 1)) * plot_width
            # Y: 0% at bottom, 100% at top
            y = bottom - (cpu_percent / 100.0) * plot_height
            line_points.extend([x, y])

        # Draw the line
        line_color = color or ChartColors.LINE
        self.canvas.create_line(*line_points, fill=line_color, width=2, smooth=True)

        return line_points

    def _draw_all_core_lines(
        self,
        core_data: List[List[float]],
        boundaries: Tuple[int, int, int, int],
        max_cores: int = 0,
    ) -> None:
        """Draw CPU usage lines for all cores with different colors."""
        cores_to_display = (
            len(core_data) if max_cores == 0 else min(len(core_data), max_cores)
        )

        for core_index in range(cores_to_display):
            if core_index < len(core_data) and core_data[core_index]:
                color = ChartColors.get_core_color(core_index)
                self._draw_cpu_usage_line(core_data[core_index], boundaries, color)

    def _draw_core_legend(
        self, core_count: int, max_cores: int, boundaries: Tuple[int, int, int, int]
    ) -> None:
        """Draw a color-coded legend showing core assignments."""
        left, top, right, _bottom = boundaries
        cores_to_show = core_count if max_cores == 0 else min(core_count, max_cores)

        if cores_to_show == 0:
            return

        # Calculate layout with row wrapping
        available_width = right - left
        cores_per_row = max(1, available_width // ChartLayout.LEGEND_ITEM_WIDTH)
        legend_start_y = top + 15

        for core_index in range(cores_to_show):
            color = ChartColors.get_core_color(core_index)

            # Calculate position with row wrapping
            row_number = core_index // cores_per_row
            column_number = core_index % cores_per_row

            x = left + (column_number * ChartLayout.LEGEND_ITEM_WIDTH)
            y = legend_start_y + (row_number * ChartLayout.LEGEND_ROW_HEIGHT)

            # Draw color indicator and label
            self.canvas.create_rectangle(x, y, x + 8, y + 8, fill=color, outline=color)
            self.canvas.create_text(
                x + 12,
                y + 4,
                text=f"Core {core_index}",
                fill=ChartColors.TEXT,
                anchor="w",
                font=("TkDefaultFont", 8),
            )

    def _draw_fill_under_curve(
        self, line_points: List[float], boundaries: Tuple[int, int, int, int]
    ) -> None:
        """Draw a subtle filled area under the CPU usage curve."""
        if len(line_points) < 4:
            return

        left, _top, right, bottom = boundaries

        # Create polygon points: bottom-left, line points, bottom-right
        polygon_points = [left, bottom] + line_points + [right, bottom]

        self.canvas.create_polygon(
            *polygon_points, fill=ChartColors.FILL, stipple="gray25", outline=""
        )

    def _draw_chart_title(
        self, title_text: str, boundaries: Tuple[int, int, int, int]
    ) -> None:
        """Draw the main chart title centered above the plot area."""
        left, top, right, _bottom = boundaries
        center_x = (left + right) / 2

        self.canvas.create_text(
            center_x,
            top - 2,
            text=title_text,
            fill=ChartColors.TITLE,
            anchor="s",
            font=("TkDefaultFont", 11, "bold"),
        )
