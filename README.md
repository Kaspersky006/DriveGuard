# DriveGuard

A Python toolkit that checks vehicle telemetry data before it is used for analysis.
It finds missing columns, missing values and invalid readings and produces a structured validation report.

## Structure (4 modules)

| Module | Role |
|---|---|
| `src/driveguard/reader.py` | **Ingestion**: loads the CSV file |
| `src/driveguard/config.py` | **Configuration**: required columns and valid value ranges |
| `src/driveguard/validator.py` | **Validation**: 12 checks on the data |
| `src/driveguard/reporter.py` | **Reporting**: `ValidationIssue` and `ValidationReport`, plus text output |

## Run locally

```bash
pip install -e ".[test]"
python main.py data/raw/sample_telemetry.csv
pytest
```

The program exits with code `0` if the data is clean and `1` if problems were found, so it can stop a CI pipeline.

## Run with Docker

```bash
docker build -t driveguard .
docker run --rm driveguard                     # validate the sample file
docker run --rm driveguard python -m pytest    # run the 15 tests inside the container
```

## Tests

15 pytest tests cover correct data, incomplete data (missing columns, missing values, empty file),
faulty data (negative speed, impossible speed changes, invalid GPS, wrong types) and edge cases
(values exactly at the limit, the report output).
