"""
Data models and structures for CPU monitoring.

Contains data classes and containers for organizing CPU usage information.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class CPUStatistics:
    """Container for aggregated CPU usage statistics.

    Holds current, average, and maximum CPU usage values with formatting methods.
    """

    current: float
    average: float
    maximum: float

    def format_status_text(self, timestamp: str) -> str:
        """Format statistics into a human-readable status string."""
        return (
            f"{timestamp}  |  "
            f"Current: {self.current:5.1f}%   "
            f"Avg: {self.average:5.1f}%   "
            f"Max: {self.maximum:5.1f}%"
        )


@dataclass
class CPUCoreData:
    """Container for multi-core CPU usage data.

    Encapsulates overall system usage and per-core usage data with utility methods.
    """

    overall: float
    per_core: List[float]
    core_count: int

    @property
    def has_per_core_data(self) -> bool:
        """Check if valid per-core data is available."""
        return bool(self.per_core) and self.core_count > 0

    @property
    def effective_core_count(self) -> int:
        """Get the actual number of cores with data."""
        return len(self.per_core) if self.per_core else 0
