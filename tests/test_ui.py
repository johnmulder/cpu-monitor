"""Tests for UI components, colors, and chart rendering."""

import tkinter as tk
from collections import deque
from unittest.mock import Mock, patch

import pytest

from cpu_monitor.core.data_models import CPUCoreData, CPUStatistics
from cpu_monitor.ui.chart_renderer import ChartRenderer
from cpu_monitor.ui.colors import ChartColors, ChartLayout
from cpu_monitor.ui.main_window import CPUGraphApp


@pytest.fixture
def mock_canvas():
    """Mock Tkinter Canvas."""
    return Mock(spec=tk.Canvas)


@pytest.fixture
def chart_renderer(mock_canvas):
    """ChartRenderer with mock canvas."""
    return ChartRenderer(mock_canvas, width=800, height=400)


class TestChartColors:
    """ChartColors tests."""

    def test_color_constants_exist(self):
        """Test color constants exist."""
        assert hasattr(ChartColors, "BACKGROUND")
        assert hasattr(ChartColors, "BORDER")
        assert hasattr(ChartColors, "GRID")
        assert hasattr(ChartColors, "TEXT")
        assert hasattr(ChartColors, "TITLE")
        assert hasattr(ChartColors, "LINE")
        assert hasattr(ChartColors, "FILL")
        assert hasattr(ChartColors, "CORE_PALETTE")

    def test_color_format_validation(self):
        """Test hex color format."""
        colors_to_test = [
            ChartColors.BACKGROUND,
            ChartColors.BORDER,
            ChartColors.GRID,
            ChartColors.TEXT,
            ChartColors.TITLE,
            ChartColors.LINE,
            ChartColors.FILL,
        ]

        for color in colors_to_test:
            assert isinstance(color, str)
            assert color.startswith("#")
            assert len(color) == 7  # #RRGGBB format
            hex_part = color[1:]
            int(hex_part, 16)  # Should not raise ValueError

    def test_core_palette_properties(self):
        """Test core color palette properties."""
        palette = ChartColors.CORE_PALETTE

        assert isinstance(palette, (list, tuple))
        assert len(palette) >= 8  # Should have at least 8 different colors

        # All colors should be valid hex
        for color in palette:
            assert isinstance(color, str)
            assert color.startswith("#")
            assert len(color) == 7
            int(color[1:], 16)  # Validate hex

    def test_get_core_color_method(self):
        """Test get_core_color method functionality."""
        color0 = ChartColors.get_core_color(0)
        color1 = ChartColors.get_core_color(1)

        assert color0 != color1  # Different cores should have different colors
        assert color0 in ChartColors.CORE_PALETTE
        assert color1 in ChartColors.CORE_PALETTE
        palette_len = len(ChartColors.CORE_PALETTE)
        color_wrapped = ChartColors.get_core_color(palette_len)
        color_first = ChartColors.get_core_color(0)
        assert color_wrapped == color_first  # Should wrap around

    def test_distinct_colors(self):
        """Test that core colors are visually distinct."""
        palette = ChartColors.CORE_PALETTE

        # Should have no duplicate colors in palette
        assert len(palette) == len(set(palette))

        # Basic distinctness check - colors should not be identical or too similar
        for i, color in enumerate(palette[:6]):
            for j, other_color in enumerate(palette[:6]):
                if i != j:
                    # Colors should be different
                    assert color.lower() != other_color.lower()

                    rgb1 = (
                        int(color[1:3], 16),
                        int(color[3:5], 16),
                        int(color[5:7], 16),
                    )
                    rgb2 = (
                        int(other_color[1:3], 16),
                        int(other_color[3:5], 16),
                        int(other_color[5:7], 16),
                    )

                    # At least one RGB component should differ by 20+ (out of 255)
                    max_diff = max(abs(c1 - c2) for c1, c2 in zip(rgb1, rgb2))
                    error_message = f"Colors too similar: {color} vs {other_color}"
                    assert max_diff >= 20, error_message


class TestChartLayout:
    """Test cases for ChartLayout class."""

    def test_layout_constants_exist(self):
        """Test that all expected layout constants are defined."""
        assert hasattr(ChartLayout, "MARGINS")
        assert hasattr(ChartLayout, "Y_AXIS_TICKS")
        assert hasattr(ChartLayout, "LEGEND_ITEM_WIDTH")
        assert hasattr(ChartLayout, "LEGEND_ROW_HEIGHT")

    def test_margin_values(self):
        """Test that margin values are reasonable."""
        margins = ChartLayout.MARGINS

        assert isinstance(margins, dict)
        required_keys = ["left", "right", "top", "bottom"]

        for key in required_keys:
            assert key in margins
            assert isinstance(margins[key], int)
            assert 0 <= margins[key] <= 100  # Reasonable margin sizes

    def test_legend_properties(self):
        """Test legend layout properties."""
        assert isinstance(ChartLayout.LEGEND_ITEM_WIDTH, int)
        assert isinstance(ChartLayout.LEGEND_ROW_HEIGHT, int)

        assert ChartLayout.LEGEND_ITEM_WIDTH > 0
        assert ChartLayout.LEGEND_ROW_HEIGHT > 0

    def test_y_axis_ticks(self):
        """Test Y-axis tick configuration."""
        ticks = ChartLayout.Y_AXIS_TICKS
        assert isinstance(ticks, tuple)
        assert len(ticks) >= 3  # Should have at least 0%, 50%, 100%
        assert 0 in ticks and 100 in ticks  # Should include boundaries

        # Should be sorted ascending
        assert list(ticks) == sorted(ticks)


class TestChartRenderer:
    """Test cases for ChartRenderer class."""

    def test_initialization(self, mock_canvas):
        """Test ChartRenderer initialization."""
        renderer = ChartRenderer(mock_canvas, width=900, height=345)

        assert renderer.canvas == mock_canvas
        assert renderer.width == 900
        assert renderer.height == 345

    def test_clear_canvas(self, chart_renderer, mock_canvas):
        """Test canvas clearing functionality."""
        chart_renderer.clear_canvas()

        # Should call delete on canvas to clear all items
        mock_canvas.delete.assert_called_once_with("all")

    def test_plot_boundaries_calculation(self, chart_renderer):
        """Test plot boundaries calculation."""
        boundaries = chart_renderer.plot_boundaries

        assert isinstance(boundaries, tuple)
        assert len(boundaries) == 4  # left, top, right, bottom
        left, top, right, bottom = boundaries

        # Boundaries should be within canvas dimensions
        assert 0 <= left < right <= 800
        assert 0 <= top < bottom <= 400

        # Should account for margins
        assert left >= ChartLayout.MARGINS["left"]
        assert top >= ChartLayout.MARGINS["top"]

    def test_render_complete_chart_calls_clear(self, chart_renderer, mock_canvas):
        """Test that render_complete_chart clears the canvas."""
        # Test data
        overall_data = [25.0, 30.0, 35.0, 40.0, 45.0]
        interval_ms = 500

        chart_renderer.render_complete_chart(overall_data, interval_ms)

        # Should clear canvas
        mock_canvas.delete.assert_called_with("all")

    def test_render_chart_with_overall_data(self, chart_renderer, mock_canvas):
        """Test rendering chart with overall CPU data."""
        usage_data = [10.0, 20.0, 30.0, 40.0, 50.0]
        interval_ms = 1000

        # This should not raise any errors
        chart_renderer.render_complete_chart(usage_data, interval_ms)

        # Should have called canvas methods for drawing
        assert mock_canvas.delete.called  # Canvas cleared
        assert mock_canvas.create_rectangle.called or mock_canvas.create_line.called

    def test_render_chart_with_per_core_data(self, chart_renderer, mock_canvas):
        """Test rendering chart with per-core CPU data."""
        overall_data = [25.0, 30.0, 35.0, 40.0]
        per_core_data = [
            [20.0, 25.0, 30.0, 35.0],  # Core 0
            [30.0, 35.0, 40.0, 45.0],  # Core 1
        ]
        interval_ms = 1000

        # This should not raise any errors
        chart_renderer.render_complete_chart(
            overall_data, interval_ms, per_core_data, show_per_core=True, max_cores=2
        )

        # Should have called canvas methods for drawing
        assert mock_canvas.delete.called  # Canvas cleared
        assert mock_canvas.create_line.called or mock_canvas.create_text.called

    def test_render_empty_data(self, chart_renderer, mock_canvas):
        """Test rendering with empty or minimal data."""
        # Should handle empty data gracefully
        chart_renderer.render_complete_chart([], 1000)

        # Should still clear and draw basic structure
        assert mock_canvas.delete.called

    def test_render_legend_with_zero_cores(self, chart_renderer, mock_canvas):
        """Test legend rendering with zero cores (edge case)."""

        # Test the specific case where cores_to_show == 0
        boundaries = (10, 10, 100, 50)  # left, top, right, bottom

        # This should trigger the early return on line 235
        chart_renderer._draw_core_legend(0, 4, boundaries)


class TestChartRendererIntegration:
    """Integration tests for chart rendering functionality."""

    def test_realistic_chart_rendering(self, mock_canvas):
        """Test rendering with realistic data."""
        renderer = ChartRenderer(mock_canvas, width=900, height=345)

        # Realistic CPU data (2 minutes at 1-second intervals)
        overall_data = [25.0 + (i % 30) * 2.0 for i in range(120)]
        per_core_data = [
            [20.0 + (i % 25) * 1.5 for i in range(120)],  # Core 0
            [30.0 + (i % 35) * 2.0 for i in range(120)],  # Core 1
            [15.0 + (i % 40) * 1.8 for i in range(120)],  # Core 2
            [35.0 + (i % 20) * 2.2 for i in range(120)],  # Core 3
        ]

        renderer.render_complete_chart(
            overall_data=overall_data,
            interval_ms=1000,
            per_core_data=None,
            show_per_core=False,
        )

        renderer.render_complete_chart(
            overall_data=overall_data,
            interval_ms=1000,
            per_core_data=per_core_data,
            show_per_core=True,
            max_cores=4,
        )

        # Should have made multiple canvas calls for complex rendering
        assert mock_canvas.delete.call_count >= 2  # Clear called for each render
        assert mock_canvas.create_line.call_count >= 2  # Lines drawn

    def test_boundary_data_handling(self, mock_canvas):
        """Test handling of boundary conditions in data."""
        renderer = ChartRenderer(mock_canvas, width=800, height=400)

        # Test with minimal data
        minimal_data = [50.0]
        renderer.render_complete_chart(minimal_data, interval_ms=1000)

        extreme_data = [0.0, 100.0, 0.0, 100.0]
        renderer.render_complete_chart(extreme_data, interval_ms=500)

        # Should handle both cases without errors
        assert mock_canvas.delete.call_count >= 2


class TestCPUGraphApp:
    """Tests for the main application window."""

    @pytest.fixture
    def mock_cpu_reader(self):
        """Mock CPU reader."""
        mock = Mock()
        mock.get_core_count.return_value = 4
        mock.get_cpu_data.return_value = CPUCoreData(
            overall=45.0, per_core=[25.0, 35.0, 55.0, 65.0], core_count=4
        )
        return mock

    def test_calculate_history_points(self):
        """Test history points calculation."""
        # Test the method in isolation without creating the full app
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(
                    CPUGraphApp
                )  # Create without calling __init__
                app.interval_ms = 500

                result = app._calculate_history_points(60)
                assert result == 120  # 60 seconds * 1000ms / 500ms interval

    def test_calculate_statistics_with_data(self):
        """Test statistics calculation with data."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.data = deque([10.0, 20.0, 30.0, 40.0, 50.0])

                stats = app._calculate_statistics()

                assert isinstance(stats, CPUStatistics)
                assert stats.current == 50.0  # Last value
                assert stats.average == 30.0  # Average
                assert stats.maximum == 50.0  # Maximum

    def test_calculate_statistics_empty_data(self):
        """Test statistics calculation with empty data."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.data = deque()

                stats = app._calculate_statistics()

                assert isinstance(stats, CPUStatistics)
                assert stats.current == 0.0
                assert stats.average == 0.0
                assert stats.maximum == 0.0

    @patch("time.strftime")
    def test_update_status_display(self, mock_strftime):
        """Test status display update."""
        mock_strftime.return_value = "12:34:56"

        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.status_label = Mock()
                app.cpu_reader = Mock()
                app.cpu_reader.get_core_count.return_value = 4

                stats = CPUStatistics(current=45.0, average=40.0, maximum=80.0)
                app._update_status_display(stats)

                app.status_label.config.assert_called_once()
                args, kwargs = app.status_label.config.call_args
                status_text = kwargs.get("text", "")

                assert "12:34:56" in status_text
                assert "45.0%" in status_text
                assert "40.0%" in status_text
                assert "80.0%" in status_text
                assert "Cores: 4" in status_text

    def test_clear_data(self):
        """Test data clearing functionality."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.history_points = 10

                # Add some data
                app.data = deque([10.0, 20.0, 30.0])
                app.per_core_data = [deque([5.0, 15.0, 25.0]) for _ in range(2)]

                # Mock the refresh chart method
                app._refresh_chart = Mock()

                app._clear_data()

                # Check that data is cleared and filled with zeros
                assert len(app.data) == 10
                assert all(x == 0.0 for x in app.data)
                assert all(len(core_data) == 10 for core_data in app.per_core_data)
                assert all(
                    all(x == 0.0 for x in core_data) for core_data in app.per_core_data
                )
                app._refresh_chart.assert_called_once()

    def test_toggle_pause(self):
        """Test pause/resume toggle."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.pause_button = Mock()
                app.is_paused = False

                app._toggle_pause()
                assert app.is_paused is True
                app.pause_button.config.assert_called_with(text="Resume")

                app._toggle_pause()
                assert app.is_paused is False
                app.pause_button.config.assert_called_with(text="Pause")

    def test_toggle_view(self):
        """Test view toggle between overall and per-core."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.view_button = Mock()
                app._refresh_chart = Mock()
                app.show_per_core = False
                app.per_core_data = []
                app._initialize_per_core_data = Mock()

                app._toggle_view()
                assert app.show_per_core is True
                app._initialize_per_core_data.assert_called_once()
                app.view_button.config.assert_called_with(text="Overall")
                app._refresh_chart.assert_called_once()

    def test_handle_update_error(self):
        """Test error handling in updates."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.status_label = Mock()

                test_error = RuntimeError("Test error")
                app._handle_update_error(test_error)

                app.status_label.config.assert_called_once_with(
                    text="Error: Test error"
                )

    def test_refresh_chart_overall_view(self):
        """Test chart refresh in overall view."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.chart_renderer = Mock()
                app.data = deque([10.0, 20.0, 30.0])
                app.show_per_core = False
                app.per_core_data = []
                app.interval_ms = 500
                app.max_cores_display = 0

                app._refresh_chart()

                app.chart_renderer.render_complete_chart.assert_called_once()
                args, kwargs = app.chart_renderer.render_complete_chart.call_args

                assert kwargs["overall_data"] == [10.0, 20.0, 30.0]
                assert kwargs["show_per_core"] is False
                assert kwargs["per_core_data"] is None

    def test_refresh_chart_per_core_view(self):
        """Test chart refresh in per-core view."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.chart_renderer = Mock()
                app.data = deque([30.0])
                app.show_per_core = True
                app.per_core_data = [deque([10.0]), deque([20.0])]
                app.interval_ms = 1000
                app.max_cores_display = 2

                app._refresh_chart()

                app.chart_renderer.render_complete_chart.assert_called_once()
                args, kwargs = app.chart_renderer.render_complete_chart.call_args

                assert kwargs["overall_data"] == [30.0]
                assert kwargs["show_per_core"] is True
                assert kwargs["per_core_data"] == [[10.0], [20.0]]

    def test_initialize_per_core_data(self):
        """Test per-core data initialization."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.cpu_reader = Mock()
                app.cpu_reader.get_core_count.return_value = 4
                app.max_cores_display = 0
                app.history_points = 10
                app.per_core_data = []

                app._initialize_per_core_data()

                assert len(app.per_core_data) == 4
                assert all(
                    isinstance(core_data, deque) for core_data in app.per_core_data
                )
                assert all(len(core_data) == 10 for core_data in app.per_core_data)
                assert app.max_cores_display == 4

    def test_initialize_per_core_data_with_limit(self):
        """Test per-core data initialization with core limit."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.cpu_reader = Mock()
                app.cpu_reader.get_core_count.return_value = 8
                app.max_cores_display = 4
                app.history_points = 20
                app.per_core_data = []

                app._initialize_per_core_data()

                assert len(app.per_core_data) == 4
                assert app.max_cores_display == 4

    def test_update_loop_normal_operation(self):
        """Test normal update loop operation."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.is_paused = False
                app.show_per_core = True
                app.per_core_data = [deque() for _ in range(4)]
                app.data = deque()
                app.interval_ms = 500

                # Mock dependencies
                app.cpu_reader = Mock()
                app.cpu_reader.get_cpu_data.return_value = CPUCoreData(
                    overall=45.0, per_core=[25.0, 35.0, 55.0, 65.0], core_count=4
                )
                app._calculate_statistics = Mock(
                    return_value=CPUStatistics(45.0, 40.0, 50.0)
                )
                app._update_status_display = Mock()
                app._refresh_chart = Mock()

                with patch.object(app, "after") as mock_after:
                    app._update_loop()

                    # Check that data was added
                    assert app.data[-1] == 45.0
                    assert app.per_core_data[0][-1] == 25.0
                    assert app.per_core_data[1][-1] == 35.0

                    app._calculate_statistics.assert_called_once()
                    app._update_status_display.assert_called_once()
                    app._refresh_chart.assert_called_once()
                    mock_after.assert_called_once_with(500, app._update_loop)

    def test_update_loop_paused(self):
        """Test update loop when paused."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.is_paused = True
                app.cpu_reader = Mock()
                app.interval_ms = 500

                with patch.object(app, "after") as mock_after:
                    app._update_loop()

                    # Should not call CPU reader when paused
                    app.cpu_reader.get_cpu_data.assert_not_called()
                    mock_after.assert_called_once_with(500, app._update_loop)

    def test_update_loop_error_handling(self):
        """Test update loop error handling."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.is_paused = False
                app.cpu_reader = Mock()
                app.cpu_reader.get_cpu_data.side_effect = RuntimeError("CPU read error")
                app._handle_update_error = Mock()
                app.interval_ms = 1000

                with patch.object(app, "after") as mock_after:
                    app._update_loop()

                    app._handle_update_error.assert_called_once()
                    mock_after.assert_called_once_with(1000, app._update_loop)

    def test_setup_window(self):
        """Test window setup."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.title = Mock()
                app.resizable = Mock()

                app._setup_window()

                app.title.assert_called_once()
                app.resizable.assert_called_once_with(False, False)

    def test_start_update_loop(self):
        """Test update loop initialization."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)

                with patch.object(app, "after") as mock_after:
                    app._start_update_loop()

                    mock_after.assert_called_once_with(0, app._update_loop)

    def test_create_canvas_functionality(self):
        """Test canvas creation with mocked components."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)

                # Mock UI components
                mock_parent = Mock()
                mock_canvas = Mock()

                with patch("tkinter.Canvas", return_value=mock_canvas):
                    app._create_canvas(mock_parent)

                    assert app.canvas == mock_canvas
                    mock_canvas.grid.assert_called_once()

    def test_create_status_label_functionality(self):
        """Test status label creation."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)

                mock_parent = Mock()
                mock_label = Mock()

                with patch("tkinter.Label", return_value=mock_label):
                    app._create_status_label(mock_parent)

                    assert app.status_label == mock_label
                    mock_label.grid.assert_called_once()

    def test_create_control_buttons_functionality(self):
        """Test control buttons creation."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.show_per_core = False

                mock_parent = Mock()
                mock_button = Mock()

                with patch("tkinter.Button", return_value=mock_button):
                    app._create_control_buttons(mock_parent)

                    # Should have created buttons and stored references
                    assert app.pause_button == mock_button
                    assert app.view_button == mock_button
                    # Button.grid should be called for each button
                    assert mock_button.grid.call_count == 4

    def test_create_ui_components_integration(self):
        """Test the complete UI component creation flow."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)

                # Mock all the sub-methods
                app._create_canvas = Mock()
                app._create_status_label = Mock()
                app._create_control_buttons = Mock()

                # Mock canvas attribute needed by ChartRenderer
                app.canvas = Mock()

                # Mock Frame and ChartRenderer
                mock_frame = Mock()
                mock_renderer = Mock()

                with patch("tkinter.Frame", return_value=mock_frame), patch(
                    "cpu_monitor.ui.main_window.ChartRenderer",
                    return_value=mock_renderer,
                ):
                    app._create_ui_components()

                    # Should call all sub-methods
                    app._create_canvas.assert_called_once_with(mock_frame)
                    app._create_status_label.assert_called_once_with(mock_frame)
                    app._create_control_buttons.assert_called_once_with(mock_frame)

                    # Should create chart renderer
                    assert app.chart_renderer == mock_renderer

    def test_app_initialization_flow(self):
        """Test the complete app initialization flow without GUI."""
        with patch("cpu_monitor.ui.main_window.CPUReader") as mock_reader_class:
            mock_reader = Mock()
            mock_reader.get_core_count.return_value = 4
            mock_reader_class.return_value = mock_reader

            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)

                # Mock all the initialization methods
                app._setup_window = Mock()
                app._create_ui_components = Mock()
                app._initialize_per_core_data_if_needed = Mock()
                app._start_update_loop = Mock()

                # Call init manually
                CPUGraphApp.__init__(
                    app,
                    interval_ms=1000,
                    history_secs=120,
                    show_per_core=True,
                    max_cores=8,
                )

                # Check initialization
                assert app.interval_ms == 1000
                assert app.show_per_core is True
                assert app.max_cores_display == 8

                # Check that all setup methods were called
                app._setup_window.assert_called_once()
                app._create_ui_components.assert_called_once()
                app._initialize_per_core_data_if_needed.assert_called_once()
                app._start_update_loop.assert_called_once()

    def test_initialize_per_core_data_if_needed_no_action(self):
        """Test _initialize_per_core_data_if_needed when no action is needed."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.show_per_core = False  # Should not initialize
                app.per_core_data = []
                app._initialize_per_core_data = Mock()

                app._initialize_per_core_data_if_needed()

                # Should not call initialization since show_per_core is False
                app._initialize_per_core_data.assert_not_called()

    def test_initialize_per_core_data_if_needed_with_action(self):
        """Test _initialize_per_core_data_if_needed when action is needed."""
        with patch("cpu_monitor.ui.main_window.CPUReader"):
            with patch("tkinter.Tk.__init__", return_value=None):
                app = CPUGraphApp.__new__(CPUGraphApp)
                app.show_per_core = True  # Should initialize
                app.per_core_data = []  # Empty, so needs initialization
                app._initialize_per_core_data = Mock()

                app._initialize_per_core_data_if_needed()

                # Should call initialization since conditions are met
                app._initialize_per_core_data.assert_called_once()
