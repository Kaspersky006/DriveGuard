from pathlib import Path

import pandas as pd


def read_telemetry(file_path: str) -> pd.DataFrame:
    """
    Read a telemetry dataset from a CSV file.

    Args:
        file_path: Path to the telemetry CSV file.

    Returns:
        A pandas DataFrame containing the telemetry data.

    Raises:
        FileNotFoundError: If the telemetry file does not exist.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Telemetry file not found: {file_path}"
        )

    dataframe = pd.read_csv(path)

    return dataframe