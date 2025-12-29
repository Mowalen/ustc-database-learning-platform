from datetime import datetime, timezone, timedelta

# Define standard timezone for the application (UTC+8)
# We use a fixed offset of +8 hours.
APP_TIMEZONE = timezone(timedelta(hours=8), name="Asia/Shanghai")

def get_now() -> datetime:
    """Get current time in application timezone."""
    return datetime.now(APP_TIMEZONE)

def to_app_timezone(dt: datetime) -> datetime:
    """Convert a datetime to application timezone."""
    if dt.tzinfo is None:
        # If naive, assume it's already in the target timezone or just attach it
        return dt.replace(tzinfo=APP_TIMEZONE)
    return dt.astimezone(APP_TIMEZONE)
