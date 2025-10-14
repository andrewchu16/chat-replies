from datetime import datetime, timezone


def get_utc_now() -> datetime:
    """Get the current UTC time."""
    return datetime.now(timezone.utc)