"""Validation: run every quality check on a telemetry DataFrame."""

import pandas as pd

from driveguard.config import (
    MAX_ACCELERATION,
    MAX_SPEED,
    MAX_SPEED_CHANGE_ACCELERATION,
    MAX_STEERING_ANGLE,
    NUMERIC_COLUMNS,
    REQUIRED_COLUMNS,
)
from driveguard.reporter import ValidationReport


def _numeric(dataframe: pd.DataFrame, column: str) -> pd.Series:
    """Return a column as numbers. Text that is not a number becomes NaN."""
    return pd.to_numeric(dataframe[column], errors="coerce")


# --- Incomplete data -------------------------------------------------------

def check_empty_dataset(dataframe: pd.DataFrame, report: ValidationReport) -> None:
    """The file has a header but no data rows."""
    if dataframe.empty:
        report.add_issue("Empty Dataset", "High", "The dataset contains no telemetry records.")


def check_required_columns(dataframe: pd.DataFrame, report: ValidationReport) -> None:
    """Every column from REQUIRED_COLUMNS must exist."""
    missing = set(REQUIRED_COLUMNS) - set(dataframe.columns)
    if missing:
        report.add_issue(
            "Required Columns", "High",
            f"Missing required columns: {', '.join(sorted(missing))}",
        )


def check_missing_values(dataframe: pd.DataFrame, report: ValidationReport) -> None:
    """No cell may be empty."""
    for column, count in dataframe.isnull().sum().items():
        if count > 0:
            report.add_issue(
                "Missing Values", "Medium",
                f"Column '{column}' contains {count} missing value(s).",
            )


# --- Faulty data -----------------------------------------------------------

def check_numeric_columns(dataframe: pd.DataFrame, report: ValidationReport) -> None:
    """Telemetry columns must contain numbers, not text like 'abc'."""
    for column in NUMERIC_COLUMNS:
        if column not in dataframe.columns:
            continue
        converted = _numeric(dataframe, column)
        invalid = (converted.isna() & dataframe[column].notna()).sum()
        if invalid > 0:
            report.add_issue(
                "Numeric Data Type", "High",
                f"Column '{column}' contains {invalid} non-numeric value(s).",
            )


def check_duplicate_rows(dataframe: pd.DataFrame, report: ValidationReport) -> None:
    """The same row must not appear twice."""
    count = dataframe.duplicated().sum()
    if count > 0:
        report.add_issue("Duplicate Rows", "Medium", f"{count} duplicate row(s) detected.")


def check_duplicate_timestamps(dataframe: pd.DataFrame, report: ValidationReport) -> None:
    """Two samples must not have the same time."""
    if "timestamp" not in dataframe.columns:
        return
    count = dataframe["timestamp"].duplicated().sum()
    if count > 0:
        report.add_issue("Duplicate Timestamps", "High", f"{count} duplicate timestamp(s) detected.")


def check_timestamp_order(dataframe: pd.DataFrame, report: ValidationReport) -> None:
    """Time must never go backwards."""
    if "timestamp" not in dataframe.columns:
        return
    backwards = (_numeric(dataframe, "timestamp").diff() < 0).sum()
    if backwards > 0:
        report.add_issue("Timestamp Order", "High", f"Timestamp moved backwards {backwards} time(s).")


def check_speed_range(dataframe: pd.DataFrame, report: ValidationReport) -> None:
    """Speed must be between 0 and MAX_SPEED km/h."""
    if "speed" not in dataframe.columns:
        return
    speed = _numeric(dataframe, "speed")

    negative = (speed < 0).sum()
    if negative > 0:
        report.add_issue("Negative Speed", "High", f"{negative} negative speed value(s) detected.")

    too_fast = (speed > MAX_SPEED).sum()
    if too_fast > 0:
        report.add_issue("Maximum Speed", "High", f"{too_fast} speed value(s) exceeded {MAX_SPEED} km/h.")


def check_speed_change(dataframe: pd.DataFrame, report: ValidationReport) -> None:
    """Speed must not change faster than a real car can accelerate or brake."""
    if "timestamp" not in dataframe.columns or "speed" not in dataframe.columns:
        return

    speed_change_mps = _numeric(dataframe, "speed").diff() / 3.6   # km/h -> m/s
    time_change_s = _numeric(dataframe, "timestamp").diff()

    valid = time_change_s > 0          # skip duplicate or backwards timestamps
    acceleration = speed_change_mps[valid] / time_change_s[valid]

    count = (acceleration.abs() > MAX_SPEED_CHANGE_ACCELERATION).sum()
    if count > 0:
        report.add_issue(
            "Unrealistic Speed Change", "High",
            f"{count} speed change(s) faster than {MAX_SPEED_CHANGE_ACCELERATION} m/s².",
        )


def check_steering_angle(dataframe: pd.DataFrame, report: ValidationReport) -> None:
    """Steering angle must stay within ±MAX_STEERING_ANGLE degrees."""
    if "steering_angle" not in dataframe.columns:
        return
    count = (_numeric(dataframe, "steering_angle").abs() > MAX_STEERING_ANGLE).sum()
    if count > 0:
        report.add_issue(
            "Steering Angle Range", "High",
            f"{count} steering angle value(s) exceeded ±{MAX_STEERING_ANGLE} degrees.",
        )


def check_acceleration_range(dataframe: pd.DataFrame, report: ValidationReport) -> None:
    """Measured acceleration must stay within ±MAX_ACCELERATION m/s²."""
    for column in ["acceleration_x", "acceleration_y"]:
        if column not in dataframe.columns:
            continue
        count = (_numeric(dataframe, column).abs() > MAX_ACCELERATION).sum()
        if count > 0:
            report.add_issue(
                "Acceleration Range", "High",
                f"{count} value(s) in '{column}' exceeded ±{MAX_ACCELERATION} m/s².",
            )


def check_gps_coordinates(dataframe: pd.DataFrame, report: ValidationReport) -> None:
    """Latitude must be within ±90, longitude within ±180 degrees."""
    for column, limit in [("gps_lat", 90), ("gps_lon", 180)]:
        if column not in dataframe.columns:
            continue
        count = (_numeric(dataframe, column).abs() > limit).sum()
        if count > 0:
            report.add_issue("Invalid GPS", "High", f"{count} invalid value(s) in '{column}'.")


# --- Run everything ----------------------------------------------------------

CHECKS = [
    check_empty_dataset,
    check_required_columns,
    check_missing_values,
    check_numeric_columns,
    check_duplicate_rows,
    check_duplicate_timestamps,
    check_timestamp_order,
    check_speed_range,
    check_speed_change,
    check_steering_angle,
    check_acceleration_range,
    check_gps_coordinates,
]


def validate(dataframe: pd.DataFrame) -> ValidationReport:
    """Run all checks and collect every issue in one report."""
    report = ValidationReport()
    for check in CHECKS:
        check(dataframe, report)
    return report
