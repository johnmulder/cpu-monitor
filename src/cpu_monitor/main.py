"""
CPU Monitor - Package Entry Point

Main entry point for the CPU monitoring package.
Provides the main() function used by console scripts.
"""

from .cli import parse_arguments
from .ui import CPUGraphApp


def main() -> int:
    """Main entry point for the CPU monitoring application.

    Parses command line arguments and launches the GUI application.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        config = parse_arguments()
    except SystemExit:
        return 0
    except Exception as e:
        print(f"[ERROR] Argument parsing failed: {e}")
        return 1

    try:
        app = CPUGraphApp(
            interval_ms=config.interval_ms,
            history_secs=config.history_secs,
            show_per_core=config.show_per_core,
            max_cores=config.max_cores_display,
        )
        app.mainloop()
        return 0
    except KeyboardInterrupt:
        print("\n[INFO] Application interrupted by user")
        return 0
    except Exception as e:
        print(f"[ERROR] Application error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
