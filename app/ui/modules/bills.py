"""Bills Module - Bill Management UI

This module provides the bill management interface including:
- Bill creation and editing
- Bill deletion
- Payment method management
- Frequency scheduling
- Account and category association
- Integration with budget bills system
"""

import sys
from typing import Any, Dict, List
from pathlib import Path

# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import requests
from app.config import API_URL
from app.ui.utils import fetch_accounts, fetch_bills, fetch_categories, handle_error, parse_date, get_payment_method_label, format_datetime, format_date

try:
    from app.models.schemas import FrequencyEnum, PaymentMethod
except ImportError:
    from ..models.schemas import FrequencyEnum, PaymentMethod


def get_payment_method_value(label: str) -> str:
    """Convert payment method display label back to enum value.
    
    Args:
        label: Human-readable label (e.g., 'Manual', 'Automatic')
    
    Returns:
        Payment method enum value for API calls
    """
    label_to_value_map = {
        "Manual": PaymentMethod.MANUAL.value,
        "Automatic": PaymentMethod.AUTOMATIC.value,
        "Transfer": PaymentMethod.TRANSFER.value,
        "Other": PaymentMethod.OTHER.value,
    }
    return label_to_value_map.get(label, PaymentMethod.MANUAL.value)


def update_bill(
    bill_id: str,
    name: str,
    budgeted_amount: float,
    description: str | None = None,
    frequency: str | None = None,
    payment_method: str | None = None,
    update_scope: str | None = None,
    account_id: str | None = None,
    category_id: str | None = None,
    transfer_account_id: str | None = None,
) -> bool:
    """Update an existing bill via API.
    
    Args:
        bill_id: Unique bill identifier
        name: Updated bill name
        budgeted_amount: Updated budgeted amount
        description: Updated description (optional)
        frequency: Payment frequency (e.g., 'monthly', 'weekly')
        payment_method: Payment method enum value
        update_scope: Scope of update for recurring bills
        account_id: Associated payment account ID
        category_id: Associated category ID
    
    Returns:
        True if update succeeded, False otherwise
    """
    import requests as req
    from app.config import API_URL
    payload = {
        "name": name,
        "budgeted_amount": budgeted_amount,
    }
    if description is not None:
        payload["description"] = description
    if frequency:
        payload["frequency"] = frequency
    if payment_method:
        payload["payment_method"] = payment_method
    if update_scope:
        payload["update_scope"] = update_scope
    if account_id:
        payload["account_id"] = account_id
    if category_id is not None:
        payload["category_id"] = category_id
    if transfer_account_id:
        payload["transfer_account_id"] = transfer_account_id
    resp = req.patch(f"{API_URL}/bills/{bill_id}", json=payload)
    if resp.status_code != 200:
        return False
    return True


def delete_bill(bill_id: str) -> bool:
    """Delete a bill permanently via API.
    
    Args:
        bill_id: Unique bill identifier
    
    Returns:
        True if deletion succeeded, False otherwise
    """
    import requests as req
    from app.config import API_URL
    resp = req.delete(f"{API_URL}/bills/{bill_id}")
    if resp.status_code != 200:
        return False
    return True


def build_bills_tab(ui, requests, API_URL, _refresh_dashboard_ref, register_refresh_callback, format_currency, datetime, timezone, open_budget_bill_edit_dialog_global, _refresh_budget_bills_ref, _refresh_transactions_ref, *args):
    """Build the complete bills tab UI with all components.
    
    Creates:
        - Create bill button and dialog
        - Bills table with edit/delete actions
        - Payment method selector
        - Frequency scheduler
        - Account and category associations
    
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
        _refresh_budget_bills_ref: Reference to budget bills refresh callback
        _refresh_transactions_ref: Reference to transactions refresh callback
        *args: Additional arguments passed by dynamic module loader
    """
    with ui.row().classes("items-center justify-start w-full mb-2"):
        create_bill_btn = ui.button("Create Bill", color="primary")

    create_bill_dialog = ui.dialog()
    with create_bill_dialog, ui.card().classes("w-full max-w-lg"):
        ui.label("Create Bill").classes("text-lg font-semibold")

        bill_create_name = ui.input(label="Name", placeholder="Electric Bill")
        bill_create_description = ui.input(label="Description (optional)", placeholder="Monthly utility bill")
        bill_create_budgeted = ui.number(label="Budgeted Amount", format="%.2f", value=0.0)
        bill_create_frequency = ui.select(
                [freq.value for freq in FrequencyEnum],
                label="Frequency",
                value="monthly",
        )
        payment_method_options = {"Manual": "manual", "Automatic": "automatic", "Transfer": "transfer", "Other": "other"}
        bill_create_payment_method = ui.select(
                options=payment_method_options,
                label="Payment Method",
                value="Manual",
        )
        bill_create_transfer_account = ui.select(
                label="Transfer To Account",
                options=[],
        ).props("dense outlined").classes("hidden")

        def on_payment_method_change():
                if bill_create_payment_method.value == "Transfer":
                    bill_create_transfer_account.classes(remove="hidden")
                else:
                    bill_create_transfer_account.classes(add="hidden")

        bill_create_payment_method.on_value_change(on_payment_method_change)
        bill_create_account = ui.select(label="Account", options={}).props("dense outlined")
        bill_create_category = ui.select(
                label="Category",
                options=["Uncategorized"],
                value="Uncategorized",
        ).props("dense outlined")
        bill_create_start_freq = ui.input(label="Frequency Start Date", placeholder="Click to select date").classes("w-full")
        bill_create_start_freq_picker = ui.date(mask="YYYY-MM-DD").props("dense outlined").classes("hidden")

        def toggle_create_start_freq_picker():
                bill_create_start_freq_picker.classes(toggle="hidden")

        bill_create_start_freq.on("click", toggle_create_start_freq_picker)

        def on_create_start_freq_selected():
                if bill_create_start_freq_picker.value:
                    date_str = bill_create_start_freq_picker.value.isoformat() if hasattr(bill_create_start_freq_picker.value, 'isoformat') else str(bill_create_start_freq_picker.value)
                    bill_create_start_freq.value = date_str
                    bill_create_start_freq_picker.classes(add="hidden")

        bill_create_start_freq_picker.on_value_change(on_create_start_freq_selected)

        def create_bill_submit():
                if not bill_create_name.value:
                    ui.notify("Bill name is required", type="warning")
                    return

                if not bill_create_account.value:
                    ui.notify("Account is required", type="warning")
                    return

                # Get account ID from selected name
                accounts = fetch_accounts()
                account_lookup_create = {a["name"]: str(a["id"]) for a in accounts}
                account_id = account_lookup_create.get(bill_create_account.value)

                if not account_id:
                    ui.notify("Selected account not found", type="warning")
                    return

                # Convert payment_method label to value using helper
                payment_method_value = get_payment_method_value(bill_create_payment_method.value)

                # Get category ID if selected
                selected_category_name = bill_create_category.value or "Uncategorized"
                category_id = None
                if selected_category_name and selected_category_name != "Uncategorized":
                    categories = fetch_categories()
                    category_lookup_create = {c["name"]: str(c["id"]) for c in categories}
                    category_id = category_lookup_create.get(selected_category_name)

                payload = {
                    "name": bill_create_name.value,
                    "description": bill_create_description.value or None,
                    "budgeted_amount": float(bill_create_budgeted.value or 0.0),
                    "frequency": bill_create_frequency.value,
                    "payment_method": payment_method_value,
                }

                # Get transfer account ID if payment method is transfer
                if payment_method_value == "transfer" and bill_create_transfer_account.value:
                    accounts = fetch_accounts()
                    account_lookup_create = {a["name"]: str(a["id"]) for a in accounts}
                    transfer_account_id = account_lookup_create.get(bill_create_transfer_account.value)
                    if transfer_account_id:
                        payload["transfer_account_id"] = transfer_account_id

                if category_id:
                    payload["category_id"] = category_id

                if bill_create_start_freq.value:
                    payload["start_freq"] = bill_create_start_freq.value

                resp = requests.post(
                    f"{API_URL}/bills/{account_id}",
                    json=payload,
                )

                if resp.status_code != 200:
                    ui.notify(handle_error(resp), type="negative")
                    return

                ui.notify("Bill created", type="positive")
                bill_create_name.value = ""
                bill_create_description.value = ""
                bill_create_budgeted.value = 0.0
                bill_create_frequency.value = "monthly"
                bill_create_payment_method.value = "Manual"
                bill_create_account.value = ""
                bill_create_category.value = "Uncategorized"
                bill_create_start_freq.value = ""
                create_bill_dialog.close()
                refresh_bills()

        with ui.row().classes("gap-2 justify-end w-full mt-2"):
                ui.button("Cancel", on_click=create_bill_dialog.close).props("flat color=grey")
                ui.button("Create", on_click=create_bill_submit).props("color=primary")

    def open_create_bill_dialog():
        # Populate account options
        accounts = fetch_accounts()
        bill_create_account.options = [a["name"] for a in accounts]
        if accounts:
            bill_create_account.value = accounts[0]["name"]
        bill_create_account.update()

        # Populate transfer account options
        bill_create_transfer_account.options = [a["name"] for a in accounts]
        bill_create_transfer_account.update()

        # Populate categories
        try:
            categories = fetch_categories()
            category_names = sorted([c["name"] for c in categories])
            bill_create_category.options = ["Uncategorized"] + category_names
            bill_create_category.value = "Uncategorized"
            bill_create_category.update()
        except Exception:
            bill_create_category.options = ["Uncategorized"]
            bill_create_category.value = "Uncategorized"
            bill_create_category.update()

        # Set start_freq to today
        today = datetime.datetime.now(timezone.utc).date().isoformat()
        bill_create_start_freq.value = today
        bill_create_start_freq_picker.value = today

        create_bill_dialog.open()

    create_bill_btn.on_click(open_create_bill_dialog)


    from app.ui.global_dialogs import setup_test_frequency_dialog
    test_freq_dialog, open_test_freq_dialog = setup_test_frequency_dialog(ui, title="Test Bill Frequency")
    with ui.row().classes("items-center justify-start w-full mb-2 mt-4"):
        ui.button("Test frequency", color="accent", on_click=open_test_freq_dialog)

    ui.label("Bills")

    month_names = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
    ]
    bills_table = ui.table(
            columns=[
                {"name": "name", "label": "Name", "field": "name", "sortable": True},
                {"name": "bank_account", "label": "Account", "field": "bank_account", "sortable": True},
                {
                    "name": "budgeted_amount",
                    "label": "Budgeted",
                    "field": "budgeted_amount",
                    "align": "right",
                    "sortable": True,
                },
                {"name": "frequency", "label": "Freq", "field": "frequency", "sortable": True},
                {"name": "actions", "label": "Actions", "field": "actions", "align": "center"},
            ],
            rows=[],
            row_key="id",
    ).classes("w-full")

    # Add custom slot for action buttons
    bills_table.add_slot(
            'body-cell-actions',
            r'''
            <q-td :props="props">
                <q-btn flat dense round color="primary" icon="edit"
                       @click="$parent.$emit('edit-bill', props.row)">
                    <q-tooltip>Edit Bill</q-tooltip>
                </q-btn>
            </q-td>
            '''
    )

    def handle_edit_bill(event):
            bill = event.args
            open_bill_edit(bill.get("bill_obj", bill))

    bills_table.on('edit-bill', handle_edit_bill)

    bills_state: Dict[str, List[Dict[str, Any]]] = {"all": []}
    account_lookup: Dict[str, str] = {}  # id -> name for display
    account_options: List[Dict[str, str]] = []  # select options as label/value
    category_lookup: Dict[str, str] = {}  # id -> name for display
    selected_bill: Dict[str, Any] = {"id": None, "row": None}
    sort_state: Dict[str, Any] = {"column": "name", "descending": False}

    def _load_categories_into_dropdown() -> None:
            """Fetch categories and update the edit dropdown; keep 'Uncategorized'."""
            nonlocal category_lookup
            try:
                categories = fetch_categories()
                category_lookup = {str(cat.get("id")): cat.get("name", "") for cat in categories}
                category_names = [name for name in category_lookup.values() if name]
                category_names.sort()
                bill_edit_category.options = ["Uncategorized"] + category_names
                if bill_edit_category.value not in bill_edit_category.options:
                    bill_edit_category.value = "Uncategorized"
                bill_edit_category.update()
            except Exception:
                category_lookup = {}
                bill_edit_category.options = ["Uncategorized"]
                bill_edit_category.value = "Uncategorized"
                bill_edit_category.update()

    def on_bill_selection(event) -> None:
            payload = event.args
            rows = []
            if isinstance(payload, list):
                rows = payload
            elif isinstance(payload, dict):
                rows = payload.get("rows") or payload.get("selection") or []
            if rows:
                row = rows[0]
                selected_bill["id"] = row.get("id")
                selected_bill["row"] = row
            else:
                selected_bill["id"] = None
                selected_bill["row"] = None
            if selected_bill["id"] is None:
                bill_edit_btn.disable()
            else:
                bill_edit_btn.enable()

    bills_table.on("selection", on_bill_selection)

    def on_bill_sort(event) -> None:
            """Handle column sorting"""
            payload = event.args
            if isinstance(payload, dict):
                sort_state["column"] = payload.get("sortBy", "name")
                sort_state["descending"] = payload.get("descending", False)
                apply_bill_filter()

    bills_table.on("request", on_bill_sort)

    def apply_bill_filter() -> None:
            rows = []
            for bill in bills_state["all"]:
                try:
                    account_id = str(bill.get("account_id")) if bill.get("account_id") else ""
                    try:
                        amount = float(bill.get("budgeted_amount", 0.0) or 0.0)
                    except Exception:
                        amount = 0.0
                    account_name = account_lookup.get(account_id, account_id) or "Unknown"
                    rows.append(
                        {
                            "id": bill.get("id"),
                            "name": bill.get("name"),
                            "bank_account": account_name,
                            "account_id": account_id,
                            "budgeted_amount": f"{amount:.2f}",
                            "frequency": bill.get("frequency"),
                            "bill_obj": bill,
                            "actions": "edit",
                        }
                    )
                except Exception:
                    continue
            # Sort rows based on current sort_state
            sort_column = sort_state["column"]
            reverse = sort_state["descending"]
            if sort_column in ["budgeted_amount"]:
                # For numeric columns, convert to float for sorting
                rows.sort(key=lambda r: float(r.get(sort_column, "0").replace(",", "")), reverse=reverse)
            else:
                rows.sort(key=lambda r: r.get(sort_column, ""), reverse=reverse)
            bills_table.rows = rows

    # Edit bill dialog
    bill_edit_dialog = ui.dialog()
    with bill_edit_dialog, ui.card().classes("w-full max-w-lg"):
            ui.label("Edit bill")
            bill_edit_name = ui.input(label="Name")
            bill_edit_description = ui.input(label="Description (optional)")
            bill_edit_budgeted = ui.number(label="Budgeted Amount", format="%.2f")
            bill_edit_frequency = ui.select(
                [freq.value for freq in FrequencyEnum],
                label="Frequency",
            )
            payment_method_options = {"Manual": "manual", "Automatic": "automatic", "Transfer": "transfer", "Other": "other"}
            bill_edit_payment_method = ui.select(options=payment_method_options, label="Payment Method")
            bill_edit_transfer_account = ui.select(
                label="Transfer To Account",
                options=[],
            ).props("dense outlined").classes("hidden")

            def on_edit_payment_method_change():
                if bill_edit_payment_method.value == "Transfer":
                    bill_edit_transfer_account.classes(remove="hidden")
                else:
                    bill_edit_transfer_account.classes(add="hidden")

            bill_edit_payment_method.on_value_change(on_edit_payment_method_change)
            bill_edit_account = ui.select(label="Account", options={}).props("dense outlined")
            bill_edit_category = ui.select(
                label="Category",
                options=["Uncategorized"],
                value="Uncategorized",
            ).props("dense outlined")
            bill_edit_start_freq = ui.input(label="Frequency Start Date (YYYY-MM-DD)").classes("w-full")
            bill_edit_start_freq_picker = ui.date(mask="YYYY-MM-DD").props("dense outlined").classes("hidden")
            def toggle_start_freq_picker():
                bill_edit_start_freq_picker.classes(toggle="hidden")
            bill_edit_start_freq.on("click", toggle_start_freq_picker)
            def on_start_freq_selected():
                if bill_edit_start_freq_picker.value:
                    date_str = bill_edit_start_freq_picker.value.isoformat() if hasattr(bill_edit_start_freq_picker.value, 'isoformat') else str(bill_edit_start_freq_picker.value)
                    bill_edit_start_freq.value = date_str
                    bill_edit_start_freq_picker.classes(add="hidden")
            bill_edit_start_freq_picker.on_value_change(on_start_freq_selected)

            def delete_bill_current():
                bill_id = bill_edit_dialog.props.get("data-id")
                if not bill_id:
                    bill_edit_dialog.close()
                    return
                ok = delete_bill(bill_id)
                if ok:
                    ui.notify("Bill deleted", type="positive")
                    refresh_bills()
                    bill_edit_dialog.close()

            def save_bill_edit():
                bill_id = bill_edit_dialog.props.get("data-id")
                if not bill_id:
                    bill_edit_dialog.close()
                    return

                # Convert account name back to ID
                selected_account_name = bill_edit_account.value
                account_id = next((aid for aid, aname in account_lookup.items() if aname == selected_account_name), None)
                selected_category_name = bill_edit_category.value or "Uncategorized"
                category_id = None
                if selected_category_name and selected_category_name != "Uncategorized":
                    category_id = next((cid for cid, cname in category_lookup.items() if cname == selected_category_name), None)
                # Convert payment_method label back to enum value using helper
                payment_method_value = get_payment_method_value(bill_edit_payment_method.value)

                # Get transfer account ID if payment method is transfer
                transfer_account_id = None
                if payment_method_value == "transfer" and bill_edit_transfer_account.value:
                    accounts = fetch_accounts()
                    account_lookup_edit = {a["name"]: str(a["id"]) for a in accounts}
                    transfer_account_id = account_lookup_edit.get(bill_edit_transfer_account.value)

                ok = update_bill(
                    bill_id=bill_id,
                    name=bill_edit_name.value,
                    description=bill_edit_description.value or None,
                    budgeted_amount=float(bill_edit_budgeted.value or 0.0),
                    frequency=bill_edit_frequency.value,
                    payment_method=payment_method_value,
                    account_id=account_id if account_id else None,
                    category_id=category_id,
                    transfer_account_id=transfer_account_id,
                )
                if ok:
                    ui.notify("Bill updated", type="positive")
                    refresh_bills()
                    bill_edit_dialog.close()
                else:
                    ui.notify("Failed to update bill", type="negative")

            with ui.row().classes("justify-between gap-2"):
                ui.button("Delete", color="negative", on_click=delete_bill_current)
                with ui.row().classes("gap-2"):
                    ui.button("Cancel", on_click=bill_edit_dialog.close)
                    ui.button("Save", color="primary", on_click=save_bill_edit)

    def open_bill_edit(bill: Dict[str, Any]) -> None:
            # Ensure categories are loaded when opening dialog
            _load_categories_into_dropdown()
            bill_edit_dialog.props["data-id"] = bill.get("id")
            bill_edit_name.value = bill.get("name", "")
            bill_edit_description.value = bill.get("description", "")
            bill_edit_budgeted.value = bill.get("budgeted_amount", 0.0)
            bill_edit_frequency.value = bill.get("frequency", "monthly")
            # Convert payment_method to display label using helper
            payment_method_value = bill.get("payment_method", "manual")
            payment_method_label = get_payment_method_label(payment_method_value)
            bill_edit_payment_method.value = payment_method_label

            # Populate transfer account select
            accounts = fetch_accounts()
            bill_edit_transfer_account.options = [a["name"] for a in accounts]
            # Set current transfer account if exists
            transfer_account_id_value = str(bill.get("transfer_account_id")) if bill.get("transfer_account_id") else ""
            if transfer_account_id_value:
                transfer_account_name = next((a["name"] for a in accounts if str(a["id"]) == transfer_account_id_value), None)
                bill_edit_transfer_account.value = transfer_account_name
            bill_edit_transfer_account.update()

            # Show/hide transfer account field based on payment method
            if payment_method_label == "Transfer":
                bill_edit_transfer_account.classes(remove="hidden")
            else:
                bill_edit_transfer_account.classes(add="hidden")

            # Populate account select with list of names
            account_names = [account_lookup.get(aid, aid) for aid in sorted(account_lookup.keys())]
            bill_edit_account.options = account_names
            # Set value to the current account name
            account_id_value = str(bill.get("account_id")) if bill.get("account_id") else ""
            current_account_name = account_lookup.get(account_id_value, "") if account_id_value else None
            bill_edit_account.value = current_account_name
            # Populate categories
            category_id_value = str(bill.get("category_id")) if bill.get("category_id") else ""
            current_category_name = category_lookup.get(category_id_value, "Uncategorized") if category_id_value else "Uncategorized"
            bill_edit_category.value = current_category_name
            # Set start_freq date
            start_freq_val = bill.get("start_freq")
            if start_freq_val:
                parsed_start_freq = parse_date(start_freq_val)
                bill_edit_start_freq.value = parsed_start_freq.date().isoformat() if parsed_start_freq else ""
            else:
                bill_edit_start_freq.value = ""
            bill_edit_dialog.open()



    def refresh_bills() -> None:
            nonlocal account_lookup
            try:
                accounts = fetch_accounts()
                account_lookup = {str(ba.get("id")): ba.get("name", "") for ba in accounts}
            except Exception:
                account_lookup = {}
            _load_categories_into_dropdown()
            try:
                bills_state["all"] = fetch_bills()
            except Exception:
                bills_state["all"] = []
            selected_bill["id"] = None
            selected_bill["row"] = None
            apply_bill_filter()

    register_refresh_callback(refresh_bills)
    refresh_bills()
