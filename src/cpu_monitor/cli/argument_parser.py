"""
Command line argument parsing and validation.

Provides CLI interface for configuring the CPU monitoring application.
"""

import argparse


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments and return validated configuration.

    Returns:
        argparse.Namespace: Validated configuration values

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
        "--per-core",
        dest="show_per_core",
        action="store_true",
        help="Start in per-core view mode (can be toggled during runtime)",
    )

    parser.add_argument(
        "--max-cores",
        dest="max_cores_display",
        type=int,
        default=0,
        metavar="N",
        help="Maximum number of cores to display (0 = show all cores)",
    )

    args = parser.parse_args()

    _validate_arguments(parser, args)
    return args


def _validate_timing_args(
    parser: argparse.ArgumentParser, args: argparse.Namespace
) -> None:
    """Validate timing-related arguments.

    Args:
        parser: The argument parser (for error reporting)
        args: Parsed arguments

    Raises:
        SystemExit: If validation fails
    """
    if args.interval_ms < 100:
        parser.error("Update interval must be at least 100ms for responsive UI")
    if args.interval_ms > 10000:
        parser.error("Update interval should not exceed 10 seconds")

    if args.history_secs < 10:
        parser.error("Time window must be at least 10 seconds")
    if args.history_secs > 3600:
        parser.error("Time window should not exceed 1 hour (3600 seconds)")


def _validate_core_args(
    parser: argparse.ArgumentParser, args: argparse.Namespace
) -> None:
    """Validate core-related arguments.

    Args:
        parser: The argument parser (for error reporting)
        args: Parsed arguments

    Raises:
        SystemExit: If validation fails
    """
    if args.max_cores_display < 0:
        parser.error("Maximum cores must be 0 (all cores) or a positive number")
    if args.max_cores_display > 64:
        parser.error("Maximum cores display limit is 64 for performance reasons")


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
    _validate_timing_args(parser, args)
    _validate_core_args(parser, args)
