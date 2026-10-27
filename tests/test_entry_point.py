"""Process-level exit status checks for the supported entry points."""

import subprocess
import sys
import sysconfig
from pathlib import Path

import pytest


@pytest.mark.parametrize("entry_point", ["module", "console"])
@pytest.mark.parametrize(
    ("arguments", "expected", "diagnostic"),
    [
        (["--interval", "1"], 2, "Update interval must be at least 100ms"),
        (["--unknown-option"], 2, "unrecognized arguments"),
        (["--help"], 0, "usage:"),
    ],
)
def test_entry_point_exit_status(entry_point, arguments, expected, diagnostic):
    """Usage errors fail while help succeeds without opening the GUI."""
    if entry_point == "module":
        command = [sys.executable, "-m", "cpu_monitor.main"]
    else:
        name = "cpu-monitor.exe" if sys.platform == "win32" else "cpu-monitor"
        command = [str(Path(sysconfig.get_path("scripts")) / name)]

    result = subprocess.run(
        command + arguments,
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )

    assert result.returncode == expected
    output = result.stdout if expected == 0 else result.stderr
    assert diagnostic in output
    assert "Traceback" not in result.stderr
    if expected == 0:
        assert result.stderr == ""
