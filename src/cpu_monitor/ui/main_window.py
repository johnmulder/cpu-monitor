"""
Main application window and user interface controller.

Coordinates between CPU monitoring core and chart rendering to provide
a complete interactive application.
"""

import time
import tkinter as tk
from collections import deque
from typing import Deque, List

from ..config.settings import UIConfig
from ..core import CPUReader, CPUStatistics
from .chart_renderer import ChartRenderer
from .colors import ChartColors


class CPUGraphApp(tk.Tk):
    """Main application window for real-time CPU utilization monitoring.

    Provides overall system CPU usage and per-core monitoring with interactive controls.
    """

    def __init__(
        self,
        interval_ms: int = 500,
        history_secs: int = 60,
        show_per_core: bool = False,
        max_cores: int = 0,
    ):
        """Initialize the main application window.

        Args:
            interval_ms: Update interval in milliseconds
            history_secs: How many seconds of history to keep
            show_per_core: Start in per-core view mode
            max_cores: Maximum cores to display (0 = all)
        """
        super().__init__()

        self.interval_ms = int(interval_ms)
        self.history_points = self._calculate_history_points(history_secs)
        self.is_paused = False
        self.show_per_core = show_per_core
        self.max_cores_display = max_cores

        self.data = deque([0.0] * self.history_points, maxlen=self.history_points)
        self.per_core_data: List[Deque[float]] = []  # List of deques, one per core
        self.cpu_reader = CPUReader()

        self._setup_window()
        self._create_ui_components()
        self._initialize_per_core_data_if_needed()

        # Start monitoring
        self._start_update_loop()

    def _setup_window(self) -> None:
        """Configure the main window properties."""
        self.title(UIConfig.WINDOW_TITLE)
        self.resizable(False, False)

    def _calculate_history_points(self, history_secs: int) -> int:
        """Calculate the number of data points to keep in history."""
        return int((history_secs * 1000) // self.interval_ms)

    def _initialize_per_core_data_if_needed(self) -> None:
        """Initialize per-core data structures if needed."""
        if self.show_per_core and not self.per_core_data:
            self._initialize_per_core_data()

    def _initialize_per_core_data(self) -> None:
        """Initialize per-core data structures."""
        core_count = self.cpu_reader.get_core_count()
        # Use all cores if max_cores_display is 0, otherwise limit
        max_cores = (
            core_count
            if self.max_cores_display == 0
            else min(core_count, self.max_cores_display)
        )
        self.per_core_data = [
            deque([0.0] * self.history_points, maxlen=self.history_points)
            for _ in range(max_cores)
        ]
        self.max_cores_display = max_cores  # Update for consistent usage

    def _create_ui_components(self) -> None:
        """Create and layout all UI components."""
        main_frame = tk.Frame(self, padx=8, pady=8)
        main_frame.pack()

        self._create_canvas(main_frame)
        self._create_status_label(main_frame)
        self._create_control_buttons(main_frame)

        # Initialize chart renderer
        canvas_width, canvas_height = UIConfig.DEFAULT_CANVAS_SIZE
        self.chart_renderer = ChartRenderer(self.canvas, canvas_width, canvas_height)

    def _create_canvas(self, parent: tk.Widget) -> None:
        """Create the main drawing canvas."""
        canvas_width, canvas_height = UIConfig.DEFAULT_CANVAS_SIZE
        self.canvas = tk.Canvas(
            parent,
            width=canvas_width,
            height=canvas_height,
            bg=ChartColors.BACKGROUND,
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, columnspan=5)

    def _create_status_label(self, parent: tk.Widget) -> None:
        """Create the status information label that shows CPU statistics."""
        self.status_label = tk.Label(
            parent, text=UIConfig.INITIAL_STATUS_MESSAGE, font=("TkDefaultFont", 10)
        )
        self.status_label.grid(row=1, column=0, sticky="w", pady=(6, 0))

    def _create_control_buttons(self, parent: tk.Widget) -> None:
        """Create control buttons (Pause, Clear, Toggle View, Quit)."""
        # Define button configurations
        buttons = [
            (UIConfig.BUTTON_PAUSE, self._toggle_pause, 1),
            (UIConfig.BUTTON_CLEAR, self._clear_data, 2),
            (
                (
                    UIConfig.BUTTON_PER_CORE
                    if not self.show_per_core
                    else UIConfig.BUTTON_OVERALL
                ),
                self._toggle_view,
                3,
            ),
            (UIConfig.BUTTON_QUIT, self.destroy, 4),
        ]

        for text, command, column in buttons:
            button = tk.Button(parent, text=text, command=command)
            button.grid(row=1, column=column, padx=8, sticky="e")

            # Store references to buttons that need text updates
            if column == 1:
                self.pause_button = button
            elif column == 3:
                self.view_button = button

    def _start_update_loop(self) -> None:
        """Start the periodic update loop."""
        self.after(0, self._update_loop)

    def _toggle_pause(self) -> None:
        """Toggle between paused and running states."""
        self.is_paused = not self.is_paused
        button_text = (
            UIConfig.BUTTON_RESUME if self.is_paused else UIConfig.BUTTON_PAUSE
        )
        self.pause_button.config(text=button_text)

    def _toggle_view(self) -> None:
        """Toggle between overall and per-core view."""
        self.show_per_core = not self.show_per_core

        # Initialize per-core data if switching to per-core view
        if self.show_per_core and not self.per_core_data:
            self._initialize_per_core_data()

        # Update button text
        view_text = (
            UIConfig.BUTTON_OVERALL if self.show_per_core else UIConfig.BUTTON_PER_CORE
        )
        self.view_button.config(text=view_text)

        # Refresh the chart immediately
        self._refresh_chart()

    def _reset_data_container(self, container: Deque[float]) -> None:
        """Reset a data container to zeros."""
        container.clear()
        container.extend([0.0] * self.history_points)

    def _clear_data(self) -> None:
        """Clear all historical data and refresh the display."""
        self._reset_data_container(self.data)

        # Clear per-core data as well
        for core_data in self.per_core_data:
            self._reset_data_container(core_data)

        self._refresh_chart()

    def _calculate_statistics(self) -> CPUStatistics:
        """Calculate current CPU usage statistics."""
        if not self.data:
            return CPUStatistics(0.0, 0.0, 0.0)

        data_list = list(self.data)
        current = data_list[-1] if data_list else 0.0
        average = sum(data_list) / len(data_list)
        maximum = max(data_list)

        return CPUStatistics(current, average, maximum)

    def _update_status_display(self, stats: CPUStatistics) -> None:
        """Update the status label with current statistics."""
        timestamp = time.strftime("%H:%M:%S")

        # Add core count information
        core_count = self.cpu_reader.get_core_count()
        core_info = f" | Cores: {core_count}" if core_count > 0 else ""

        status_text = stats.format_status_text(timestamp) + core_info
        self.status_label.config(text=status_text)

    def _refresh_chart(self) -> None:
        """Refresh the chart display with current data."""
        overall_data = list(self.data)

        # Prepare per-core data if available and needed
        per_core_data = None
        if self.show_per_core and self.per_core_data:
            per_core_data = [list(core_data) for core_data in self.per_core_data]

        self.chart_renderer.render_complete_chart(
            overall_data=overall_data,
            interval_ms=self.interval_ms,
            per_core_data=per_core_data,
            show_per_core=self.show_per_core,
            max_cores=self.max_cores_display,
        )

    def _handle_update_error(self, error: Exception) -> None:
        """Handle errors that occur during the update cycle."""
        error_message = f"Error: {error}"
        self.status_label.config(text=error_message)
        # In a production app, you might want to log this error

    def _update_loop(self) -> None:
        """Main update loop - fetches CPU data and updates display."""
        try:
            if not self.is_paused:
                # Get comprehensive CPU data
                cpu_data = self.cpu_reader.get_cpu_data()

                # Update overall data
                self.data.append(cpu_data.overall)

                # Update per-core data if available and needed
                if self.show_per_core and cpu_data.has_per_core_data:
                    cores_to_update = min(
                        len(self.per_core_data), len(cpu_data.per_core)
                    )
                    for i in range(cores_to_update):
                        self.per_core_data[i].append(cpu_data.per_core[i])

                # Update display
                statistics = self._calculate_statistics()
                self._update_status_display(statistics)
                self._refresh_chart()

        except Exception as error:
            self._handle_update_error(error)
        finally:
            # Always schedule the next update
            self.after(self.interval_ms, self._update_loop)
