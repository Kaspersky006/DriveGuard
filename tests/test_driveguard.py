"""15 tests for DriveGuard: correct, incomplete, faulty and edge-case data."""

import pandas as pd
import pytest

from driveguard.config import MAX_SPEED
from driveguard.reader import read_telemetry
from driveguard.reporter import format_report
from driveguard.validator import validate

SAMPLE_FILE = "data/raw/sample_telemetry.csv"


def clean_data() -> pd.DataFrame:
    """Three valid telemetry samples. Each test changes one thing."""
    return pd.DataFrame({
        "timestamp": [0.0, 0.1, 0.2],
        "speed": [0, 2, 4],
        "steering_angle": [0, 1, 2],
        "brake_pressure": [0, 0, 0],
        "acceleration_x": [0.0, 0.3, 0.4],
        "acceleration_y": [0.0, 0.0, 0.1],
        "yaw_rate": [0.0, 0.01, 0.02],
        "gps_lat": [48.765, 48.7651, 48.7652],
        "gps_lon": [11.423, 11.4231, 11.4232],
    })


def rules(report) -> list[str]:
    """The names of all rules that failed."""
    return [issue.rule for issue in report.issues]


# --- Correct data ------------------------------------------------------------

def test_clean_data_passes():
    report = validate(clean_data())
    assert report.passed is True
    assert report.issues == []


def test_reader_loads_sample_file():
    dataframe = read_telemetry(SAMPLE_FILE)
    assert len(dataframe) == 6
    assert "speed" in dataframe.columns


# --- Incomplete data ---------------------------------------------------------

def test_missing_required_column_is_detected():
    report = validate(clean_data().drop(columns=["speed"]))
    assert report.passed is False
    assert "Required Columns" in rules(report)


def test_missing_value_is_detected():
    data = clean_data()
    data.loc[1, "gps_lat"] = None
    report = validate(data)
    assert "Missing Values" in rules(report)


def test_header_only_file_is_reported_as_empty(tmp_path):
    file = tmp_path / "header_only.csv"
    file.write_text(",".join(clean_data().columns) + "\n")
    report = validate(read_telemetry(str(file)))
    assert "Empty Dataset" in rules(report)


def test_reader_raises_error_for_missing_file():
    with pytest.raises(FileNotFoundError):
        read_telemetry("does_not_exist.csv")


# --- Faulty data -------------------------------------------------------------

def test_negative_speed_is_detected():
    data = clean_data()
    data.loc[2, "speed"] = -5
    assert "Negative Speed" in rules(validate(data))


def test_speed_above_maximum_is_detected():
    data = clean_data()
    data["speed"] = [MAX_SPEED + 10] * 3    # constant speed, so only the range is wrong
    assert "Maximum Speed" in rules(validate(data))


def test_invalid_gps_latitude_is_detected():
    data = clean_data()
    data.loc[0, "gps_lat"] = 95.0
    assert "Invalid GPS" in rules(validate(data))


def test_unrealistic_speed_change_is_detected():
    data = clean_data()
    data.loc[2, "speed"] = 100            # 2 -> 100 km/h in 0.1 s
    assert "Unrealistic Speed Change" in rules(validate(data))


def test_timestamp_moving_backwards_is_detected():
    data = clean_data()
    data.loc[2, "timestamp"] = 0.05
    assert "Timestamp Order" in rules(validate(data))


def test_non_numeric_value_is_detected():
    data = clean_data().astype({"speed": object})
    data.loc[1, "speed"] = "fast"
    assert "Numeric Data Type" in rules(validate(data))


# --- Edge cases --------------------------------------------------------------

def test_speed_exactly_at_maximum_is_valid():
    data = clean_data()
    data["speed"] = [MAX_SPEED] * 3       # the limit itself is still allowed
    assert validate(data).passed is True


def test_sample_file_contains_known_problems():
    report = validate(read_telemetry(SAMPLE_FILE))
    assert report.passed is False
    assert "Duplicate Rows" in rules(report)
    assert "Timestamp Order" in rules(report)


def test_report_text_lists_every_issue():
    data = clean_data()
    data.loc[0, "gps_lat"] = 95.0
    data.loc[2, "speed"] = -5
    report = validate(data)
    text = format_report(report)
    assert text.startswith("Validation FAILED")
    assert len(text.splitlines()) == len(report.issues) + 1
