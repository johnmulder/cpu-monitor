"""
Shared test fixtures and utilities for CPU Monitor tests.

Reduces repetition across test modules by providing common mock setups and test data.
"""

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
