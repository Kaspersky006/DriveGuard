import pandas as pd

from src.driveguard.config import REQUIRED_COLUMNS
from src.driveguard.models import ValidationIssue, ValidationReport


def check_required_columns(
    dataframe: pd.DataFrame,
    report: ValidationReport
) -> None:
    """
    Check whether all required telemetry columns are present.
    """

    missing_columns = set(REQUIRED_COLUMNS) - set(dataframe.columns)

    if missing_columns:
        report.passed = False

        report.issues.append(
            ValidationIssue(
                rule="Required Columns",
                severity="High",
                message=f"Missing required columns: {', '.join(sorted(missing_columns))}"
            )
        )


def check_missing_values(
    dataframe: pd.DataFrame,
    report: ValidationReport
) -> None:
    """
    Check every column for missing values.
    """

    missing_values = dataframe.isnull().sum()

    for column, count in missing_values.items():

        if count > 0:
            report.passed = False

            report.issues.append(
                ValidationIssue(
                    rule="Missing Values",
                    severity="Medium",
                    message=f"Column '{column}' contains {count} missing value(s)."
                )
            )


def check_duplicate_rows(
    dataframe: pd.DataFrame,
    report: ValidationReport
) -> None:
    """
    Check for duplicate rows in the dataset.
    """

    duplicate_count = dataframe.duplicated().sum()

    if duplicate_count > 0:
        report.passed = False

        report.issues.append(
            ValidationIssue(
                rule="Duplicate Rows",
                severity="Medium",
                message=f"{duplicate_count} duplicate row(s) detected."
            )
        )


def check_speed_change(
    dataframe: pd.DataFrame,
    report: ValidationReport
) -> None:
    """
    Detect unrealistic speed changes between consecutive telemetry samples.
    """

    if "timestamp" not in dataframe.columns or "speed" not in dataframe.columns:
        return

    for index in range(1, len(dataframe)):
        previous_speed = dataframe.loc[index - 1, "speed"]
        current_speed = dataframe.loc[index, "speed"]

        previous_time = dataframe.loc[index - 1, "timestamp"]
        current_time = dataframe.loc[index, "timestamp"]

        if pd.isna(previous_speed) or pd.isna(current_speed):
            continue

        if pd.isna(previous_time) or pd.isna(current_time):
            continue

        time_difference = current_time - previous_time

        if time_difference <= 0:
            continue

        speed_difference = current_speed - previous_speed

        # Convert km/h to m/s.
        speed_difference_mps = speed_difference / 3.6

        acceleration = speed_difference_mps / time_difference

        if abs(acceleration) > 12:
            report.passed = False

            report.issues.append(
                ValidationIssue(
                    rule="Unrealistic Speed Change",
                    severity="High",
                    message=(
                        f"Speed changed from {previous_speed} km/h "
                        f"to {current_speed} km/h in "
                        f"{time_difference:.2f} second(s), "
                        f"producing an acceleration of "
                        f"{acceleration:.2f} m/s²."
                    )
                )
            )


def check_empty_dataset(
    dataframe: pd.DataFrame,
    report: ValidationReport
) -> None:
    """
    Check whether the dataset contains any telemetry records.
    """

    if dataframe.empty:
        report.passed = False

        report.issues.append(
            ValidationIssue(
                rule="Empty Dataset",
                severity="High",
                message="The dataset contains no telemetry records."
            )
        )


def check_duplicate_timestamps(
    dataframe: pd.DataFrame,
    report: ValidationReport
) -> None:
    """
    Check for duplicate timestamps in the telemetry dataset.
    """

    if "timestamp" not in dataframe.columns:
        return

    duplicate_count = dataframe["timestamp"].duplicated().sum()

    if duplicate_count > 0:
        report.passed = False

        report.issues.append(
            ValidationIssue(
                rule="Duplicate Timestamps",
                severity="High",
                message=f"{duplicate_count} duplicate timestamp(s) detected."
            )
        )


def check_negative_speed(
    dataframe: pd.DataFrame,
    report: ValidationReport
) -> None:
    """
    Check for negative vehicle speed values.
    """

    if "speed" not in dataframe.columns:
        return

    negative_speed_count = (dataframe["speed"] < 0).sum()

    if negative_speed_count > 0:
        report.passed = False

        report.issues.append(
            ValidationIssue(
                rule="Negative Speed",
                severity="High",
                message=f"{negative_speed_count} negative speed value(s) detected."
            )
        )


def check_gps_coordinates(
    dataframe: pd.DataFrame,
    report: ValidationReport
) -> None:
    """
    Check whether GPS latitude and longitude values are within valid ranges.
    """

    if "gps_lat" in dataframe.columns:
        invalid_latitude_count = (
            (dataframe["gps_lat"] < -90) |
            (dataframe["gps_lat"] > 90)
        ).sum()

        if invalid_latitude_count > 0:
            report.passed = False

            report.issues.append(
                ValidationIssue(
                    rule="Invalid GPS Latitude",
                    severity="High",
                    message=(
                        f"{invalid_latitude_count} invalid GPS "
                        f"latitude value(s) detected."
                    )
                )
            )

    if "gps_lon" in dataframe.columns:
        invalid_longitude_count = (
            (dataframe["gps_lon"] < -180) |
            (dataframe["gps_lon"] > 180)
        ).sum()

        if invalid_longitude_count > 0:
            report.passed = False

            report.issues.append(
                ValidationIssue(
                    rule="Invalid GPS Longitude",
                    severity="High",
                    message=(
                        f"{invalid_longitude_count} invalid GPS "
                        f"longitude value(s) detected."
                    )
                )
            )


def check_timestamp_order(
    dataframe: pd.DataFrame,
    report: ValidationReport
) -> None:
    """
    Check whether telemetry timestamps are in chronological order.
    """

    if "timestamp" not in dataframe.columns:
        return

    timestamps = dataframe["timestamp"]

    for index in range(1, len(timestamps)):
        previous_time = timestamps.iloc[index - 1]
        current_time = timestamps.iloc[index]

        if pd.isna(previous_time) or pd.isna(current_time):
            continue

        if current_time < previous_time:
            report.passed = False

            report.issues.append(
                ValidationIssue(
                    rule="Timestamp Order",
                    severity="High",
                    message=(
                        f"Timestamp moved backwards from "
                        f"{previous_time} to {current_time}."
                    )
                )
            )


def validate(dataframe: pd.DataFrame) -> ValidationReport:
    report = ValidationReport()

    check_required_columns(dataframe, report)
    check_missing_values(dataframe, report)
    check_duplicate_rows(dataframe, report)
    check_speed_change(dataframe, report)
    check_duplicate_timestamps(dataframe, report)
    check_empty_dataset(dataframe, report)
    check_negative_speed(dataframe, report)
    check_gps_coordinates(dataframe, report)
    check_timestamp_order(dataframe, report)

    return report