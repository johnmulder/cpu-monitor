"""
CPU monitoring and data collection system.

Provides cross-platform CPU usage monitoring with automatic fallback
from psutil to Linux /proc/stat.
"""

import sys
from pathlib import Path
from typing import List, Optional, Tuple

from .data_models import CPUCoreData


class CPUReaderError(Exception):
    """Custom exception for CPU monitoring errors."""


class CPUReader:
    """Cross-platform CPU utilization reader.

    Automatically selects the best available method for CPU monitoring:
    - psutil (preferred, cross-platform)
    - /proc/stat (Linux fallback)
    """

    PROC_STAT_PATH = "/proc/stat"
    CPU_FIELDS_MIN_COUNT = 4  # Minimum fields needed from /proc/stat

    def __init__(self) -> None:
        """Initialize the CPU reader with the best available method."""
        self._use_psutil = False
        self._previous_idle: Optional[int] = None
        self._previous_total: Optional[int] = None

        self._initialize_cpu_reader()

    def _initialize_cpu_reader(self) -> None:
        """Set up CPU monitoring using the best available method."""
        if self._try_initialize_psutil():
            return

        if self._is_linux_system():
            self._initialize_proc_stat_fallback()
        else:
            raise CPUReaderError(
                "psutil not available and /proc/stat fallback only works on Linux. "
                "Install psutil with: pip install psutil"
            )

    def _try_initialize_psutil(self) -> bool:
        """Attempt to initialize psutil monitoring."""
        try:
            import psutil

            self.psutil = psutil
            # Prime psutil's non-blocking sampler
            self.psutil.cpu_percent(interval=None)
            self._use_psutil = True
            return True
        except (ImportError, ModuleNotFoundError):
            return False

    def _is_linux_system(self) -> bool:
        """Check if running on a Linux system."""
        return sys.platform.startswith("linux")

    def _initialize_proc_stat_fallback(self) -> None:
        """Initialize Linux /proc/stat fallback monitoring."""
        try:
            self._prime_proc_stat()
        except Exception as e:
            raise CPUReaderError(f"Failed to initialize /proc/stat reader: {e}") from e

    def percent(self) -> float:
        """Get current overall CPU utilization percentage."""
        return (
            self._get_psutil_percent()
            if self._use_psutil
            else self._get_proc_stat_percent()
        )

    def get_cpu_data(self) -> CPUCoreData:
        """Get comprehensive CPU data including per-core information."""
        if self._use_psutil:
            return self._get_psutil_cpu_data()
        # Fallback only provides overall stats
        overall = self._get_proc_stat_percent()
        return CPUCoreData(overall=overall, per_core=[], core_count=0)

    def get_core_count(self) -> int:
        """Get the number of logical CPU cores."""
        if self._use_psutil:
            core_count = self.psutil.cpu_count(logical=True)
            return int(core_count) if core_count is not None else 0
        else:
            return self._count_cores_from_proc_stat()

    def _get_psutil_percent(self) -> float:
        """Get CPU percentage using psutil (non-blocking)."""
        try:
            return float(self.psutil.cpu_percent(interval=None))
        except Exception as e:
            raise CPUReaderError(
                f"Failed to get CPU percentage using psutil: {e}"
            ) from e

    def _get_psutil_cpu_data(self) -> CPUCoreData:
        """Get comprehensive CPU data using psutil."""
        try:
            # Get overall and per-core CPU usage
            overall = float(self.psutil.cpu_percent(interval=None))
            per_core = [
                float(x) for x in self.psutil.cpu_percent(interval=None, percpu=True)
            ]

            return CPUCoreData(
                overall=overall, per_core=per_core, core_count=len(per_core)
            )
        except Exception as e:
            raise CPUReaderError(f"Failed to get CPU data using psutil: {e}") from e

    def _safe_read_proc_stat(self) -> str:
        """Safely read /proc/stat with consistent error handling."""
        try:
            proc_stat_path = Path(self.PROC_STAT_PATH)
            return proc_stat_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            raise CPUReaderError(f"Failed to read {self.PROC_STAT_PATH}: {e}") from e

    def _count_cores_from_proc_stat(self) -> int:
        """Count CPU cores from /proc/stat (Linux only)."""
        try:
            lines = self._safe_read_proc_stat().splitlines()
            return sum(
                1 for line in lines if line.startswith("cpu") and line[3:4].isdigit()
            )
        except CPUReaderError:
            return 0  # Unknown

    def _read_proc_stat(self) -> Tuple[int, int]:
        """Read CPU statistics from /proc/stat. Returns (idle, total) times."""
        content = self._safe_read_proc_stat()
        first_line = content.splitlines()[0]

        if not first_line.startswith("cpu "):
            raise CPUReaderError(
                f"Unexpected {self.PROC_STAT_PATH} format: {first_line[:20]}..."
            )

        cpu_times = self._parse_cpu_times(first_line)
        return self._calculate_idle_and_total(cpu_times)

    def _parse_cpu_times(self, cpu_line: str) -> List[int]:
        """Parse CPU time values from /proc/stat line."""
        parts = cpu_line.split()
        if len(parts) < self.CPU_FIELDS_MIN_COUNT + 1:  # +1 for 'cpu' label
            raise CPUReaderError(f"Insufficient CPU fields in {self.PROC_STAT_PATH}")

        try:
            return [int(part) for part in parts[1:]]
        except ValueError as e:
            raise CPUReaderError(f"Invalid CPU time values: {e}") from e

    def _calculate_idle_and_total(self, cpu_times: List[int]) -> Tuple[int, int]:
        """Calculate idle and total CPU times from parsed values."""
        idle = cpu_times[3] + (cpu_times[4] if len(cpu_times) >= 5 else 0)
        total = sum(cpu_times)
        return idle, total

    def _prime_proc_stat(self) -> None:
        """Initialize the /proc/stat reader with baseline values."""
        idle, total = self._read_proc_stat()
        self._previous_idle, self._previous_total = idle, total

    def _get_proc_stat_percent(self) -> float:
        """Get CPU percentage using /proc/stat fallback."""
        current_idle, current_total = self._read_proc_stat()

        if self._previous_idle is None or self._previous_total is None:
            self._previous_idle, self._previous_total = current_idle, current_total
            return 0.0

        idle_delta = current_idle - self._previous_idle
        total_delta = current_total - self._previous_total

        self._previous_idle, self._previous_total = current_idle, current_total

        if total_delta <= 0:
            return 0.0

        usage_ratio = 1.0 - (idle_delta / total_delta)
        usage_percent = usage_ratio * 100.0

        return max(0.0, min(100.0, usage_percent))
