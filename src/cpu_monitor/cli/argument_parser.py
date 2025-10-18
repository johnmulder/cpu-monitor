"""
Command line argument parsing and validation.

Provides CLI interface for configuring the CPU monitoring application.
"""

import argparse

from ..config.settings import AppConfig


def parse_arguments() -> AppConfig:
    """Parse command line arguments and return validated configuration.

    Returns:
        AppConfig: Validated configuration object

    Raises:
        SystemExit: If arguments are invalid or help is requested
    """
    parser = argparse.ArgumentParser(
        description="Real-time CPU utilization monitor with interactive display",
        epilog="Examples:\n"
        "  %(prog)s --per-core                    # Show all CPU cores\n"
        "  %(prog)s --max-cores 4 --per-core     # Show first 4 cores\n"
        "  %(prog)s -i 250 -t 120                # Fast updates, long history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=500,
        metavar="MS",
        help="Update interval in milliseconds",
    )

    parser.add_argument(
        "-t",
        "--time-window",
        type=int,
        default=60,
        metavar="SECONDS",
        help="Time window for historical data in seconds",
    )

    parser.add_argument(
        "-w",
        "--width",
        type=int,
        default=900,
        metavar="PIXELS",
        help="Canvas width in pixels",
    )

    parser.add_argument(
        "--height",
        type=int,
        default=345,
        metavar="PIXELS",
        help="Canvas height in pixels",
    )

    parser.add_argument(
        "--per-core",
        action="store_true",
        help="Start in per-core view mode (can be toggled during runtime)",
    )

    parser.add_argument(
        "--max-cores",
        type=int,
        default=0,
        metavar="N",
        help="Maximum number of cores to display (0 = show all cores)",
    )

    args = parser.parse_args()

    _validate_arguments(parser, args)

    return AppConfig(
        interval_ms=args.interval,
        history_secs=args.time_window,
        canvas_width=args.width,
        canvas_height=args.height,
        show_per_core=args.per_core,
        max_cores_display=args.max_cores,
    )


def _validate_arguments(
    parser: argparse.ArgumentParser, args: argparse.Namespace
) -> None:
    """Validate parsed arguments and show helpful error messages.

    Args:
        parser: The argument parser (for error reporting)
        args: Parsed arguments

    Raises:
        SystemExit: If validation fails
    """
    if args.interval < 100:
        parser.error("Update interval must be at least 100ms for responsive UI")
    if args.interval > 10000:
        parser.error("Update interval should not exceed 10 seconds")

    if args.time_window < 10:
        parser.error("Time window must be at least 10 seconds")
    if args.time_window > 3600:
        parser.error("Time window should not exceed 1 hour (3600 seconds)")

    if args.width < 400:
        parser.error("Canvas width must be at least 400 pixels")
    if args.height < 200:
        parser.error("Canvas height must be at least 200 pixels")

    if args.max_cores < 0:
        parser.error("Maximum cores must be 0 (all cores) or a positive number")
    if args.max_cores > 64:
        parser.error("Maximum cores display limit is 64 for performance reasons")
