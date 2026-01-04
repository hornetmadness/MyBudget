"""Utility functions for timezone management and datetime operations."""

from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from typing import Optional


def get_app_timezone(tz_name: str = "UTC") -> ZoneInfo:
    """Get a ZoneInfo timezone object from a timezone name string.
    
    Args:
        tz_name: IANA timezone name (e.g., "UTC", "America/New_York", "Europe/London")
                If invalid, defaults to UTC
    
    Returns:
        ZoneInfo object for the specified timezone
    """
    try:
        return ZoneInfo(tz_name)
    except Exception:
        # Invalid timezone, fall back to UTC
        return ZoneInfo("UTC")


def now_in_app_tz(tz_name: str = "UTC") -> datetime:
    """Get current time in the app's configured timezone.
    
    Args:
        tz_name: IANA timezone name
    
    Returns:
        datetime object in the specified timezone
    """
    app_tz = get_app_timezone(tz_name)
    return datetime.now(app_tz)


def utc_now() -> datetime:
    """Get current time in UTC (for internal storage)."""
    return datetime.now(timezone.utc)


def to_app_tz(dt: datetime, tz_name: str = "UTC") -> datetime:
    """Convert a datetime to the app's configured timezone.
    
    Args:
        dt: datetime object (can be naive or timezone-aware)
        tz_name: IANA timezone name
    
    Returns:
        datetime in the specified timezone
    """
    if dt is None:
        return None
    
    app_tz = get_app_timezone(tz_name)
    
    # If naive, assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Convert to app timezone
    return dt.astimezone(app_tz)


def to_utc(dt: datetime) -> datetime:
    """Convert a datetime to UTC (for storage).
    
    Args:
        dt: datetime object (can be naive or timezone-aware)
    
    Returns:
        datetime in UTC
    """
    if dt is None:
        return None
    
    # If naive, assume UTC
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    
    # Convert to UTC
    return dt.astimezone(timezone.utc)
