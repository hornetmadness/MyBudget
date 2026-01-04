"""Transactions Module - Transaction History and Management UI

This module provides transaction viewing and filtering including:
- Complete transaction history display
- Transaction type filtering (deposit, withdrawal, transfer, payment)
- Account-based filtering
- Date range filtering
- Transaction details with source/destination tracking
- Real-time transaction updates
"""

import sys
from typing import Any, Dict, List
from pathlib import Path

# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import requests
from app.config import API_URL
from app.ui.utils import fetch_accounts, fetch_bills, fetch_transactions, fetch_budgetbills, parse_date, format_datetime, format_date


def build_transactions_tab(ui, requests, API_URL, _refresh_dashboard_ref, register_refresh_callback, format_currency, datetime, timezone, open_budget_bill_edit_dialog_global, _refresh_budget_bills_ref, _refresh_transactions_ref, *args):
    """Build the complete transactions tab UI with filtering and history.
    
    Creates:
        - Transaction history table
        - Filter controls (type, account, date range)
        - Lookup maps for account/bill name resolution
        - Real-time transaction display
        - Sortable columns for analysis
    
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
    # Create lookup maps for resolving IDs
    account_map = {}  # account_id -> name
    budgetbill_map = {}  # budgetbill_id -> bill name

    def refresh_lookup_maps():
        """Refresh ID to name lookup maps."""
        nonlocal account_map, budgetbill_map

        # Build account map
        accounts = fetch_accounts()
        account_map = {acc["id"]: acc["name"] for acc in accounts}

        # Build budgetbill map (budgetbill_id -> bill name)
        budgetbills = fetch_budgetbills()
        for bb in budgetbills:
            bill_id = bb.get("bill_id")
            if bill_id:
                # Fetch bill name
                bills = fetch_bills()
                bill = next((b for b in bills if b["id"] == bill_id), None)
                if bill:
                    budgetbill_map[bb["id"]] = bill["name"]

    # Pagination state
    page_size = 25
    current_page = {"value": 1}
    total_transactions = {"value": 0}
    search_term = {"value": ""}

    ui.label("Transactions").classes("text-2xl font-bold mb-4")

    # Search filter
    with ui.row().classes("items-center gap-4 mb-4 w-full"):
        search_input = ui.input(
            label="Search",
            placeholder="Search by account, bill, note, or amount..."
        ).classes("flex-1")

        def on_search():
            search_term["value"] = search_input.value.lower() if search_input.value else ""
            current_page["value"] = 1  # Reset to first page
            render_transactions()

        search_input.on("keydown.enter", on_search)
        ui.button("Search", icon="search", on_click=on_search).props("color=primary")
        ui.button("Clear", icon="clear", on_click=lambda: (search_input.set_value(""), on_search())).props("flat")

    # Table columns
    columns = [
        {"name": "occurred_at", "label": "Date", "field": "occurred_at", "sortable": True, "align": "left"},
        {"name": "account", "label": "Account", "field": "account", "sortable": True, "align": "left"},
        {"name": "type", "label": "Type", "field": "type", "sortable": True, "align": "left"},
        {"name": "amount", "label": "Amount", "field": "amount", "sortable": True, "align": "right"},
        {"name": "bill", "label": "Bill", "field": "bill", "sortable": False, "align": "left"},
        {"name": "note", "label": "Note", "field": "note", "sortable": False, "align": "left"},
        {"name": "actions", "label": "Actions", "field": "actions", "align": "center"},
    ]

    transactions_table = ui.table(
        columns=columns,
        rows=[],
        row_key="id",
        pagination={"rowsPerPage": page_size, "page": 1},
    ).classes("w-full")

    # Add custom slot for action buttons
    transactions_table.add_slot(
        'body-cell-actions',
        r'''
        <q-td :props="props">
            <q-btn v-if="props.row.has_budgetbill" flat dense round color="info" icon="info"
                   @click="$parent.$emit('view-budgetbill', props.row)">
                <q-tooltip>View Budget Bill Details</q-tooltip>
            </q-btn>
        </q-td>
        '''
    )

    # View budgetbill details dialog
    budgetbill_detail_dialog = ui.dialog()
    with budgetbill_detail_dialog, ui.card().classes("w-full max-w-lg"):
        budgetbill_detail_title = ui.label("Budget Bill Details").classes("text-lg font-semibold mb-4")

        budgetbill_detail_content = ui.column().classes("w-full")

        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Close", on_click=budgetbill_detail_dialog.close)

    def handle_view_budgetbill(event):
        txn = event.args
        budgetbill_id = txn.get("budgetbill_id")

        if not budgetbill_id:
            ui.notify("No budget bill associated with this transaction", type="warning")
            return

        # Fetch budgetbill details
        budgetbills = fetch_budgetbills()
        budgetbill = next((bb for bb in budgetbills if bb["id"] == budgetbill_id), None)

        if not budgetbill:
            ui.notify("Budget bill not found", type="warning")
            return

        # Clear previous content
        budgetbill_detail_content.clear()

        # Fetch bill name
        bill_id = budgetbill.get("bill_id")
        bill_name = "Unknown"
        if bill_id:
            bills = fetch_bills()
            bill = next((b for b in bills if b["id"] == bill_id), None)
            if bill:
                bill_name = bill.get("name", "Unknown")

        # Update title and display details
        budgetbill_detail_title.text = f"Budget Bill: {bill_name}"

        with budgetbill_detail_content:
            ui.label(f"Amount Budgeted: ${budgetbill.get('budgeted_amount', 0.0):,.2f}").classes("mb-2")
            ui.label(f"Amount Paid: ${budgetbill.get('paid_amount', 0.0):,.2f}").classes("mb-2")

            due_date = budgetbill.get("due_date")
            if due_date:
                parsed_due = parse_date(due_date)
                due_str = format_date(parsed_due) if parsed_due else due_date
                ui.label(f"Due Date: {due_str}").classes("mb-2")

            paid_on = budgetbill.get("paid_on")
            if paid_on:
                parsed_paid = parse_date(paid_on)
                paid_str = format_date(parsed_paid) if parsed_paid else paid_on
                ui.label(f"Paid On: {paid_str}").classes("mb-2")

            note = budgetbill.get("note")
            if note:
                ui.label(f"Note: {note}").classes("mb-2")

        budgetbill_detail_dialog.open()

    transactions_table.on('view-budgetbill', handle_view_budgetbill)

    # Pagination controls
    with ui.row().classes("items-center gap-4 mt-4"):
        prev_btn = ui.button("Previous", icon="arrow_back").props("flat")
        page_label = ui.label("")
        next_btn = ui.button("Next", icon="arrow_forward").props("flat")

    def render_transactions():
        """Fetch and render transactions with ID resolution."""
        refresh_lookup_maps()
        transactions = fetch_transactions()

        # Sort by occurred_at descending (most recent first)
        transactions.sort(key=lambda t: t.get("occurred_at", ""), reverse=True)

        # Apply search filter
        filtered_transactions = transactions
        if search_term["value"]:
            filtered_transactions = []
            for txn in transactions:
                # Get searchable fields
                account_id = txn.get("account_id")
                account_name = account_map.get(account_id, "").lower()

                budgetbill_id = txn.get("budgetbill_id")
                bill_name = budgetbill_map.get(budgetbill_id, "").lower() if budgetbill_id else ""

                note_val = (txn.get("note") or "").lower()
                amount_str = str(txn.get("amount", ""))
                txn_type = (txn.get("transaction_type") or "").lower()

                # Check if search term matches any field
                if (search_term["value"] in account_name or
                    search_term["value"] in bill_name or
                    search_term["value"] in note_val or
                    search_term["value"] in amount_str or
                    search_term["value"] in txn_type):
                    filtered_transactions.append(txn)

        total_transactions["value"] = len(filtered_transactions)

        # Paginate
        start_idx = (current_page["value"] - 1) * page_size
        end_idx = start_idx + page_size
        page_transactions = filtered_transactions[start_idx:end_idx]

        # Resolve IDs and format data
        rows = []
        for txn in page_transactions:
            # Resolve account name
            account_id = txn.get("account_id")
            account_name = account_map.get(account_id, f"Unknown ({account_id[:8]}...)" if account_id else "Unknown")

            # Resolve budgetbill to bill name
            budgetbill_id = txn.get("budgetbill_id")
            bill_name = budgetbill_map.get(budgetbill_id, "") if budgetbill_id else "-"

            # Format date
            occurred_at = parse_date(txn.get("occurred_at"))
            date_str = format_datetime(occurred_at) if occurred_at else "N/A"

            # Format amount with type indicator
            txn_type = txn.get("transaction_type", "")
            amount = txn.get("amount", 0.0)
            budgetbill_id = txn.get("budgetbill_id")

            rows.append({
                "id": txn.get("id"),
                "occurred_at": date_str,
                "account": account_name,
                "type": txn_type.capitalize(),
                "amount": f"${amount:,.2f}",
                "bill": bill_name,
                "note": txn.get("note", ""),
                "budgetbill_id": budgetbill_id,
                "has_budgetbill": bool(budgetbill_id),
            })

        transactions_table.rows = rows

        # Update pagination display
        total_pages = (total_transactions["value"] + page_size - 1) // page_size
        page_label.text = f"Page {current_page['value']} of {total_pages} ({total_transactions['value']} total)"
        prev_btn.set_enabled(current_page["value"] > 1)
        next_btn.set_enabled(current_page["value"] < total_pages)

    def go_to_prev_page():
        if current_page["value"] > 1:
            current_page["value"] -= 1
            render_transactions()

    def go_to_next_page():
        total_pages = (total_transactions["value"] + page_size - 1) // page_size
        if current_page["value"] < total_pages:
            current_page["value"] += 1
            render_transactions()

    prev_btn.on_click(go_to_prev_page)
    next_btn.on_click(go_to_next_page)

    # Store reference for access from other tabs
    _refresh_transactions_ref.append(render_transactions)

    # Register refresh callback and initial render
    register_refresh_callback(render_transactions)
    render_transactions()
