"""NiceGUI proof-of-concept for account management."""

import json
import os
import sys
import datetime as datetime_module
from datetime import timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List

# Add repo root to path for imports BEFORE any app imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests
from nicegui import ui

# Try relative import first (when imported as a module), fall back to absolute import
try:
    from .global_dialogs import setup_budget_bill_edit_dialog
except ImportError:
    from app.ui.global_dialogs import setup_budget_bill_edit_dialog

try:
    from .utils import fetch_budgetbills, parse_date, set_app_settings, format_datetime, format_date
except ImportError:
    from app.ui.utils import fetch_budgetbills, parse_date, set_app_settings, format_datetime, format_date

# Try relative import first (when imported as a module), fall back to absolute import
try:
    from ..models.schemas import FrequencyEnum, PaymentMethod
except ImportError:
    from app.models.schemas import FrequencyEnum, PaymentMethod

API_URL = os.getenv("API_URL", "http://localhost:8000")


def load_settings() -> None:
    """Load application settings from the API."""
    try:
        resp = requests.get(f"{API_URL}/settings/")
        if resp.status_code == 200:
            settings = resp.json()
            # API now returns {key: {value: ..., display_name: ...}}
            settings_dict = {
                "currency_symbol": str(settings.get("currency_symbol", {}).get("value", "$")),
                "decimal_places": int(settings.get("decimal_places", {}).get("value", 2)),
                "number_format": str(settings.get("number_format", {}).get("value", "comma")),
                "show_num_old_budgets": int(settings.get("show_num_old_budgets", {}).get("value", 3)),
                "timezone": str(settings.get("timezone", {}).get("value", "America/New_York"))
            }
            set_app_settings(settings_dict)
    except Exception:
        # Use defaults if API call fails
        pass

def format_currency(amount: float) -> str:
    """Format currency using stored settings."""
    # Import here to avoid circular imports; support both absolute and relative
    try:
        from app.ui.utils import app_settings
    except ImportError:
        from .utils import app_settings
    
    symbol = app_settings["currency_symbol"]
    decimal_places = app_settings["decimal_places"]
    number_format = app_settings["number_format"]
    
    # Format the number
    if number_format == "comma":
        # US format: 1,234.56
        formatted = f"{amount:,.{decimal_places}f}"
    else:
        # European format: 1.234,56
        formatted = f"{amount:,.{decimal_places}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    
    return f"{symbol}{formatted}"


def _handle_error(resp: requests.Response) -> None:
    try:
        detail = resp.json()
    except Exception:
        detail = resp.text
    ui.notify(f"Error {resp.status_code}: {detail}", type="negative")


# Global registry for refresh callbacks - will be populated by build_ui
_refresh_callbacks: List[callable] = []


def register_refresh_callback(callback: callable) -> None:
    """Register a callback to be called when settings are refreshed."""
    _refresh_callbacks.append(callback)


def refresh_all_currency_displays() -> None:
    """Refresh all currency displays after settings change."""
    for callback in _refresh_callbacks:
        try:
            callback()
        except Exception:
            pass


def build_ui() -> None:
    # Load settings at startup
    load_settings()
    
    ui.markdown("## MyBudget")
    ui.markdown("Simple Personal Finance Manager")

    # Store refresh functions in lists so they can be accessed from tabs
    _refresh_dashboard_ref = []
    _refresh_budget_bills_ref = []
    _refresh_transactions_ref = []
    
    # Setup global budget bill edit dialog
    open_budget_bill_edit_dialog_global = setup_budget_bill_edit_dialog(
        ui, requests, API_URL, parse_date, _handle_error,
        _refresh_dashboard_ref, _refresh_budget_bills_ref, _refresh_transactions_ref
    )

    with ui.tabs().classes("w-full") as tabs:
        ui.tab("Dashboard")
        ui.tab("Accounts")
        ui.tab("Bills")
        ui.tab("Budgets")
        ui.tab("Transactions")
        ui.tab("Reports")
        ui.tab("Settings")

    with ui.tab_panels(tabs, value="Dashboard").classes("w-full"):
        # Load tab modules dynamically
        import importlib
        
        def load_tab_module(tab_name, module_name):
            """Load a tab module if it exists, otherwise show error."""
            try:
                module = importlib.import_module(f"app.ui.modules.{module_name}")
                # Call the module's build function if it exists
                if hasattr(module, 'build_' + module_name + '_tab'):
                    with ui.tab_panel(tab_name):
                        getattr(module, 'build_' + module_name + '_tab')(ui, requests, API_URL, _refresh_dashboard_ref, register_refresh_callback, format_currency, datetime_module, timezone, open_budget_bill_edit_dialog_global, _refresh_budget_bills_ref, _refresh_transactions_ref, *getattr(module, '_EXTRA_DEPS', []))
                    return True
                else:
                    with ui.tab_panel(tab_name):
                        ui.label(f"Module {module_name} loaded but no build function found")
                    return False
            except ImportError as e:
                with ui.tab_panel(tab_name):
                    ui.label(f"Tab disabled: module {module_name} not found").classes("text-red-500")
                return False
            except Exception as e:
                with ui.tab_panel(tab_name):
                    ui.label(f"Error loading {module_name}: {str(e)}").classes("text-red-500")
                print(f"Error loading {module_name}: {e}")
                return False
        
        # Load all tabs from modules
        load_tab_module("Dashboard", "dashboard")
        load_tab_module("Accounts", "accounts")
        load_tab_module("Bills", "bills")
        load_tab_module("Budgets", "budgets")
        load_tab_module("Transactions", "transactions")
        load_tab_module("Reports", "reports")
        load_tab_module("Settings", "settings")


@ui.page("/")
def index_page():
    build_ui()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="MyBudget NiceGUI",
        port=int(os.getenv("UI_PORT", "8080")),
        host="0.0.0.0",
    )
