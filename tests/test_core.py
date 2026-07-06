"""Tests for CPU monitoring core logic and data structures."""

from unittest.mock import Mock, patch

import pytest

from cpu_monitor.core.cpu_reader import CPUReader, CPUReaderError
from cpu_monitor.core.data_models import CPUCoreData, CPUStatistics


class TestCPUStatistics:
    """CPUStatistics tests."""

    def test_creation_with_valid_data(self):
        """Test valid data creation."""
        stats = CPUStatistics(current=45.2, average=40.1, maximum=75.5)

        assert stats.current == 45.2
        assert stats.average == 40.1
        assert stats.maximum == 75.5

    def test_format_status_text(self):
        """Test the format_status_text method."""
        stats = CPUStatistics(current=42.7, average=38.2, maximum=89.1)
        formatted = stats.format_status_text("12:34:56")

        assert "12:34:56" in formatted
        assert "42.7%" in formatted
        assert "38.2%" in formatted
        assert "89.1%" in formatted
        assert "Current:" in formatted
        assert "Avg:" in formatted
        assert "Max:" in formatted


class TestCPUCoreData:
    """CPUCoreData tests."""

    def test_has_per_core_data_property(self):
        """Test the has_per_core_data computed property."""
        with_data = CPUCoreData(overall=50.0, per_core=[25.0, 75.0], core_count=2)
        assert with_data.has_per_core_data is True

        without_data = CPUCoreData(overall=50.0, per_core=[], core_count=0)
        assert without_data.has_per_core_data is False


class TestCPUReader:
    """CPUReader tests."""

    @patch("builtins.__import__")
    def test_get_cpu_data_with_psutil(self, mock_import, mock_psutil):
        """Test get_cpu_data when psutil is available."""
        mock_import.return_value = mock_psutil

        reader = CPUReader()
        data = reader.get_cpu_data()

        assert isinstance(data, CPUCoreData)
        assert data.overall == 45.0
        assert data.per_core == [25.0, 35.0, 55.0, 65.0]
        assert data.core_count == 4
        assert data.has_per_core_data is True

    def test_psutil_import_failure(self):
        """Test behavior when psutil is not available."""
        real_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == "psutil":
                raise ImportError("No module named psutil")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            with pytest.raises(CPUReaderError, match="Install psutil"):
                CPUReader()

    @patch("builtins.__import__")
    def test_get_cpu_data_wraps_psutil_errors(self, mock_import):
        """Test psutil exception handling."""
        mock_psutil = Mock()
        mock_psutil.cpu_percent.side_effect = [None, Exception("psutil error")]
        mock_import.return_value = mock_psutil

        reader = CPUReader()

        with pytest.raises(CPUReaderError, match="Failed to get CPU data"):
            reader.get_cpu_data()

    @patch("builtins.__import__")
    def test_get_core_count(self, mock_import, mock_psutil):
        """Test get_core_count delegates to psutil."""
        mock_import.return_value = mock_psutil

        reader = CPUReader()

        assert reader.get_core_count() == 4
        mock_psutil.cpu_count.assert_called_once_with(logical=True)

    @patch("builtins.__import__")
    def test_get_core_count_unknown(self, mock_import):
        """Test get_core_count returns 0 when psutil cannot determine a count."""
        mock_psutil = Mock()
        mock_psutil.cpu_percent.return_value = None
        mock_psutil.cpu_count.return_value = None
        mock_import.return_value = mock_psutil

        reader = CPUReader()

        assert reader.get_core_count() == 0

    @patch("builtins.__import__")
    def test_get_core_count_wraps_psutil_errors(self, mock_import):
        """Test get_core_count exception handling."""
        mock_psutil = Mock()
        mock_psutil.cpu_percent.return_value = None
        mock_psutil.cpu_count.side_effect = Exception("psutil error")
        mock_import.return_value = mock_psutil

        reader = CPUReader()

        with pytest.raises(CPUReaderError, match="Failed to get CPU core count"):
            reader.get_core_count()

    def test_cpu_reader_error_exception(self):
        """Test CPUReaderError exception behavior."""
        error = CPUReaderError("Test error message")

        assert str(error) == "Test error message"
        assert isinstance(error, Exception)


class TestCPUReaderIntegration:
    """Integration tests for CPU monitoring functionality."""

    def test_real_cpu_data_collection(self):
        """Test actual CPU data collection."""
        try:
            reader = CPUReader()
            stats = reader.get_cpu_data()

            assert isinstance(stats, CPUCoreData)
            assert 0.0 <= stats.overall <= 100.0
            assert stats.core_count > 0

            if stats.has_per_core_data:
                assert len(stats.per_core) == stats.core_count
                assert all(0.0 <= core <= 100.0 for core in stats.per_core)

        except CPUReaderError:
            pytest.skip("CPU monitoring not available in test environment")

    def test_multiple_readings_stability(self):
        """Test that multiple CPU readings are stable."""
        try:
            reader = CPUReader()
            readings = [reader.get_cpu_data() for _ in range(3)]

            core_counts = [stats.core_count for stats in readings]
            assert len(set(core_counts)) == 1

            for stats in readings:
                assert 0.0 <= stats.overall <= 100.0
                if stats.has_per_core_data:
                    assert all(0.0 <= core <= 100.0 for core in stats.per_core)

        except CPUReaderError:
            pytest.skip("CPU monitoring not available in test environment")
