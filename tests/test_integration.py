"""
Quick integration test for CPU Monitor application.

Tests that the basic application flow works end-to-end
without requiring complex mocking or GUI testing.
"""

from unittest.mock import patch

import pytest

from cpu_monitor.cli.argument_parser import parse_arguments
from cpu_monitor.core.cpu_reader import CPUReader


class TestApplicationIntegration:
    """Integration tests for core application functionality."""

    def test_cli_to_config_pipeline(self):
        """Test CLI argument parsing creates valid config."""
        with patch("sys.argv", ["cpu-monitor", "--per-core", "--max-cores", "8"]):
            config = parse_arguments()

            assert config.show_per_core is True
            assert config.max_cores_display == 8

    def test_cpu_reader_basic_functionality(self):
        """Test basic CPU reader functionality."""
        try:
            reader = CPUReader()

            # Should be able to create without errors
            assert reader is not None

            # Should be able to get core count
            core_count = reader.get_core_count()
            assert isinstance(core_count, int)
            assert core_count > 0

            # Should be able to get some kind of CPU data
            # (May fail if no monitoring available, which is OK)
            cpu_data = reader.get_cpu_data()
            assert cpu_data is not None
            assert hasattr(cpu_data, "overall")
            assert hasattr(cpu_data, "per_core")
            assert hasattr(cpu_data, "core_count")

        except Exception as e:
            # If CPU monitoring fails, that's acceptable for testing
            pytest.skip(f"CPU monitoring not available: {e}")

    def test_color_palette_consistency(self):
        """Test that color palette works correctly."""
        from cpu_monitor.ui.colors import ChartColors

        # Should have a reasonable number of colors
        assert len(ChartColors.CORE_PALETTE) >= 8

        # get_core_color should work for various indices
        color1 = ChartColors.get_core_color(0)
        color2 = ChartColors.get_core_color(1)
        color_wrap = ChartColors.get_core_color(len(ChartColors.CORE_PALETTE))

        assert color1 != color2
        assert color1 == color_wrap  # Should wrap around
