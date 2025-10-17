"""Tests for main entry point and CLI integration."""

import sys
from unittest.mock import Mock, patch

from cpu_monitor.main import main


class TestMainFunction:
    """Main entry point tests."""

    @patch("cpu_monitor.main.parse_arguments")
    @patch("cpu_monitor.main.CPUGraphApp")
    def test_successful_execution(self, mock_app_class, mock_parse):
        """Test successful app execution."""
        mock_config = Mock()
        mock_config.interval_ms = 1000
        mock_config.history_secs = 60
        mock_config.show_per_core = False
        mock_config.max_cores_display = 0
        mock_parse.return_value = mock_config

        mock_app = Mock()
        mock_app_class.return_value = mock_app

        # Execute
        result = main()

        assert result == 0
        mock_parse.assert_called_once()
        mock_app_class.assert_called_once_with(
            interval_ms=1000,
            history_secs=60,
            show_per_core=False,
            max_cores=0,
        )
        mock_app.mainloop.assert_called_once()

    @patch("cpu_monitor.main.parse_arguments")
    def test_argument_parsing_system_exit(self, mock_parse):
        """Test SystemExit handling (--help, etc.)."""
        mock_parse.side_effect = SystemExit(0)

        result = main()

        assert result == 0

    @patch("cpu_monitor.main.parse_arguments")
    def test_argument_parsing_exception(self, mock_parse):
        """Test argument parsing errors."""
        mock_parse.side_effect = ValueError("Invalid argument")

        with patch("builtins.print") as mock_print:
            result = main()

        assert result == 1
        mock_print.assert_called_with(
            "[ERROR] Argument parsing failed: Invalid argument"
        )

    @patch("cpu_monitor.main.parse_arguments")
    @patch("cpu_monitor.main.CPUGraphApp")
    def test_keyboard_interrupt(self, mock_app_class, mock_parse):
        """Test Ctrl+C handling."""
        mock_config = Mock()
        mock_config.interval_ms = 1000
        mock_config.history_secs = 60
        mock_config.show_per_core = True
        mock_config.max_cores_display = 4
        mock_parse.return_value = mock_config

        mock_app = Mock()
        mock_app.mainloop.side_effect = KeyboardInterrupt()
        mock_app_class.return_value = mock_app

        with patch("builtins.print") as mock_print:
            result = main()

        assert result == 0
        mock_print.assert_called_with("\n[INFO] Application interrupted by user")

    @patch("cpu_monitor.main.parse_arguments")
    @patch("cpu_monitor.main.CPUGraphApp")
    def test_application_exception(self, mock_app_class, mock_parse):
        """Test unexpected application errors."""
        mock_config = Mock()
        mock_config.interval_ms = 500
        mock_config.history_secs = 120
        mock_config.show_per_core = False
        mock_config.max_cores_display = 8
        mock_parse.return_value = mock_config

        mock_app = Mock()
        mock_app.mainloop.side_effect = RuntimeError("GUI initialization failed")
        mock_app_class.return_value = mock_app

        with patch("builtins.print") as mock_print, patch(
            "traceback.print_exc"
        ) as mock_traceback:
            result = main()

        assert result == 1
        mock_print.assert_called_with(
            "[ERROR] Application error: GUI initialization failed"
        )
        mock_traceback.assert_called_once()

    def test_main_module_execution_concept(self):
        """Test main module structure."""
        assert hasattr(sys, "exit")
        from cpu_monitor.main import main

        assert callable(main)
