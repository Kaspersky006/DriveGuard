# Small official Python image: Debian without extra tools
FROM python:3.12-slim

WORKDIR /app

# Install the package and its test dependencies first,
# so Docker can reuse this layer when only data or tests change
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir ".[test]"

COPY main.py ./
COPY data ./data
COPY tests ./tests

# Default: validate the sample file
CMD ["python", "main.py", "data/raw/sample_telemetry.csv"]
