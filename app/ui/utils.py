"""Shared Utility Functions for UI Modules

This module provides centralized utility functions used across all UI modules:
- API fetch operations (accounts, bills, categories, transactions)
- Error handling and message formatting
- Response validation
- Date parsing utilities

All functions use the centralized API_URL configuration and provide
consistent error handling for UI components.
"""

import sys
import datetime
from typing import Any, Dict, List
from pathlib import Path
from datetime import timezone

# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests
from app.config import API_URL

# Try to import timezone utilities
try:
    from ..utils import to_app_tz
except ImportError:
    from app.utils import to_app_tz

try:
    from ..models.schemas import PaymentMethod
except ImportError:
    from app.models.schemas import PaymentMethod


def get_payment_method_label(payment_method: str) -> str:
    """Convert payment method enum value to human-readable display label.
    
    Args:
        payment_method: Payment method enum value (e.g., 'manual', 'automatic')
    
    Returns:
        Display label (e.g., 'Manual', 'Automatic')
    """
    payment_method_map = {
        PaymentMethod.MANUAL.value: "Manual",
        PaymentMethod.AUTOMATIC.value: "Automatic",
        PaymentMethod.TRANSFER.value: "Transfer",
        PaymentMethod.OTHER.value: "Other",
    }
    return payment_method_map.get(payment_method, "Manual")


def parse_date(value: Any) -> datetime.datetime | None:
    """Parse a date value into a datetime object.
    
    Handles multiple input formats:
    - datetime objects (returned as-is)
    - ISO format strings with or without 'Z' suffix
    - None or invalid values (returns None)
    
    Args:
        value: Date value to parse (datetime, str, or None)
    
    Returns:
        Parsed datetime object or None if parsing fails
    
    Example:
        >>> parse_date("2024-01-15T10:30:00Z")
        datetime.datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
    """
    if isinstance(value, datetime.datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None
    return None


def handle_error(resp: requests.Response) -> str:
    """Extract and format error message from API response.
    
    Attempts to parse JSON error details, falls back to raw text if JSON parsing fails.
    
    Args:
        resp: HTTP response object from requests library
    
    Returns:
        Formatted error string with status code and details, suitable for UI display
    
    Example:
        >>> resp = requests.get(url)
        >>> if resp.status_code != 200:
        >>>     ui.notify(handle_error(resp), type="negative")
    """
    try:
        detail = resp.json()
    except Exception:
        detail = resp.text
    return f"API Error {resp.status_code}: {detail}"


def fetch_accounts() -> List[Dict[str, Any]]:
    """Fetch all accounts from the API.
    
    Returns:
        List of account dictionaries with fields: id, name, account_type, 
        balance, description, enabled. Returns empty list if fetch fails.
    """
    resp = requests.get(f"{API_URL}/accounts/")
    if resp.status_code != 200:
        return []
    return resp.json()


def fetch_bills() -> List[Dict[str, Any]]:
    """Fetch all bills from the API.
    
    Returns:
        List of bill dictionaries with fields: id, name, budgeted_amount,
        description, frequency, payment_method, account_id, category_id.
        Returns empty list if fetch fails.
    """
    resp = requests.get(f"{API_URL}/bills/")
    if resp.status_code != 200:
        return []
    return resp.json()


def fetch_categories() -> List[Dict[str, Any]]:
    """Fetch all expense categories from the API.
    
    Returns:
        List of category dictionaries with fields: id, name, description.
        Returns empty list if fetch fails.
    """
    resp = requests.get(f"{API_URL}/categories/")
    if resp.status_code != 200:
        return []
    return resp.json()


def fetch_transactions() -> List[Dict[str, Any]]:
    """Fetch all transactions from the API.
    
    Returns:
        List of transaction dictionaries with fields: id, transaction_type,
        amount, occurred_at, note, account_id, bill_id, budget_bill_id.
        Returns empty list if fetch fails.
    """
    resp = requests.get(f"{API_URL}/transactions/")
    if resp.status_code != 200:
        return []
    return resp.json()


def fetch_budgetbills() -> List[Dict[str, Any]]:
    """Fetch all budget bills across all budgets from the API.
    
    Returns:
        List of budget bill dictionaries with fields: id, budget_id, bill_id,
        budgeted_amount, due_date, paid_amount, paid_on, note.
        Returns empty list if fetch fails.
    """
    resp = requests.get(f"{API_URL}/budgets/")
    if resp.status_code != 200:
        return []
    budgets = resp.json()
    budgetbills = []
    for budget in budgets:
        budget_id = budget.get("id")
        resp = requests.get(f"{API_URL}/budgets/{budget_id}/bills")
        if resp.status_code == 200:
            budgetbills.extend(resp.json())
    return budgetbills


# Global app settings - will be populated from API
app_settings = {
    "currency_symbol": "$",
    "decimal_places": 2,
    "number_format": "comma",
    "show_num_old_budgets": 3,
    "timezone": "America/New_York",
}


def set_app_settings(settings: Dict[str, Any]) -> None:
    """Update global app settings from API.
    
    Args:
        settings: Dictionary of settings to update
    """
    global app_settings
    app_settings.update(settings)


def format_datetime(dt: datetime.datetime, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Format datetime using app's configured timezone.
    
    Args:
        dt: datetime object (can be naive or timezone-aware)
        fmt: strftime format string (default: "%Y-%m-%d %H:%M")
    
    Returns:
        Formatted datetime string in app's timezone
    """
    if dt is None:
        return "N/A"
    
    try:
        tz_name = app_settings.get("timezone", "America/New_York")
        dt_tz = to_app_tz(dt, tz_name)
        return dt_tz.strftime(fmt)
    except Exception:
        # Fallback to basic formatting if timezone conversion fails
        return dt.strftime(fmt) if dt else "N/A"


def format_date(dt: datetime.datetime, fmt: str = "%Y-%m-%d") -> str:
    """Format date using app's configured timezone.
    
    Args:
        dt: datetime object (can be naive or timezone-aware)
        fmt: strftime format string (default: "%Y-%m-%d")
    
    Returns:
        Formatted date string in app's timezone
    """
    return format_datetime(dt, fmt)
