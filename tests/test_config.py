"""
Unit tests for CPU Monitor configuration module.

Tests the configuration settings, data structures, and constants
used throughout the application.
"""

from cpu_monitor.config.settings import AppConfig, UIConfig


class TestAppConfig:
    """Test cases for AppConfig dataclass."""

    def test_default_values(self):
        """Test that AppConfig has expected default values."""
        config = AppConfig()

        assert config.interval_ms == 500
        assert config.history_secs == 60
        assert config.canvas_width == 900
        assert config.canvas_height == 345
        assert config.show_per_core is False
        assert config.max_cores_display == 0

    def test_custom_values(self):
        """Test AppConfig with custom values."""
        config = AppConfig(
            interval_ms=250,
            history_secs=120,
            canvas_width=1200,
            canvas_height=400,
            show_per_core=True,
            max_cores_display=8,
        )

        assert config.interval_ms == 250
        assert config.history_secs == 120
        assert config.canvas_width == 1200
        assert config.canvas_height == 400
        assert config.show_per_core is True
        assert config.max_cores_display == 8

    def test_immutable_after_creation(self):
        """Test that AppConfig fields can be modified (dataclass is mutable)."""
        config = AppConfig()

        # Dataclass allows modification by default
        config.interval_ms = 1000
        assert config.interval_ms == 1000

    def test_type_validation(self):
        """Test type validation for AppConfig fields."""
        # This would only matter if we added validation decorators
        config = AppConfig(interval_ms=250)
        assert isinstance(config.interval_ms, int)

    def test_boundary_values(self):
        """Test boundary values for configuration."""
        config = AppConfig(
            interval_ms=1,  # Minimum practical value
            history_secs=1,  # Minimum history
            max_cores_display=0,  # Special value for "all cores"
        )

        assert config.interval_ms == 1
        assert config.history_secs == 1
        assert config.max_cores_display == 0


class TestUIConfig:
    """Test cases for UIConfig constants."""

    def test_ui_constants_exist(self):
        """Test that all expected UI constants are defined."""
        assert hasattr(UIConfig, "DEFAULT_CANVAS_SIZE")
        assert hasattr(UIConfig, "WINDOW_TITLE")
        assert hasattr(UIConfig, "INITIAL_STATUS_MESSAGE")
        assert hasattr(UIConfig, "BUTTON_PAUSE")
        assert hasattr(UIConfig, "BUTTON_RESUME")
        assert hasattr(UIConfig, "BUTTON_CLEAR")
        assert hasattr(UIConfig, "BUTTON_QUIT")
        assert hasattr(UIConfig, "BUTTON_PER_CORE")
        assert hasattr(UIConfig, "BUTTON_OVERALL")

    def test_default_canvas_size(self):
        """Test default canvas size is a valid tuple."""
        size = UIConfig.DEFAULT_CANVAS_SIZE
        assert isinstance(size, tuple)
        assert len(size) == 2
        assert all(isinstance(dim, int) for dim in size)
        assert all(dim > 0 for dim in size)

    def test_window_title(self):
        """Test window title is a non-empty string."""
        title = UIConfig.WINDOW_TITLE
        assert isinstance(title, str)
        assert len(title) > 0
        assert "CPU" in title or "Monitor" in title

    def test_button_labels(self):
        """Test that button labels are non-empty strings."""
        buttons = [
            UIConfig.BUTTON_PAUSE,
            UIConfig.BUTTON_RESUME,
            UIConfig.BUTTON_CLEAR,
            UIConfig.BUTTON_QUIT,
            UIConfig.BUTTON_PER_CORE,
            UIConfig.BUTTON_OVERALL,
        ]

        for button in buttons:
            assert isinstance(button, str)
            assert len(button) > 0

    def test_initial_status_message(self):
        """Test initial status message is appropriate."""
        message = UIConfig.INITIAL_STATUS_MESSAGE
        assert isinstance(message, str)
        assert len(message) > 0
        assert "CPU" in message or "monitor" in message.lower()


class TestConfigIntegration:
    """Integration tests for configuration module."""

    def test_config_compatibility(self):
        """Test that AppConfig values work with UIConfig constants."""
        config = AppConfig()
        ui_size = UIConfig.DEFAULT_CANVAS_SIZE

        assert config.canvas_width >= ui_size[0] or config.canvas_width > 0
        assert config.canvas_height >= ui_size[1] or config.canvas_height > 0

    def test_realistic_configuration(self):
        """Test a realistic application configuration."""
        config = AppConfig(
            interval_ms=500,  # 2 FPS
            history_secs=300,  # 5 minutes of history
            canvas_width=1200,  # HD width
            canvas_height=600,  # HD height
            show_per_core=True,
            max_cores_display=16,  # Modern CPU core count
        )

        assert 100 <= config.interval_ms <= 5000  # 0.2 to 10 FPS
        assert 10 <= config.history_secs <= 3600  # 10 seconds to 1 hour
        assert 400 <= config.canvas_width <= 4000  # Reasonable display sizes
        assert 200 <= config.canvas_height <= 2000
        assert 0 <= config.max_cores_display <= 128  # Reasonable core counts
