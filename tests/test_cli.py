"""Tests for CLI argument parsing and validation."""

from unittest.mock import patch

import pytest

from cpu_monitor.cli.argument_parser import parse_arguments
from cpu_monitor.config.settings import AppConfig


class TestArgumentParsing:
    """Argument parsing tests."""

    def test_default_values(self):
        """Test default values."""
        with patch("sys.argv", ["cpu-monitor"]):
            config = parse_arguments()

        assert isinstance(config, AppConfig)
        assert config.interval_ms == 500  # Default
        assert config.history_secs == 60  # Default
        assert config.canvas_width == 900  # Default
        assert config.canvas_height == 345  # Default
        assert config.show_per_core is False  # Default
        assert config.max_cores_display == 0  # Default

    def test_custom_interval(self):
        """Test custom interval values."""
        with patch("sys.argv", ["cpu-monitor", "--interval", "250"]):
            config = parse_arguments()
            assert config.interval_ms == 250

    def test_per_core_flag(self):
        """Test per-core flag."""
        with patch("sys.argv", ["cpu-monitor", "--per-core"]):
            config = parse_arguments()
            assert config.show_per_core is True

        with patch("sys.argv", ["cpu-monitor"]):
            config = parse_arguments()
            assert config.show_per_core is False

    def test_max_cores_setting(self):
        """Test max cores setting."""
        with patch("sys.argv", ["cpu-monitor", "--max-cores", "8"]):
            config = parse_arguments()
            assert config.max_cores_display == 8

    def test_combined_arguments(self):
        """Test multiple arguments."""
        args = [
            "cpu-monitor",
            "--interval",
            "250",
            "--time-window",
            "180",
            "--width",
            "1200",
            "--height",
            "600",
            "--per-core",
            "--max-cores",
            "8",
        ]

        with patch("sys.argv", args):
            config = parse_arguments()

            assert config.interval_ms == 250
            assert config.history_secs == 180
            assert config.canvas_width == 1200
            assert config.canvas_height == 600
            assert config.show_per_core is True
            assert config.max_cores_display == 8


class TestCLIIntegration:
    """CLI integration tests."""

    def test_realistic_usage_scenarios(self):
        """Test realistic usage scenarios."""
        with patch("sys.argv", ["cpu-monitor"]):
            config = parse_arguments()
            assert config.interval_ms == 500
            assert config.show_per_core is False

        with patch("sys.argv", ["cpu-monitor", "--per-core", "-i", "250"]):
            config = parse_arguments()
            assert config.interval_ms == 250
            assert config.show_per_core is True


class TestArgumentValidation:
    """Argument validation tests."""

    def test_invalid_values(self) -> None:
        """Test error handling for out-of-range values."""
        with patch("sys.argv", ["cpu-monitor", "-i", "50"]), pytest.raises(SystemExit):
            parse_arguments()

        with patch("sys.argv", ["cpu-monitor", "-i", "11000"]), pytest.raises(
            SystemExit
        ):
            parse_arguments()

        with patch("sys.argv", ["cpu-monitor", "-t", "-1"]), pytest.raises(SystemExit):
            parse_arguments()

        with patch("sys.argv", ["cpu-monitor", "-t", "0"]), pytest.raises(SystemExit):
            parse_arguments()

        with patch("sys.argv", ["cpu-monitor", "-t", "3700"]), pytest.raises(
            SystemExit
        ):
            parse_arguments()

        with patch("sys.argv", ["cpu-monitor", "--width", "0"]), pytest.raises(
            SystemExit
        ):
            parse_arguments()

        with patch("sys.argv", ["cpu-monitor", "--height", "150"]), pytest.raises(
            SystemExit
        ):
            parse_arguments()

        with patch("sys.argv", ["cpu-monitor", "--max-cores", "-1"]), pytest.raises(
            SystemExit
        ):
            parse_arguments()

        with patch("sys.argv", ["cpu-monitor", "--max-cores", "999"]), pytest.raises(
            SystemExit
        ):
            parse_arguments()
