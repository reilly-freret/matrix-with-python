from datetime import datetime, timezone


def mins_in_future(d: datetime) -> str:
    # Convert input string to datetime object
    input_datetime = datetime.fromisoformat(d)

    # Get the current datetime
    current_datetime = datetime.now(timezone.utc)

    # Calculate the time difference
    time_difference = input_datetime - current_datetime

    # Extract minutes from the time difference
    minutes_in_future = time_difference.total_seconds() / 60

    return minutes_in_future
