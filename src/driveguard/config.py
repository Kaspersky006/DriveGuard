"""Configuration: which columns are required and which value ranges are valid."""

REQUIRED_COLUMNS = [
    "timestamp",
    "speed",
    "steering_angle",
    "brake_pressure",
    "acceleration_x",
    "acceleration_y",
    "yaw_rate",
    "gps_lat",
    "gps_lon",
]

# Every telemetry column must contain numbers.
NUMERIC_COLUMNS = REQUIRED_COLUMNS

MAX_SPEED = 300                  # km/h
MAX_STEERING_ANGLE = 720         # degrees, in both directions
MAX_ACCELERATION = 20            # m/s², in both directions
MAX_SPEED_CHANGE_ACCELERATION = 12  # m/s², computed from two speed samples
