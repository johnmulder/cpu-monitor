<!-- markdownlint-disable MD013 -->

# Audit Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the over-engineering found in the ponytail audit while keeping the CPU monitor working.

**Architecture:** Cut unused layers before rewriting behavior. Keep the app as a small Tkinter program with `argparse`, `psutil`, and focused tests. Each task should leave the repo runnable.

**Tech Stack:** Python, Tkinter, argparse, psutil, pytest, ruff.

---

## File Map

- Modify: `src/cpu_monitor/main.py` for direct imports.
- Modify: `src/cpu_monitor/cli/argument_parser.py` to return `argparse.Namespace` and drop unused size flags.
- Modify: `src/cpu_monitor/ui/main_window.py` to inline UI labels and import core classes directly.
- Modify: `src/cpu_monitor/core/cpu_reader.py` to use `psutil` only.
- Modify: `src/cpu_monitor/core/data_models.py` only if a task inlines/removes an unused property.
- Modify: package `__init__.py` files to remove re-export barrels.
- Modify: `tests/test_cli.py`, `tests/test_core.py`, `tests/test_ui.py`, `tests/test_main.py`, `tests/test_integration.py`.
- Delete: `tests/test_config.py`.
- Delete: `src/cpu_monitor/config/settings.py`.
- Delete: `src/cpu_monitor/config/__init__.py`.
- Delete: `MANIFEST.in`.
- Delete: `.github/copilot-instructions.md`.
- Modify: `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `README.md`.

## Task 1: Remove Export Barrels

**Files:**

- Modify: `src/cpu_monitor/main.py`
- Modify: `src/cpu_monitor/ui/main_window.py`
- Modify: `src/cpu_monitor/__init__.py`
- Modify: `src/cpu_monitor/cli/__init__.py`
- Modify: `src/cpu_monitor/core/__init__.py`
- Modify: `src/cpu_monitor/ui/__init__.py`
- Modify: `tests/test_integration.py`

- [ ] **Step 1: Use direct imports in app code**

Change imports to:

```python
# src/cpu_monitor/main.py
from .cli.argument_parser import parse_arguments
from .ui.main_window import CPUGraphApp
```

```python
# src/cpu_monitor/ui/main_window.py
from ..core.cpu_reader import CPUReader
from ..core.data_models import CPUStatistics
from .chart_renderer import ChartRenderer
from .colors import ChartColors
```

- [ ] **Step 2: Replace package barrels with plain package markers**

Use this content for `src/cpu_monitor/cli/__init__.py`, `src/cpu_monitor/core/__init__.py`, and `src/cpu_monitor/ui/__init__.py`:

```python
"""Package marker."""
```

Use this content for `src/cpu_monitor/__init__.py`:

```python
"""CPU utilization monitor."""

__version__ = "2.0.0"
```

- [ ] **Step 3: Remove import-barrel tests**

Delete `test_package_imports` from `tests/test_integration.py`. Keep tests that execute behavior.

- [ ] **Step 4: Verify**

Run:

```bash
rtk pytest tests/test_integration.py tests/test_main.py -q
```

Expected: all selected tests pass.

## Task 2: Delete Config Layer And Unused Size Flags

**Files:**

- Modify: `src/cpu_monitor/cli/argument_parser.py`
- Modify: `src/cpu_monitor/ui/main_window.py`
- Delete: `src/cpu_monitor/config/settings.py`
- Delete: `src/cpu_monitor/config/__init__.py`
- Delete: `tests/test_config.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_integration.py`

- [ ] **Step 1: Return the parser namespace directly**

In `src/cpu_monitor/cli/argument_parser.py`, remove `AppConfig` and give arguments the names the app already uses:

```python
parser.add_argument(
    "-i",
    "--interval",
    dest="interval_ms",
    type=int,
    default=500,
    metavar="MS",
    help="Update interval in milliseconds",
)
parser.add_argument(
    "-t",
    "--time-window",
    dest="history_secs",
    type=int,
    default=60,
    metavar="SECONDS",
    help="Time window for historical data in seconds",
)
parser.add_argument(
    "--max-cores",
    dest="max_cores_display",
    type=int,
    default=0,
    metavar="N",
    help="Maximum number of cores to display (0 = show all cores)",
)
```

Remove `--width`, `--height`, and `_validate_display_args`.

Make validation read the renamed fields:

```python
def _validate_timing_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.interval_ms < 100:
        parser.error("Update interval must be at least 100ms for responsive UI")
    if args.interval_ms > 10000:
        parser.error("Update interval should not exceed 10 seconds")
    if args.history_secs < 10:
        parser.error("Time window must be at least 10 seconds")
    if args.history_secs > 3600:
        parser.error("Time window should not exceed 1 hour (3600 seconds)")
```

```python
def _validate_core_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.max_cores_display < 0:
        parser.error("Maximum cores must be 0 (all cores) or a positive number")
    if args.max_cores_display > 64:
        parser.error("Maximum cores display limit is 64 for performance reasons")
```

Return `args` after validation.

- [ ] **Step 2: Inline UI constants in `main_window.py`**

Add near imports:

```python
DEFAULT_CANVAS_SIZE = (900, 345)
WINDOW_TITLE = "CPU Utilization Monitor"
INITIAL_STATUS_MESSAGE = "Initializing CPU monitor..."
BUTTON_PAUSE = "Pause"
BUTTON_RESUME = "Resume"
BUTTON_CLEAR = "Clear"
BUTTON_QUIT = "Quit"
BUTTON_PER_CORE = "Per-Core"
BUTTON_OVERALL = "Overall"
```

Replace every `UIConfig.X` usage with the matching constant and remove `from ..config.settings import UIConfig`.

- [ ] **Step 3: Remove config tests and imports**

Delete `tests/test_config.py`.

In `tests/test_cli.py`, remove `AppConfig` imports and `isinstance(config, AppConfig)` assertions. Remove assertions for `canvas_width` and `canvas_height`. Remove `--width` and `--height` from combined argument tests.

In `tests/test_integration.py`, remove `AppConfig` import and `test_config_creation_and_usage`.

- [ ] **Step 4: Verify**

Run:

```bash
rtk pytest tests/test_cli.py tests/test_integration.py tests/test_ui.py::TestCPUGraphApp -q
```

Expected: all selected tests pass.

## Task 3: Make CPUReader Psutil-Only

**Files:**

- Modify: `src/cpu_monitor/core/cpu_reader.py`
- Modify: `src/cpu_monitor/core/data_models.py`
- Modify: `tests/test_core.py`
- Modify: `tests/conftest.py`

- [ ] **Step 1: Replace `CPUReader` fallback logic**

Keep `CPUReaderError`, import `CPUCoreData`, and make `CPUReader` this small:

```python
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
        try:
            per_core = [float(x) for x in self.psutil.cpu_percent(interval=None, percpu=True)]
            return CPUCoreData(
                overall=float(self.psutil.cpu_percent(interval=None)),
                per_core=per_core,
                core_count=len(per_core),
            )
        except Exception as exc:
            raise CPUReaderError(f"Failed to get CPU data using psutil: {exc}") from exc

    def get_core_count(self) -> int:
        try:
            core_count = self.psutil.cpu_count(logical=True)
            return int(core_count) if core_count is not None else 0
        except Exception as exc:
            raise CPUReaderError(f"Failed to get CPU core count using psutil: {exc}") from exc
```

- [ ] **Step 2: Remove unused data-model property**

Delete `CPUCoreData.effective_core_count`; it is only tested, not used by the app.

- [ ] **Step 3: Replace core tests with psutil behavior tests**

In `tests/test_core.py`, remove every `/proc/stat`, `percent()`, and fallback test. Keep:

- `CPUStatistics.format_status_text`
- `CPUCoreData.has_per_core_data`
- `CPUReader` psutil success
- `CPUReader` import failure
- `CPUReader` psutil read failure
- `CPUReader.get_core_count`

Use the existing `mock_psutil` fixture for success paths.

- [ ] **Step 4: Remove proc-stat fixtures**

From `tests/conftest.py`, delete:

- `mock_proc_stat_content`
- `sample_cpu_data`
- `chart_test_data` if unused after Task 4
- `create_mock_path_with_content`
- `create_failing_mock_path`

- [ ] **Step 5: Verify**

Run:

```bash
rtk pytest tests/test_core.py -q
```

Expected: all core tests pass.

## Task 4: Replace Property-Based Padding With Small Examples

**Files:**

- Modify: `tests/test_core.py`
- Modify: `tests/test_ui.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: Remove Hypothesis imports**

Delete these imports from tests:

```python
from hypothesis import given
from hypothesis import strategies as st
```

- [ ] **Step 2: Replace color property test**

Use this in `tests/test_ui.py`:

```python
@pytest.mark.parametrize("core_index", [0, 1, 19, 20, 21, -1])
def test_get_core_color_wraps(core_index):
    color = ChartColors.get_core_color(core_index)
    assert color in ChartColors.CORE_PALETTE
    assert ChartColors.get_core_color(core_index + len(ChartColors.CORE_PALETTE)) == color
```

- [ ] **Step 3: Replace history property test**

Use a parametrized example in `tests/test_ui.py`:

```python
@pytest.mark.parametrize(
    ("history_secs", "interval_ms", "expected"),
    [(60, 500, 120), (10, 1000, 10), (1, 10000, 0)],
)
def test_calculate_history_points_examples(history_secs, interval_ms, expected):
    app = CPUGraphApp.__new__(CPUGraphApp)
    app.interval_ms = interval_ms
    assert app._calculate_history_points(history_secs) == expected
```

- [ ] **Step 4: Delete arithmetic property test**

Delete `test_cpu_percentage_calculation_properties` from `tests/test_core.py`; after Task 3 the app no longer owns that formula.

- [ ] **Step 5: Remove dependency**

Delete this line from `pyproject.toml`:

```toml
"hypothesis>=6.0.0",
```

- [ ] **Step 6: Verify**

Run:

```bash
rtk pytest tests/test_ui.py tests/test_core.py -q
```

Expected: all selected tests pass.

## Task 5: Remove Coverage Gate And Duplicate Formatters

**Files:**

- Modify: `pyproject.toml`
- Modify: `.pre-commit-config.yaml`
- Modify: `.github/workflows/ci.yml`
- Modify: `README.md`

- [ ] **Step 1: Make pytest plain**

In `pyproject.toml`, remove `pytest-cov` from dev dependencies and change pytest options to:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose"
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests"
]
```

Delete `[tool.coverage.run]` and `[tool.coverage.report]`.

- [ ] **Step 2: Remove Black and isort**

Delete these dev dependencies:

```toml
"black>=22.0.0",
"isort>=5.12.0",
```

Delete `[tool.black]`.

Keep Ruff import sorting (`"I"`) and add formatting command docs instead of Black/isort.

- [ ] **Step 3: Update pre-commit**

Remove the `psf/black` and `pycqa/isort` repos from `.pre-commit-config.yaml`.

Add Ruff format beside Ruff check:

```yaml
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.3
    hooks:
      - id: ruff
        description: Run ruff linter
        args: ['--fix', '--exit-non-zero-on-fix']
      - id: ruff-format
        description: Format Python code with ruff
```

- [ ] **Step 4: Update CI**

In `.github/workflows/ci.yml`, change the test command to:

```yaml
    - name: Run tests
      run: pytest
```

Delete the Codecov upload step.

- [ ] **Step 5: Update README commands**

Replace coverage commands with:

```bash
pytest
ruff check src/ tests/
ruff format src/ tests/
```

Remove Black, isort, coverage badge/claims, and Codecov references.

- [ ] **Step 6: Verify**

Run:

```bash
rtk pytest -q
rtk ruff check src tests
rtk ruff format --check src tests
```

Expected: tests pass, Ruff reports no errors, formatting check passes.

## Task 6: Delete Packaging And Assistant Metadata Noise

**Files:**

- Delete: `MANIFEST.in`
- Delete: `.github/copilot-instructions.md`
- Modify: `README.md`

- [ ] **Step 1: Delete stale packaging manifest**

Remove `MANIFEST.in`. The project already uses `pyproject.toml` package discovery and does not have `requirements.txt`.

- [ ] **Step 2: Delete unrelated Copilot instructions**

Remove `.github/copilot-instructions.md`; it describes posts, front matter, and static files that do not exist in this app.

- [ ] **Step 3: Trim README sections**

Keep install, run, options, screenshots, and test commands. Remove long hook tables and troubleshooting that duplicate tool docs.

Remove `--width` and `--height` from usage and command-line options.

- [ ] **Step 4: Verify packaging metadata**

Run:

```bash
rtk python -m build --sdist --wheel
```

Expected: source and wheel distributions build successfully.

## Final Verification

- [ ] Run:

```bash
rtk pytest -q
rtk ruff check src tests
rtk ruff format --check src tests
rtk python -m build --sdist --wheel
```

- [ ] Confirm the app starts:

```bash
rtk python -m cpu_monitor.main --help
```

Expected: help prints without errors and no `--width` or `--height` options appear.

- [ ] Commit in small chunks:

```bash
rtk git add src tests pyproject.toml .pre-commit-config.yaml .github README.md
rtk git commit -m "Remove audit-identified complexity"
```
