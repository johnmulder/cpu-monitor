"""
CPU monitoring and data collection.

Uses psutil, which is already the runtime dependency for this package.
"""

from .data_models import CPUCoreData


class CPUReaderError(Exception):
    """CPU monitoring failed."""


class CPUReader:
    """CPU utilization reader backed by psutil."""

    def __init__(self) -> None:
        try:
            import psutil
        except ImportError as exc:
            raise CPUReaderError("Install psutil with: pip install psutil") from exc

        self.psutil = psutil
        self.psutil.cpu_percent(interval=None)

    def get_cpu_data(self) -> CPUCoreData:
        """Get overall and per-core CPU utilization."""
        try:
            overall = float(self.psutil.cpu_percent(interval=None))
            per_core = [
                float(x) for x in self.psutil.cpu_percent(interval=None, percpu=True)
            ]
            return CPUCoreData(
                overall=overall,
                per_core=per_core,
                core_count=len(per_core),
            )
        except Exception as exc:
            raise CPUReaderError(f"Failed to get CPU data using psutil: {exc}") from exc

    def get_core_count(self) -> int:
        """Get the number of logical CPU cores."""
        try:
            core_count = self.psutil.cpu_count(logical=True)
            return int(core_count) if core_count is not None else 0
        except Exception as exc:
            raise CPUReaderError(
                f"Failed to get CPU core count using psutil: {exc}"
            ) from exc
