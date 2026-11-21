"""Ingestion: load a telemetry CSV file into a pandas DataFrame."""

from pathlib import Path

import pandas as pd


def read_telemetry(file_path: str) -> pd.DataFrame:
    """
    Read a telemetry dataset from a CSV file.

    Raises:
        FileNotFoundError: If the telemetry file does not exist.
        ValueError: If the file is completely empty (not even a header line).
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Telemetry file not found: {file_path}")

    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise ValueError(f"Telemetry file is empty: {file_path}")
