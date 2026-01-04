"""Settings Module - Application Configuration UI

This module provides application settings and configuration including:
- Currency format preferences
- Category management (create, edit, delete)
- Database backup and restore
- Application metadata display
- User preferences
"""

import sys
import json
from typing import Any, Dict, List
from pathlib import Path

# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import requests
from app.config import API_URL, settings
from app.ui.utils import fetch_accounts, fetch_bills, fetch_categories, parse_date, app_settings


def build_settings_tab(ui, requests, API_URL, _refresh_dashboard_ref, register_refresh_callback, format_currency, datetime, timezone, open_budget_bill_edit_dialog_global, _refresh_budget_bills_ref, _refresh_transactions_ref, *args) -> None:
    """Build the complete settings tab UI with configuration options.
    
    Creates:
        - Application settings sub-tab with currency preferences
        - Category management with CRUD operations
        - Database backup/restore functionality
        - About section with version information
    
    Args:
        ui: NiceGUI ui instance
        requests: HTTP requests module
        API_URL: Base API URL for backend calls
        _refresh_dashboard_ref: Reference to dashboard refresh callback
        register_refresh_callback: Function to register refresh callbacks
        format_currency: Currency formatting utility function
        datetime: Datetime module
        timezone: Timezone module
        open_budget_bill_edit_dialog_global: Global dialog opener for budget bills
        *args: Additional arguments passed by dynamic module loader
    """
    ui.label("Settings").classes("text-2xl font-bold mb-4")

    # Create sub-tabs for Settings
    with ui.tabs().classes("w-full") as settings_tabs:
        ui.tab("Application Settings")
        ui.tab("Backup")
        ui.tab("Categories")
        ui.tab("Help")

    with ui.tab_panels(settings_tabs, value="Application Settings").classes("w-full"):
        # Application Settings sub-tab
        with ui.tab_panel("Application Settings"):
            with ui.card().classes("w-full max-w-2xl"):
                ui.label("Application Settings").classes("text-lg font-semibold mb-4")

                # Currency symbol setting
                with ui.row().classes("items-center justify-between w-full mb-4"):
                    currency_label = ui.label("").classes("text-base")
                    currency_select = ui.select(
                        options={"$": "USD ($)", "EUR": "EUR (€)", "GBP": "GBP (£)"},
                        value="$",
                        label="Currency"
                    ).classes("w-48")

                ui.separator()

                # Decimal places setting
                with ui.row().classes("items-center justify-between w-full mb-4"):
                    decimal_label = ui.label("").classes("text-base")
                    decimal_select = ui.select(
                        options={"2": "2 decimal places", "3": "3 decimal places"},
                        value="2",
                        label="Decimals"
                    ).classes("w-48")

                ui.separator()

                # Number format setting
                with ui.row().classes("items-center justify-between w-full mb-4"):
                    number_format_label = ui.label("").classes("text-base")
                    number_format = ui.select(
                        options={"comma": "1,234.56", "period": "1.234,56"},
                        value="comma",
                        label="Format"
                    ).classes("w-48")

                ui.separator()

                # Timezone setting
                with ui.row().classes("items-center justify-between w-full mb-4"):
                    timezone_label = ui.label("Timezone").classes("text-base")
                    timezone_select = ui.select(
                        options={
                            "UTC": "UTC",
                            "America/New_York": "America/New_York",
                            "America/Chicago": "America/Chicago",
                            "America/Denver": "America/Denver",
                            "America/Los_Angeles": "America/Los_Angeles",
                            "Europe/London": "Europe/London",
                            "Europe/Paris": "Europe/Paris",
                            "Europe/Berlin": "Europe/Berlin",
                            "Asia/Tokyo": "Asia/Tokyo",
                            "Asia/Shanghai": "Asia/Shanghai",
                            "Asia/Hong_Kong": "Asia/Hong_Kong",
                            "Asia/Singapore": "Asia/Singapore",
                            "Australia/Sydney": "Australia/Sydney",
                        },
                        value="UTC",
                        label="Timezone"
                    ).classes("w-48")

                ui.separator()

                # Pruning Settings
                ui.label("Data Management").classes("text-lg font-semibold mt-6 mb-4")

                with ui.row().classes("items-center justify-between w-full mb-4"):
                    prune_budgets_label = ui.label("").classes("text-base")
                    prune_budgets_input = ui.number(
                        label="Months",
                        value=24,
                        min=1,
                        max=120,
                        step=1,
                    ).classes("w-48")

                # Prune budgets section
                with ui.row().classes("items-center gap-4 mt-4"):
                    prune_status_label = ui.label("").classes("text-sm text-gray-600")

                    def check_prune_status():
                        """Check how many budgets would be pruned."""
                        resp = requests.get(f"{API_URL}/budgets/prune/list")
                        if resp.status_code == 200:
                            budgets = resp.json()
                            count = len(budgets)
                            if count > 0:
                                prune_status_label.text = f"{count} old budget(s) ready to prune"
                            else:
                                prune_status_label.text = "No old budgets to prune"
                        else:
                            prune_status_label.text = "Error checking budgets"

                    def perform_prune():
                        """Perform the actual pruning with confirmation."""
                        def confirm_prune():
                            resp = requests.post(f"{API_URL}/budgets/prune")
                            if resp.status_code == 200:
                                result = resp.json()
                                ui.notify(f"Pruned {result.get('count', 0)} budgets", type="positive")
                                check_prune_status()
                                prune_dialog.close()
                            else:
                                ui.notify("Failed to prune budgets", type="negative")

                        # Create confirmation dialog
                        prune_dialog = ui.dialog()
                        with prune_dialog, ui.card().classes("w-full max-w-md"):
                            ui.label("Confirm Budget Pruning").classes("text-lg font-semibold mb-4")
                            ui.label("This will permanently delete (soft delete) budgets older than the configured retention period.").classes("text-sm text-gray-600 mb-4")
                            with ui.row().classes("gap-2 justify-end"):
                                ui.button("Cancel", on_click=prune_dialog.close).props("flat")
                                ui.button("Confirm Prune", color="negative", on_click=confirm_prune)

                        prune_dialog.open()

                    ui.button("Check Prune Status", on_click=check_prune_status).props("flat")
                    ui.button("Prune Old Budgets", color="warning", on_click=perform_prune)

                check_prune_status()  # Initial check on load

                ui.separator()

                # API Settings
                ui.label("API Configuration").classes("text-lg font-semibold mt-6 mb-4")

                with ui.row().classes("items-center justify-between w-full mb-4"):
                    ui.label("API URL").classes("text-base")
                    ui.label(f"{API_URL}").classes("text-sm text-gray-600 font-mono")

                ui.separator()

                # Save settings button
                with ui.row().classes("justify-end gap-2 mt-6"):
                    def save_settings():
                        global app_settings
                        payload = {
                            "currency_symbol": currency_select.value,
                            "decimal_places": int(decimal_select.value),
                            "number_format": number_format.value,
                            "timezone": timezone_select.value,
                            "prune_budgets_after_months": int(prune_budgets_input.value or 24),
                        }
                        resp = requests.patch(f"{API_URL}/settings/", json=payload)
                        if resp.status_code == 200:
                            # Update global settings immediately
                            app_settings["currency_symbol"] = currency_select.value
                            app_settings["decimal_places"] = int(decimal_select.value)
                            app_settings["number_format"] = number_format.value
                            app_settings["timezone"] = timezone_select.value
                            # Refresh all displays
                            refresh_all_currency_displays()
                            ui.notify("Settings saved and applied successfully", type="positive")
                        else:
                            ui.notify("Failed to save settings", type="negative")

                    def load_settings_panel():
                        resp = requests.get(f"{API_URL}/settings/")
                        if resp.status_code == 200:
                            settings_data = resp.json()
                            # Populate values
                            currency_select.value = settings_data.get("currency_symbol", {}).get("value", "$")
                            decimal_select.value = str(settings_data.get("decimal_places", {}).get("value", 2))
                            number_format.value = settings_data.get("number_format", {}).get("value", "comma")
                            timezone_select.value = settings_data.get("timezone", {}).get("value", "UTC")
                            prune_budgets_input.value = settings_data.get("prune_budgets_after_months", {}).get("value", 24)

                            # Populate display names
                            currency_label.text = settings_data.get("currency_symbol", {}).get("display_name", "Currency Symbol")
                            decimal_label.text = settings_data.get("decimal_places", {}).get("display_name", "Decimal Places")
                            number_format_label.text = settings_data.get("number_format", {}).get("display_name", "Number Format")
                            timezone_label.text = settings_data.get("timezone", {}).get("display_name", "Timezone")
                            prune_budgets_label.text = settings_data.get("prune_budgets_after_months", {}).get("display_name", "Prune Budgets After (months)")

                    def reset_settings():
                        global app_settings
                        payload = {
                            "currency_symbol": "$",
                            "decimal_places": 2,
                            "number_format": "comma",
                            "timezone": "America/New_York",
                            "prune_budgets_after_months": 24,
                        }
                        resp = requests.patch(f"{API_URL}/settings/", json=payload)
                        if resp.status_code == 200:
                            # Update global settings immediately
                            app_settings["currency_symbol"] = "$"
                            app_settings["decimal_places"] = 2
                            app_settings["number_format"] = "comma"
                            app_settings["timezone"] = "UTC"
                            # Refresh all displays
                            refresh_all_currency_displays()
                            currency_select.value = "$"
                            decimal_select.value = "2"
                            number_format.value = "comma"
                            timezone_select.value = "UTC"
                            prune_budgets_input.value = 24
                            ui.notify("Settings reset to defaults and applied", type="info")
                        else:
                            ui.notify("Failed to reset settings", type="negative")

                    ui.button("Save Settings", color="primary", on_click=save_settings)
                    ui.button("Reset to Defaults", on_click=reset_settings)

                # Load settings on tab open
                load_settings_panel()

            # About section
            with ui.card().classes("w-full max-w-2xl mt-6"):
                ui.label("About MyBudget").classes("text-lg font-semibold mb-4")
                ui.label(f"Version {settings.APP_VERSION}").classes("text-sm text-gray-600 mb-2")
                ui.label(settings.APP_DESCRIPTION).classes("text-sm text-gray-600")

        # Backup sub-tab
        with ui.tab_panel("Backup"):
            with ui.card().classes("w-full max-w-2xl"):
                ui.label("Database Backup").classes("text-lg font-semibold mb-4")
                ui.label("Download a backup of your application database.").classes("text-sm text-gray-600 mb-6")

                with ui.row().classes("items-center gap-4"):
                    ui.icon("storage").classes("text-4xl text-blue-500")
                    with ui.column():
                        ui.label("MyBudget Database").classes("text-base font-semibold")
                        ui.label("SQLite database file containing all your financial data").classes("text-sm text-gray-600")

                ui.separator().classes("my-6")

                with ui.row().classes("justify-start gap-4 mt-6"):
                    def download_database():
                        try:
                            # Create a download by opening the file URL
                            download_url = f"{API_URL}/settings/backup/download-db"
                            ui.download(src=download_url)
                            ui.notify("Database backup started", type="positive")
                        except Exception as e:
                            ui.notify(f"Failed to download backup: {str(e)}", type="negative")

                    ui.button("Download Database Backup", color="primary", icon="download", on_click=download_database)

                ui.label("The backup file contains all accounts, bills, budgets, and transactions.").classes("text-xs text-gray-500 mt-6")


        # Categories sub-tab
        with ui.tab_panel("Categories"):
            categories_container = ui.column().classes("w-full")

            # Dialog to show bills using a category
            category_usage_dialog = ui.dialog()
            with category_usage_dialog, ui.card().classes("w-full max-w-lg"):
                category_usage_title = ui.label("Category Usage").classes("text-lg font-semibold mb-2")
                category_usage_list = ui.column().classes("w-full gap-2")
                with ui.row().classes("justify-end mt-4"):
                    ui.button("Close", on_click=category_usage_dialog.close)

            def load_categories():
                """Load and display all categories."""
                categories_container.clear()

                try:
                    resp = requests.get(f"{API_URL}/categories/")
                    if resp.status_code != 200:
                        ui.notify("Failed to load categories", type="negative")
                        return

                    categories = resp.json()

                    def open_category_usage(category: Dict[str, Any]):
                        """Show dialog listing active bills using the category."""
                        category_usage_title.text = f"Category: {category.get('name', 'Category Usage')}"
                        category_usage_list.clear()
                        try:
                            bills = fetch_bills()
                        except Exception:
                            bills = []
                        active_bills = [
                            b for b in bills
                            if str(b.get("category_id")) == str(category.get("id"))
                            and not b.get("deleted", False)
                            and b.get("enabled", True)
                        ]
                        with category_usage_list:
                            if not active_bills:
                                ui.label("No active bills are using this category.").classes("text-sm text-gray-600")
                            else:
                                ui.label(f"Active bills using '{category.get('name', '')}':").classes("text-sm text-gray-700 mb-2")
                                for bill in active_bills:
                                    bill_name = bill.get("name", "Bill")
                                    bill_id = bill.get("id")
                                    ui.link(bill_name, f"{API_URL}/bills/{bill_id}").props("target=_blank").classes("text-primary underline")
                        category_usage_dialog.open()

                    with categories_container:
                        ui.label("Bill Categories").classes("text-lg font-semibold mb-4")
                        ui.label(f"Manage {len(categories)} categories").classes("text-sm text-gray-600 mb-6")

                        # Add category form
                        with ui.card().classes("w-full max-w-2xl mb-6"):
                            ui.label("Add New Category").classes("text-base font-semibold mb-4")

                            with ui.row().classes("w-full gap-4"):
                                category_name = ui.input(label="Category Name", placeholder="e.g., Utilities").classes("flex-1")
                                category_desc = ui.input(label="Description", placeholder="Optional description").classes("flex-1")

                            with ui.row().classes("justify-end gap-2 mt-4"):
                                def add_category():
                                    if not category_name.value:
                                        ui.notify("Please enter a category name", type="warning")
                                        return

                                    payload = {
                                        "name": category_name.value,
                                        "description": category_desc.value if category_desc.value else None,
                                    }
                                    resp = requests.post(f"{API_URL}/categories/", json=payload)
                                    if resp.status_code == 201:
                                        ui.notify(f"Category '{category_name.value}' created", type="positive")
                                        category_name.value = ""
                                        category_desc.value = ""
                                        load_categories()
                                    else:
                                        error_msg = resp.json().get("detail", "Failed to create category")
                                        ui.notify(f"Error: {error_msg}", type="negative")

                                ui.button("Add Category", color="primary", on_click=add_category)

                        # Categories list
                        if categories:
                            ui.separator().classes("my-6")
                            ui.label("Existing Categories").classes("text-base font-semibold mb-4")

                            for category in categories:
                                with ui.card().classes("w-full"):
                                    with ui.row().classes("items-center justify-between w-full"):
                                        with ui.column():
                                            category_link = ui.link(category["name"], "#").classes("text-base font-semibold text-primary underline")
                                            category_link.on(
                                                "click",
                                                lambda e, cat=category: open_category_usage(cat),
                                            )
                                            if category.get("description"):
                                                ui.label(category["description"]).classes("text-sm text-gray-600")

                                        with ui.row().classes("gap-2"):
                                            def make_delete_handler(cat_id):
                                                def delete_category():
                                                    resp = requests.delete(f"{API_URL}/categories/{cat_id}")
                                                    if resp.status_code == 200:
                                                        ui.notify("Category deleted", type="positive")
                                                        load_categories()
                                                    else:
                                                        ui.notify("Failed to delete category", type="negative")
                                                return delete_category

                                            ui.button("Delete", color="negative", on_click=make_delete_handler(category["id"])).props("flat")
                        else:
                            ui.label("No categories yet. Create one to get started!").classes("text-sm text-gray-500 italic")

                except Exception as e:
                    ui.notify(f"Error loading categories: {str(e)}", type="negative")

            # Load categories on tab open
            load_categories()

        # Help sub-tab
        with ui.tab_panel("Help"):
            with ui.card().classes("w-full max-w-4xl"):
                ui.label("Help & Documentation").classes("text-lg font-semibold mb-4")

                with ui.row().classes("items-center gap-3 mb-3"):
                    ui.label("Source: API docs").classes("text-sm text-gray-600")
                    doc_choice = ui.select(
                        options={
                            "user": "User Guide (/docs/user)",
                            "developer": "Developer Guide (/docs/developer)",
                            "list": "Available Docs (/docs/list)",
                            "redoc": "API Docs (/redoc)",
                            "swagger": "Swagger (/docs)",
                        },
                        value="user",
                        label="View"
                    ).classes("w-72")
                    reload_btn = ui.button("Reload", icon="refresh")

                doc_container = ui.html("<div class='text-sm text-gray-600'>Loading documentation…</div>").classes("w-full h-[70vh] overflow-auto bg-white border border-gray-200 rounded")

                def load_docs():
                    try:
                        choice = doc_choice.value or "user"
                        endpoint = {
                            "user": "docs/user",
                            "developer": "docs/developer",
                            "list": "docs/list",
                            "redoc": "redoc",
                            "swagger": "docs",
                        }.get(choice, "docs/user")
                        resp = requests.get(f"{API_URL}/{endpoint}")
                        if resp.status_code == 200:
                            content_type = resp.headers.get("content-type", "")
                            if "application/json" in content_type:
                                try:
                                    payload = resp.json()
                                    doc_container.content = f"<pre class='text-xs whitespace-pre-wrap'>{json.dumps(payload, indent=2)}</pre>"
                                except Exception:
                                    doc_container.content = resp.text
                            else:
                                doc_container.content = resp.text
                        else:
                            doc_container.content = f"<p class='text-red-600'>Failed to load documentation (status {resp.status_code}).</p>"
                    except Exception as e:
                        doc_container.content = f"<p class='text-red-600'>Error loading documentation: {str(e)}</p>"

                reload_btn.on_click(load_docs)
                doc_choice.on("update:model-value", lambda _: load_docs())

                load_docs()

