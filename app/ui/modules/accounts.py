"""Accounts Module - Account Management UI

This module provides the complete account management interface including:
- Account CRUD operations (Create, Read, Update, Delete)
- Financial operations (Add funds, Deduct funds, Transfer between accounts)
- Transaction history viewing
- Income source management
- Account balance tracking

The module handles all account-related UI components and their interactions.
"""

import json
import sys
from typing import Any, Dict, List
from datetime import timedelta
from pathlib import Path

# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import requests
from app.config import API_URL
from app.ui.utils import fetch_accounts, handle_error, parse_date, format_datetime, format_date


def create_account(name: str, account_type: str, description: str = None, balance: float = 0.0) -> tuple[bool, str | None]:
    """Create a new account via API.
    
    Args:
        name: Account name
        account_type: Type of account (e.g., "Checking", "Savings", "Credit Card")
        description: Optional account description
        balance: Initial account balance (default: 0.0)
    
    Returns:
        tuple: (success: bool, error_message: str | None)
            - success: True if account was created successfully
            - error_message: Error details if creation failed, None otherwise
    """
    payload = {
        "name": name,
        "account_type": json.dumps({"name": account_type}),
        "balance": balance,
    }
    if description:
        payload["description"] = description
    resp = requests.post(f"{API_URL}/accounts/", json=payload)
    if resp.status_code != 200:
        return False, handle_error(resp)
    return True, None


def update_account(account_id: str, name: str, account_type: str, description: str = None, balance: float = 0.0, enabled: bool = True) -> tuple[bool, str | None]:
    """Update an existing account via API.
    
    Args:
        account_id: Unique account identifier
        name: Updated account name
        account_type: Updated account type
        description: Updated account description (optional)
        balance: Updated account balance
        enabled: Whether the account is active (default: True)
    
    Returns:
        tuple: (success: bool, error_message: str | None)
            - success: True if account was updated successfully
            - error_message: Error details if update failed, None otherwise
    """
    payload = {
        "name": name,
        "account_type": json.dumps({"name": account_type}),
        "balance": balance,
        "enabled": enabled,
    }
    if description:
        payload["description"] = description
    resp = requests.patch(f"{API_URL}/accounts/{account_id}", json=payload)
    if resp.status_code != 200:
        return False, handle_error(resp)
    return True, None


def toggle_account_enabled(account_id: str, enabled: bool) -> tuple[bool, str | None]:
    """Toggle account enabled status.
    
    Returns:
        tuple: (success: bool, error_message: str | None)
    """
    resp = requests.patch(f"{API_URL}/accounts/{account_id}", json={"enabled": enabled})
    if resp.status_code != 200:
        return False, handle_error(resp)
    return True, None


def delete_account(account_id: str) -> tuple[bool, str | None]:
    """Delete account permanently via API.
    
    Args:
        account_id: Unique account identifier
    
    Returns:
        tuple: (success: bool, error_message: str | None)
            - success: True if account was deleted successfully
            - error_message: Error details if deletion failed, None otherwise
    """
    resp = requests.delete(f"{API_URL}/accounts/{account_id}")
    if resp.status_code != 200:
        return False, handle_error(resp)
    return True, None


def build_accounts_tab(ui, requests, API_URL, _refresh_dashboard_ref, register_refresh_callback, format_currency, datetime, timezone, open_budget_bill_edit_dialog_global, _refresh_budget_bills_ref, _refresh_transactions_ref, *args):
    """Build complete accounts tab UI with all components and dialogs.
    
    Creates:
        - Create account button and dialog
        - Accounts table with action buttons (edit, add funds, deduct funds, transfer, view transactions)
        - Edit account dialog
        - Add/Deduct funds dialogs
        - Transfer funds dialog
        - Transaction history dialog
        - Income sources section with create/edit/delete functionality
    
    Args:
        ui: NiceGUI ui instance
        requests: HTTP requests module
        API_URL: Base API URL for backend calls
        _refresh_dashboard_ref: Reference to dashboard refresh callback
        register_refresh_callback: Function to register refresh callbacks
        fetch_budgetbills: Function to fetch budget bills
        format_currency: Currency formatting utility function
        datetime: Datetime module
        timezone: Timezone module
        open_budget_bill_edit_dialog_global: Global dialog opener for budget bills
        _refresh_budget_bills_ref: Reference to budget bills refresh callback
        _refresh_transactions_ref: Reference to transactions refresh callback
        *args: Additional arguments passed by dynamic module loader
    """
    with ui.row().classes("items-center justify-start w-full mb-2"):
        create_account_btn = ui.button("Create Account", color="primary")

    create_account_dialog = ui.dialog()
    with create_account_dialog, ui.card().classes("w-full max-w-lg"):
        ui.label("Create Account").classes("text-lg font-semibold")
        name_input = ui.input(label="Name", placeholder="Checking")
        account_type_options = {"Checking": "Checking", "Savings": "Savings", "Investment": "Investment", "Cash": "Cash", "Credit Card": "Credit Card", "Personal Loan": "Personal Loan", "Debit Card": "Debit Card", "Store Card": "Store Card", "Mortgage": "Mortgage", "Auto Loan": "Auto Loan", "Student Loan": "Student Loan", "Line of Credit": "Line of Credit", "Money Market": "Money Market", "Certificate of Deposit": "Certificate of Deposit", "Retirement Account": "Retirement Account", "Brokerage Account": "Brokerage Account", "Health Savings Account": "Health Savings Account", "PayPal": "PayPal", "Cryptocurrency Wallet": "Cryptocurrency Wallet"}
        type_select = ui.select(
            options=account_type_options,
            label="Account type",
            value="Checking",
        )
        description_input = ui.input(label="Description (optional)", placeholder="e.g., Personal checking account")
        balance_input = ui.number(label="Starting balance", value=1000.0, format="%.2f")

        def submit() -> None:
            if not name_input.value:
                ui.notify("Name is required", type="warning")
                return
            ok, error = create_account(
                name=name_input.value,
                account_type=type_select.value,
                description=description_input.value if description_input.value else None,
                balance=float(balance_input.value or 0.0),
            )
            if ok:
                ui.notify("Account created", type="positive")
                name_input.value = ""
                description_input.value = ""
                balance_input.value = 1000.0
                create_account_dialog.close()
                refresh()
            else:
                ui.notify(error or "Failed to create account", type="negative")

        with ui.row().classes("gap-2 justify-end w-full mt-2"):
            ui.button("Cancel", on_click=create_account_dialog.close).props("flat color=grey")
            ui.button("Create", on_click=submit).props("color=primary")

    def open_create_account_dialog():
        name_input.value = ""
        type_select.value = "Checking"
        description_input.value = ""
        balance_input.value = 1000.0
        create_account_dialog.open()

    create_account_btn.on_click(open_create_account_dialog)

    with ui.card().classes("w-full max-w-4xl"):
        ui.label("Accounts").classes("text-lg font-semibold mb-2")

        table = ui.table(
            columns=[
                {"name": "name", "label": "Name", "field": "name", "sortable": True},
                {"name": "account_type", "label": "Type", "field": "account_type", "sortable": True},
                {"name": "description", "label": "Description", "field": "description", "sortable": False},
                {"name": "balance", "label": "Balance", "field": "balance", "align": "right", "sortable": True},
                {"name": "enabled", "label": "Enabled", "field": "enabled", "sortable": True},
                {"name": "actions", "label": "Actions", "field": "actions", "align": "center"},
            ],
            rows=[],
            row_key="id",
        ).classes("w-full")

    # Add custom slot for action buttons
    table.add_slot(
        'body-cell-actions',
        r'''
        <q-td :props="props">
            <q-btn flat dense round color="primary" icon="edit"
                   @click="$parent.$emit('edit-account', props.row)">
                <q-tooltip>Edit Account</q-tooltip>
            </q-btn>
            <q-btn flat dense round color="green" icon="add_circle"
                   @click="$parent.$emit('add-funds', props.row)">
                <q-tooltip>Add Funds</q-tooltip>
            </q-btn>
            <q-btn flat dense round color="orange" icon="remove_circle"
                   @click="$parent.$emit('deduct-funds', props.row)">
                <q-tooltip>Deduct Funds</q-tooltip>
            </q-btn>
            <q-btn flat dense round color="blue" icon="compare_arrows"
                   @click="$parent.$emit('transfer-funds', props.row)">
                <q-tooltip>Transfer Funds</q-tooltip>
            </q-btn>
            <q-btn flat dense round color="purple" icon="receipt"
                   @click="$parent.$emit('view-transactions', props.row)">
                <q-tooltip>View Transactions</q-tooltip>
            </q-btn>
        </q-td>
        '''
    )

    def handle_edit_account(event):
        account = event.args
        open_edit(account)

    def handle_add_funds(event):
        account = event.args
        open_add_funds(account)

    def handle_deduct_funds(event):
        account = event.args
        open_deduct_funds(account)

    def handle_transfer_funds(event):
        account = event.args
        open_transfer(account)

    def handle_view_transactions(event):
        account = event.args
        account_id = account.get("id")
        account_name = account.get("name", "Account")
        account_txn_title.text = f"Transactions for: {account_name}"

        # Get all transactions
        txn_resp = requests.get(f"{API_URL}/transactions/")
        if txn_resp.status_code != 200:
            ui.notify("Failed to load transactions", type="warning")
            return

        transactions = txn_resp.json()

        # Filter transactions by account_id
        account_transactions = [
            txn for txn in transactions 
            if txn.get("account_id") == account_id
        ]

        # Format rows
        rows = []
        for txn in account_transactions:
            occurred_at = parse_date(txn.get("occurred_at"))
            trans_date = occurred_at.strftime("%Y-%m-%d %H:%M") if occurred_at else "N/A"

            trans_type = txn.get("transaction_type", "").capitalize()
            amount = float(txn.get("amount", 0.0))
            note = txn.get("note", "")

            rows.append({
                "id": txn.get("id"),
                "occurred_at": trans_date,
                "type": trans_type,
                "amount": format_currency(amount),
                "note": note,
            })

        # Sort by date descending
        rows.sort(key=lambda r: r["occurred_at"], reverse=True)
        account_txn_table.rows = rows
        account_txn_dialog.open()

    # Connect table event handlers
    table.on('edit-account', handle_edit_account)
    table.on('add-funds', handle_add_funds)
    table.on('deduct-funds', handle_deduct_funds)
    table.on('transfer-funds', handle_transfer_funds)
    table.on('view-transactions', handle_view_transactions)

    selected: dict[str, Any] = {"id": None, "enabled": None, "row": None}

    def render_rows(accounts: List[Dict[str, Any]]) -> None:
        rows = []
        for acc in accounts:
            try:
                acct_type = json.loads(acc.get("account_type", "{}")).get("name")
            except Exception:
                acct_type = acc.get("account_type")
            # Store both parsed and original for edit dialog
            rows.append({**acc, "account_type": acct_type, "account_type_raw": acc.get("account_type")})
        table.rows = rows

    def refresh() -> None:
        accounts = fetch_accounts()
        render_rows(accounts)

    def on_delete(account_id: str) -> None:
        ok, error = delete_account(account_id)
        if ok:
            ui.notify("Deleted", type="positive")
            refresh()
        else:
            ui.notify(error or "Failed to delete account", type="negative")

    # Edit dialog
    edit_dialog = ui.dialog()
    with edit_dialog, ui.card().classes("w-full max-w-lg"):
        ui.label("Edit Account").classes("text-lg font-semibold")
        edit_name = ui.input(label="Name")
        account_type_options = {"Checking": "Checking", "Savings": "Savings", "Investment": "Investment", "Cash": "Cash", "Credit Card": "Credit Card", "Personal Loan": "Personal Loan", "Debit Card": "Debit Card", "Store Card": "Store Card", "Mortgage": "Mortgage", "Auto Loan": "Auto Loan", "Student Loan": "Student Loan", "Line of Credit": "Line of Credit", "Money Market": "Money Market", "Certificate of Deposit": "Certificate of Deposit", "Retirement Account": "Retirement Account", "Brokerage Account": "Brokerage Account", "Health Savings Account": "Health Savings Account", "PayPal": "PayPal", "Cryptocurrency Wallet": "Cryptocurrency Wallet"}
        edit_type = ui.select(options=account_type_options, label="Account type", value="Checking")
        edit_description = ui.input(label="Description (optional)")
        with ui.row().classes("items-center gap-2"):
            ui.label("Enabled")
            edit_enabled = ui.switch(value=True)

        def delete_current():
            acc_id = edit_dialog.props.get("data-id")
            if not acc_id:
                edit_dialog.close()
                return
            on_delete(acc_id)
            edit_dialog.close()

        def save_edit():
            acc_id = edit_dialog.props.get("data-id")
            if not acc_id:
                edit_dialog.close()
                return
            enabled_value = edit_enabled.value
            ok, error = update_account(
                account_id=acc_id,
                name=edit_name.value,
                account_type=edit_type.value,
                description=edit_description.value if edit_description.value else None,
                balance=0.0,
                enabled=enabled_value,
            )
            if ok:
                ui.notify("Account updated", type="positive")
                edit_dialog.close()
                refresh()
                if _refresh_dashboard_ref:
                    _refresh_dashboard_ref[0]()
            else:
                ui.notify(error or "Failed to update account", type="negative")

        with ui.row().classes("justify-between gap-2"):
            ui.button("Delete", color="negative", on_click=delete_current)
            with ui.row().classes("gap-2"):
                ui.button("Cancel", on_click=edit_dialog.close)
                ui.button("Save", color="primary", on_click=save_edit)

    def open_edit(account: Dict[str, Any]) -> None:
        # Prefill form fields
        edit_dialog.props["data-id"] = account.get("id")
        edit_name.value = account.get("name")

        # Get account type - it's already parsed in the table row
        acct_type = account.get("account_type", "Checking")
        # Normalize to title case to match select options
        if acct_type:
            acct_type = acct_type.title()
        # Ensure it matches one of our options
        valid_types = [opt for opt in edit_type.options]
        if acct_type not in valid_types:
            acct_type = "Checking"
        edit_type.value = acct_type
        edit_type.update()
        edit_description.value = account.get("description", "")
        edit_enabled.value = account.get("enabled", True)
        edit_dialog.open()

    # Add Funds dialog
    add_funds_dialog = ui.dialog()
    with add_funds_dialog, ui.card().classes("w-full max-w-md"):
        ui.label("Add Funds").classes("text-lg font-semibold")
        add_funds_amount = ui.number(label="Amount", value=0.0, format="%.2f")
        add_funds_note = ui.input(label="Note (optional)")

        def submit_add_funds():
            acc_id = add_funds_dialog.props.get("data-id")
            if not acc_id:
                add_funds_dialog.close()
                return
            amount = float(add_funds_amount.value or 0.0)
            if amount <= 0:
                ui.notify("Amount must be greater than 0", type="warning")
                return
            
            payload = {
                "amount": amount,
                "note": add_funds_note.value or "Manual deposit",
            }
            resp = requests.post(f"{API_URL}/accounts/{acc_id}/add-funds", json=payload)
            if resp.status_code == 200:
                ui.notify("Funds added successfully", type="positive")
                add_funds_dialog.close()
                refresh()
                if _refresh_dashboard_ref:
                    _refresh_dashboard_ref[0]()
                if _refresh_transactions_ref:
                    _refresh_transactions_ref[0]()
            else:
                ui.notify(handle_error(resp), type="negative")

        with ui.row().classes("gap-2 justify-end w-full mt-2"):
            ui.button("Cancel", on_click=add_funds_dialog.close).props("flat color=grey")
            ui.button("Add", color="primary", on_click=submit_add_funds)

    # Deduct Funds dialog
    deduct_funds_dialog = ui.dialog()
    with deduct_funds_dialog, ui.card().classes("w-full max-w-md"):
        ui.label("Deduct Funds").classes("text-lg font-semibold")
        deduct_funds_amount = ui.number(label="Amount", value=0.0, format="%.2f")
        deduct_funds_note = ui.input(label="Note (optional)")

        def submit_deduct_funds():
            acc_id = deduct_funds_dialog.props.get("data-id")
            if not acc_id:
                deduct_funds_dialog.close()
                return
            amount = float(deduct_funds_amount.value or 0.0)
            if amount <= 0:
                ui.notify("Amount must be greater than 0", type="warning")
                return
            
            payload = {
                "amount": amount,
                "note": deduct_funds_note.value or "Manual withdrawal",
            }
            resp = requests.post(f"{API_URL}/accounts/{acc_id}/deduct-funds", json=payload)
            if resp.status_code == 200:
                ui.notify("Funds deducted successfully", type="positive")
                deduct_funds_dialog.close()
                refresh()
                if _refresh_dashboard_ref:
                    _refresh_dashboard_ref[0]()
                if _refresh_transactions_ref:
                    _refresh_transactions_ref[0]()
            else:
                ui.notify(handle_error(resp), type="negative")

        with ui.row().classes("gap-2 justify-end w-full mt-2"):
            ui.button("Cancel", on_click=deduct_funds_dialog.close).props("flat color=grey")
            ui.button("Deduct", color="primary", on_click=submit_deduct_funds)

    # Transfer Funds dialog
    transfer_dialog = ui.dialog()
    with transfer_dialog, ui.card().classes("w-full max-w-md"):
        ui.label("Transfer Funds").classes("text-lg font-semibold")
        transfer_from_label = ui.label("")
        transfer_to_select = ui.select(label="To Account", options=[])
        transfer_amount = ui.number(label="Amount", value=0.0, format="%.2f")
        transfer_note = ui.input(label="Note (optional)")

        def submit_transfer():
            from_id = transfer_dialog.props.get("data-id")
            if not from_id:
                transfer_dialog.close()
                return
            
            to_account_name = transfer_to_select.value
            if not to_account_name:
                ui.notify("Please select a destination account", type="warning")
                return
            
            amount = float(transfer_amount.value or 0.0)
            if amount <= 0:
                ui.notify("Amount must be greater than 0", type="warning")
                return
            
            # Find the destination account ID
            accounts = fetch_accounts()
            to_account = next((a for a in accounts if a["name"] == to_account_name), None)
            if not to_account:
                ui.notify("Destination account not found", type="warning")
                return
            
            payload = {
                "from_account_id": from_id,
                "to_account_id": to_account["id"],
                "amount": amount,
                "note": transfer_note.value or "Transfer",
            }
            resp = requests.post(f"{API_URL}/transactions/transfer", json=payload)
            if resp.status_code == 200:
                ui.notify("Transfer completed successfully", type="positive")
                transfer_dialog.close()
                refresh()
                if _refresh_dashboard_ref:
                    _refresh_dashboard_ref[0]()
                if _refresh_transactions_ref:
                    _refresh_transactions_ref[0]()
            else:
                ui.notify(handle_error(resp), type="negative")

        with ui.row().classes("gap-2 justify-end w-full mt-2"):
            ui.button("Cancel", on_click=transfer_dialog.close).props("flat color=grey")
            ui.button("Transfer", color="primary", on_click=submit_transfer)

    # View Transactions dialog
    account_txn_dialog = ui.dialog()
    with account_txn_dialog, ui.card().classes("w-full max-w-4xl"):
        account_txn_title = ui.label("Transactions").classes("text-lg font-semibold mb-2")
        account_txn_table = ui.table(
            columns=[
                {"name": "occurred_at", "label": "Date", "field": "occurred_at", "sortable": True},
                {"name": "type", "label": "Type", "field": "type", "sortable": True},
                {"name": "amount", "label": "Amount", "field": "amount", "align": "right", "sortable": True},
                {"name": "note", "label": "Note", "field": "note", "sortable": False},
            ],
            rows=[],
            row_key="id",
        ).classes("w-full")
        
        with ui.row().classes("gap-2 justify-end w-full mt-2"):
            ui.button("Close", on_click=account_txn_dialog.close)

    def open_add_funds(account: Dict[str, Any]) -> None:
        add_funds_dialog.props["data-id"] = account.get("id")
        add_funds_amount.value = 0.0
        add_funds_note.value = ""
        add_funds_dialog.open()

    def open_deduct_funds(account: Dict[str, Any]) -> None:
        deduct_funds_dialog.props["data-id"] = account.get("id")
        deduct_funds_amount.value = 0.0
        deduct_funds_note.value = ""
        deduct_funds_dialog.open()

    def open_transfer(account: Dict[str, Any]) -> None:
        transfer_dialog.props["data-id"] = account.get("id")
        transfer_from_label.text = f"From: {account.get('name')}"

        # Get all accounts except the current one
        accounts = fetch_accounts()
        other_accounts = [a for a in accounts if a["id"] != account.get("id")]
        transfer_to_select.options = [a["name"] for a in other_accounts]
        transfer_to_select.update()
        transfer_to_select.value = None

        transfer_amount.value = 0.0
        transfer_note.value = ""
        transfer_dialog.open()

    register_refresh_callback(refresh)
    refresh()

    with ui.card().classes("w-full max-w-4xl"):
        ui.label("Income Sources").classes("text-lg font-semibold mb-2")

        income_table = ui.table(
            columns=[
                {"name": "account_name", "label": "Account", "field": "account_name", "sortable": True},
                {"name": "name", "label": "Name", "field": "name", "sortable": True},
                {"name": "description", "label": "Description", "field": "description", "sortable": False},
                {"name": "amount", "label": "Amount", "field": "amount", "align": "right", "sortable": True},
                {"name": "frequency", "label": "Frequency", "field": "frequency", "sortable": True},
                {"name": "enabled", "label": "Enabled", "field": "enabled", "sortable": True},
                {"name": "actions", "label": "Actions", "field": "actions", "align": "center"},
            ],
            rows=[],
            row_key="id",
        ).classes("w-full")

        income_table.add_slot(
            'body',
            r'''
            <q-tr :props="props" :class="{'bg-green-1': props.row.due_soon}">
                <q-td v-for="col in props.cols" :key="col.name" :props="props">
                    <div v-if="col.name === 'actions'">
                        <q-btn flat dense round color="green" icon="check_circle"
                               @click="$parent.$emit('verify-deposit', props.row)">
                            <q-tooltip>Verify Deposit</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round color="primary" icon="edit"
                               @click="$parent.$emit('edit-income', props.row)">
                            <q-tooltip>Edit Income</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round color="red" icon="delete"
                               @click="$parent.$emit('delete-income', props.row)">
                            <q-tooltip>Delete Income</q-tooltip>
                        </q-btn>
                    </div>
                    <div v-else>
                        {{ col.value }}
                    </div>
                </q-td>
            </q-tr>
            '''
        )

        def fetch_income_sources():
            """Fetch all income sources."""
            resp = requests.get(f"{API_URL}/income/")
            if resp.status_code == 200:
                return resp.json()
            return []

        def refresh_income():
            """Refresh income sources table."""
            income_sources = fetch_income_sources()
            accounts = fetch_accounts()
            account_map = {a["id"]: a["name"] for a in accounts}

            transactions_resp = requests.get(f"{API_URL}/transactions/")
            all_transactions = []
            if transactions_resp.status_code == 200:
                all_transactions = transactions_resp.json()

            today = datetime.datetime.now(timezone.utc)

            def is_income_due_soon(income):
                """Check if income is due within the next 3 days."""
                start_freq_str = income.get("start_freq")
                if not start_freq_str:
                    return False

                try:
                    start_freq = parse_date(start_freq_str)
                    if not start_freq:
                        return False
                    if start_freq.tzinfo is None:
                        start_freq = start_freq.replace(tzinfo=timezone.utc)
                except Exception:
                    return False

                frequency = income.get("frequency", "monthly")
                for days_ahead in range(0, 4):
                    check_date = today + timedelta(days=days_ahead)
                    days_since_start = (check_date.date() - start_freq.date()).days

                    if days_since_start < 0:
                        continue

                    is_due = False
                    if frequency == "daily":
                        is_due = True
                    elif frequency == "weekly":
                        is_due = (days_since_start % 7 == 0)
                    elif frequency == "biweekly":
                        is_due = (days_since_start % 14 == 0)
                    elif frequency == "semimonthly":
                        # Semimonthly: due on 1st and 15th of each month
                        is_due = check_date.day in (1, 15)
                    elif frequency == "monthly":
                        is_due = (check_date.day == start_freq.day)
                    elif frequency == "yearly":
                        is_due = (check_date.month == start_freq.month and check_date.day == start_freq.day)

                    if is_due:
                        return True
                return False

            def is_income_verified(income):
                """Check if income has been verified in the transaction log."""
                income_name = income.get("name", "")
                account_id = income.get("account_id")

                for txn in all_transactions:
                    if txn.get("account_id") == account_id:
                        note = txn.get("note", "")
                        if f"Income verified: {income_name}" in note or f"Deposit verified: {income_name}" in note:
                            occurred_at_str = txn.get("occurred_at")
                            if occurred_at_str:
                                try:
                                    occurred_at = parse_date(occurred_at_str)
                                    if occurred_at:
                                        if occurred_at.tzinfo is None:
                                            occurred_at = occurred_at.replace(tzinfo=timezone.utc)
                                        days_ago = (today - occurred_at).days
                                        if days_ago <= 3:
                                            return True
                                except Exception:
                                    pass
                return False

            rows = []
            for income in income_sources:
                if not income.get("deleted", False):
                    account_id = income.get("account_id")
                    account_name = account_map.get(account_id, "Unknown")

                    due_soon = is_income_due_soon(income)

                    if due_soon and is_income_verified(income):
                        due_soon = False

                    rows.append({
                        "id": income["id"],
                        "account_id": account_id,
                        "account_name": account_name,
                        "name": income.get("name", ""),
                        "description": income.get("description", ""),
                        "amount": f"${float(income.get('amount', 0.0)):,.2f}",
                        "frequency": income.get("frequency", ""),
                        "start_freq": income.get("start_freq", ""),
                        "enabled": income.get("enabled", True),
                        "due_soon": due_soon,
                    })

            income_table.rows = rows

        income_dialog = ui.dialog()
        with income_dialog, ui.card().classes("w-full max-w-lg"):
            income_title = ui.label("Add Income Source").classes("text-lg font-semibold")
            income_account_select = ui.select(label="Account", options=["Select account..."]).classes("w-full")
            income_name_input = ui.input(label="Income Name", placeholder="e.g., Salary")
            income_description_input = ui.input(label="Description (optional)", placeholder="e.g., Monthly salary")
            income_amount_input = ui.number(label="Amount", format="%.2f", value=0.0)
            income_frequency_select = ui.select(
                label="Frequency",
                options=["daily", "weekly", "biweekly", "semimonthly", "monthly", "yearly"],
                value="monthly"
            )

            income_start_freq_input = ui.input(label="Frequency Start Date", placeholder="Click to select date").classes("w-full")
            income_start_freq_picker = ui.date(mask="YYYY-MM-DD").props("dense outlined").classes("w-full hidden")

            def toggle_start_freq_picker():
                income_start_freq_picker.classes(toggle="hidden")

            income_start_freq_input.on("click", toggle_start_freq_picker)

            def on_start_freq_selected():
                if income_start_freq_picker.value:
                    date_str = income_start_freq_picker.value.isoformat() if hasattr(income_start_freq_picker.value, 'isoformat') else str(income_start_freq_picker.value)
                    income_start_freq_input.value = date_str
                    income_start_freq_picker.classes(add="hidden")

            income_start_freq_picker.on_value_change(on_start_freq_selected)

            def save_income():
                if not income_name_input.value or not income_account_select.value:
                    ui.notify("Name and Account are required", type="warning")
                    return

                if not income_start_freq_input.value:
                    ui.notify("Start Date is required", type="warning")
                    return

                account_id = None
                for acc in fetch_accounts():
                    if acc["name"] == income_account_select.value:
                        account_id = acc["id"]
                        break

                if not account_id:
                    ui.notify("Account not found", type="warning")
                    return

                amount = float(income_amount_input.value or 0.0)

                income_id = income_dialog.props.get("data-id")

                payload = {
                    "name": income_name_input.value,
                    "description": income_description_input.value or None,
                    "amount": amount,
                    "frequency": income_frequency_select.value,
                    "start_freq": income_start_freq_input.value,
                }

                if income_id:
                    resp = requests.patch(
                        f"{API_URL}/income/{income_id}",
                        json=payload,
                    )
                    if resp.status_code != 200:
                        ui.notify(handle_error(resp), type="negative")
                        return
                    ui.notify("Income source updated", type="positive")
                else:
                    resp = requests.post(
                        f"{API_URL}/income/?account_id={account_id}",
                        json=payload,
                    )
                    if resp.status_code != 201:
                        ui.notify(handle_error(resp), type="negative")
                        return
                    ui.notify("Income source created", type="positive")

                income_dialog.close()
                refresh_income()

            with ui.row().classes("gap-2 justify-end w-full mt-4"):
                ui.button("Cancel", on_click=income_dialog.close).props("flat color=grey")
                ui.button("Save", on_click=save_income).props("color=primary")

        def open_add_income():
            income_dialog.props["data-id"] = None
            income_title.text = "Add Income Source"
            accounts = fetch_accounts()
            account_options = [a["name"] for a in accounts if a.get("enabled", True)]
            income_account_select.options = account_options if account_options else ["No enabled accounts"]
            income_account_select.value = None
            income_account_select.update()
            income_name_input.value = ""
            income_description_input.value = ""
            income_amount_input.value = 0.0
            income_frequency_select.value = "monthly"
            income_start_freq_input.value = ""
            income_start_freq_picker.value = None
            income_start_freq_picker.classes(add="hidden")
            income_dialog.open()

        def open_edit_income(income):
            income_dialog.props["data-id"] = income.get("id")
            income_title.text = "Edit Income Source"
            accounts = fetch_accounts()
            account_options = [a["name"] for a in accounts if a.get("enabled", True)]
            income_account_select.options = account_options if account_options else ["No enabled accounts"]
            income_account_select.value = income.get("account_name")
            income_account_select.update()
            income_name_input.value = income.get("name", "")
            income_description_input.value = income.get("description", "")
            amount_str = income.get("amount", "$0.00").replace("$", "").replace(",", "")
            income_amount_input.value = float(amount_str) if amount_str else 0.0
            income_frequency_select.value = income.get("frequency", "monthly")
            if income.get("start_freq"):
                income_start_freq_input.value = income.get("start_freq")
            income_start_freq_picker.classes(add="hidden")
            income_dialog.open()

        def handle_edit_income(event):
            income = event.args
            open_edit_income(income)

        def handle_delete_income(event):
            income = event.args
            async def confirm_delete():
                resp = requests.delete(f"{API_URL}/income/{income['id']}")
                if resp.status_code != 204:
                    ui.notify(handle_error(resp), type="negative")
                    return
                ui.notify("Income source deleted", type="positive")
                refresh_income()

            ui.context_menu(lambda: [
                ui.menu_item("Confirm", on_click=confirm_delete)
            ]).open()

        def handle_verify_deposit(event):
            income = event.args
            income_id = income.get("id")
            account_id = income.get("account_id")
            amount = income.get("amount", "$0.00")

            amount_numeric = float(amount.replace("$", "").replace(",", "")) if isinstance(amount, str) else float(amount)

            funds_payload = {
                "amount": amount_numeric,
                "note": f"Income verified: {income.get('name', 'Income')}",
            }

            resp = requests.post(f"{API_URL}/accounts/{account_id}/add-funds", json=funds_payload)
            if resp.status_code != 200:
                ui.notify(handle_error(resp), type="negative")
                return

            ui.notify(f"Deposit verified and logged: ${amount_numeric:,.2f}", type="positive")
            refresh_income()
            if _refresh_dashboard_ref:
                _refresh_dashboard_ref[0]()
            if _refresh_transactions_ref:
                _refresh_transactions_ref[0]()

        income_table.on('verify-deposit', handle_verify_deposit)
        income_table.on('edit-income', handle_edit_income)
        income_table.on('delete-income', handle_delete_income)

        with ui.row().classes("items-center justify-start w-full mb-2 mt-4"):
            ui.button("Add Income Source", color="primary", on_click=open_add_income)

        refresh_income()
