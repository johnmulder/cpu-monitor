"""
Shared test fixtures and utilities for CPU Monitor tests.

Reduces repetition across test modules by providing common mock setups and test data.
"""

from typing import Any, Dict, List
from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_psutil():
    """Mock psutil module with default CPU data."""
    mock = Mock()
    mock.cpu_percent.side_effect = [
        None,  # Prime call
        45.0,  # Overall usage
        [25.0, 35.0, 55.0, 65.0],  # Per-core usage
    ]
    mock.cpu_count.return_value = 4
    return mock


@pytest.fixture
def mock_proc_stat_content():
    """Standard /proc/stat content for testing."""
    return """cpu  123456 0 78901 987654 0 0 0 0 0 0
cpu0 30864 0 19725 246913 0 0 0 0 0 0
cpu1 30864 0 19725 246913 0 0 0 0 0 0
cpu2 30864 0 19725 246913 0 0 0 0 0 0
cpu3 30864 0 19725 246913 0 0 0 0 0 0
"""


@pytest.fixture
def sample_cpu_data() -> Dict[str, Any]:
    """Sample CPU data for testing."""
    return {
        "overall": 45.2,
        "per_core": [25.0, 35.0, 55.0, 65.0],
        "core_count": 4,
    }


@pytest.fixture
def chart_test_data() -> Dict[str, List[float]]:
    """Test data for chart rendering."""
    return {
        "overall_data": [25.0, 30.0, 35.0, 40.0, 45.0],
        "per_core_data": [
            [20.0, 25.0, 30.0, 35.0, 40.0],  # Core 0
            [30.0, 35.0, 40.0, 45.0, 50.0],  # Core 1
            [15.0, 20.0, 25.0, 30.0, 35.0],  # Core 2
            [35.0, 40.0, 45.0, 50.0, 55.0],  # Core 3
        ],
    }


def create_mock_path_with_content(content: str) -> Mock:
    """Create a mock Path object that returns specific content."""
    mock_path_instance = Mock()
    mock_path_instance.read_text.return_value = content
    return mock_path_instance


def create_failing_mock_path(error: Exception) -> Mock:
    """Create a mock Path object that raises an exception."""
    mock_path_instance = Mock()
    mock_path_instance.read_text.side_effect = error
    return mock_path_instance
