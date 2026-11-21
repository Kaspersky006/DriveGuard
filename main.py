"""Command-line entry point: python main.py <telemetry.csv>"""

import argparse
import sys

from driveguard.reader import read_telemetry
from driveguard.reporter import format_report
from driveguard.validator import validate


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a telemetry CSV file.")
    parser.add_argument(
        "file_path",
        nargs="?",
        default="data/raw/sample_telemetry.csv",
        help="Path to the telemetry CSV file",
    )
    args = parser.parse_args()

    dataframe = read_telemetry(args.file_path)
    report = validate(dataframe)
    print(format_report(report))

    # Exit code 0 = data is clean, 1 = problems found (useful in CI pipelines).
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
