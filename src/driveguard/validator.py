import pandas as pd

from src.driveguard.config import REQUIRED_COLUMNS
from src.driveguard.models import ValidationIssue, ValidationReport


def check_required_columns(
    dataframe: pd.DataFrame,
    report: ValidationReport
) -> None:
    """
    Check whether all required telemetry columns exist.
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
    Check for missing values in each column.
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


def validate(dataframe: pd.DataFrame) -> ValidationReport:
    """
    Run all validation rules and return one validation report.
    """

    report = ValidationReport()

    check_required_columns(dataframe, report)
    check_missing_values(dataframe, report)

    return report
