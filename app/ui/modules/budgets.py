"""Budgets Module - Budget Management UI

This module provides comprehensive budget management including:
- Budget creation with start/end dates
- Budget comparison and analysis
- Bill-to-budget associations (budget bills)
- Payment tracking and status management
- Budget cloning from templates
- Spending analysis and overages
- Budget archival and history
"""

from typing import Any, Dict
import datetime
import app.ui.utils as ui_utils
from datetime import timedelta
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.ui.utils import handle_error, parse_date, fetch_bills, fetch_accounts, get_payment_method_label, format_datetime, format_date, app_settings


def build_budgets_tab(ui, requests, API_URL, _refresh_dashboard_ref, register_refresh_callback, format_currency, datetime, timezone, open_budget_bill_edit_dialog_global, _refresh_budget_bills_ref, _refresh_transactions_ref, *args):
    """Build the complete budgets tab UI with all budget management features.
    
    Creates:
        - Create budget dialog with date pickers and template selection
        - Budget selector and management interface
        - Budget bills table with add/edit/delete/mark-paid functionality
        - Payment status tracking
        - Spending analysis and overage warnings
        - Budget deletion with confirmation
    
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
        create_budget_btn = ui.button("Create Budget", color="primary")

    create_budget_dialog = ui.dialog()
    with create_budget_dialog, ui.card().classes("w-full max-w-xl"):
            ui.label("Create Budget").classes("text-lg font-semibold")

            budget_name_input = ui.input(label="Budget Name", placeholder="January 2025 Budget")
            budget_start_date_input = ui.input(label="Start Date", placeholder="Click to select date")
            budget_start_date_picker = ui.date(mask="YYYY-MM-DD").props("dense outlined").classes("hidden")

            def toggle_budget_start_date_picker():
                budget_start_date_picker.classes(toggle="hidden")

            budget_start_date_input.on("click", toggle_budget_start_date_picker)

            def on_budget_start_date_selected():
                if budget_start_date_picker.value:
                    date_str = budget_start_date_picker.value.isoformat() if hasattr(budget_start_date_picker.value, 'isoformat') else str(budget_start_date_picker.value)
                    budget_start_date_input.value = date_str
                    budget_start_date_picker.classes(add="hidden")

            budget_start_date_picker.on_value_change(on_budget_start_date_selected)

            budget_end_date_input = ui.input(label="End Date", placeholder="Click to select date")
            budget_end_date_picker = ui.date(mask="YYYY-MM-DD").props("dense outlined").classes("hidden")

            def toggle_budget_end_date_picker():
                budget_end_date_picker.classes(toggle="hidden")

            budget_end_date_input.on("click", toggle_budget_end_date_picker)

            def on_budget_end_date_selected():
                if budget_end_date_picker.value:
                    date_str = budget_end_date_picker.value.isoformat() if hasattr(budget_end_date_picker.value, 'isoformat') else str(budget_end_date_picker.value)
                    budget_end_date_input.value = date_str
                    budget_end_date_picker.classes(add="hidden")

            budget_end_date_picker.on_value_change(on_budget_end_date_selected)

            budget_description_input = ui.input(label="Description (optional)")

            def create_budget_submit():
                if not budget_name_input.value:
                    ui.notify("Budget name is required", type="warning")
                    return

                start_date = None
                if budget_start_date_input.value:
                    start_date = f"{budget_start_date_input.value}T00:00:00Z"

                end_date = None
                if budget_end_date_input.value:
                    end_date = f"{budget_end_date_input.value}T23:59:59Z"

                payload = {
                    "name": budget_name_input.value,
                    "description": budget_description_input.value or None,
                }
                if start_date:
                    payload["start_date"] = start_date
                if end_date:
                    payload["end_date"] = end_date

                resp = requests.post(
                    f"{API_URL}/budgets/",
                    json=payload,
                )
                if resp.status_code != 200:
                    ui.notify(handle_error(resp), type="negative")
                    return

                ui.notify("Budget created", type="positive")
                budget_name_input.value = ""
                budget_start_date_input.value = None
                budget_end_date_input.value = None
                budget_description_input.value = ""
                create_budget_dialog.close()
                refresh_budgets()

            with ui.row().classes("gap-2 justify-end w-full mt-2"):
                ui.button("Cancel", on_click=create_budget_dialog.close).props("flat color=grey")
                ui.button("Create", on_click=create_budget_submit).props("color=primary")

    # Create chart container immediately after create button
    chart_container = ui.column().classes("w-full max-w-4xl mb-4")

    def update_chart():
        chart_container.clear()
        with chart_container:
            try:
                fig = render_projected_balance_chart()
                if fig:
                    ui.plotly(fig).classes("w-full")
            except Exception as e:
                ui.label(f"Error rendering chart: {e}").classes("text-red-600")

    clone_budget_dialog = ui.dialog()
    with clone_budget_dialog, ui.card().classes("w-full max-w-xl"):
        ui.label("Clone Budget").classes("text-lg font-semibold")

        clone_budget_name_input = ui.input(label="Budget Name", placeholder="Cloned Budget")
        clone_budget_start_input = ui.input(label="Start Date", placeholder="Click to select date")
        clone_budget_start_picker = ui.date(mask="YYYY-MM-DD").props("dense outlined").classes("hidden")

        def toggle_clone_start_picker():
            clone_budget_start_picker.classes(toggle="hidden")

        clone_budget_start_input.on("click", toggle_clone_start_picker)

        def on_clone_start_selected():
            if clone_budget_start_picker.value:
                date_str = clone_budget_start_picker.value.isoformat() if hasattr(clone_budget_start_picker.value, 'isoformat') else str(clone_budget_start_picker.value)
                clone_budget_start_input.value = date_str
                clone_budget_start_picker.classes(add="hidden")

        clone_budget_start_picker.on_value_change(on_clone_start_selected)

        clone_budget_end_input = ui.input(label="End Date", placeholder="Click to select date")
        clone_budget_end_picker = ui.date(mask="YYYY-MM-DD").props("dense outlined").classes("hidden")

        def toggle_clone_end_picker():
            clone_budget_end_picker.classes(toggle="hidden")

        clone_budget_end_input.on("click", toggle_clone_end_picker)

        def on_clone_end_selected():
            if clone_budget_end_picker.value:
                date_str = clone_budget_end_picker.value.isoformat() if hasattr(clone_budget_end_picker.value, 'isoformat') else str(clone_budget_end_picker.value)
                clone_budget_end_input.value = date_str
                clone_budget_end_picker.classes(add="hidden")

        clone_budget_end_picker.on_value_change(on_clone_end_selected)

        clone_budget_description_input = ui.input(label="Description (optional)")

        def clone_budget_submit():
            source_id = clone_budget_dialog.props.get("source-id")
            if not source_id:
                ui.notify("No budget selected to clone", type="warning")
                return
            if not clone_budget_name_input.value:
                ui.notify("Budget name is required", type="warning")
                return
            if not clone_budget_start_input.value or not clone_budget_end_input.value:
                ui.notify("Start and End dates are required", type="warning")
                return

            start_date = f"{clone_budget_start_input.value}T00:00:00Z"
            end_date = f"{clone_budget_end_input.value}T23:59:59Z"

            payload = {
                "name": clone_budget_name_input.value,
                "description": clone_budget_description_input.value or None,
                "start_date": start_date,
                "end_date": end_date,
            }

            resp = requests.post(f"{API_URL}/budgets/", json=payload)
            if resp.status_code != 200:
                ui.notify(handle_error(resp), type="negative")
                return

            new_budget = resp.json()
            new_budget_id = new_budget.get("id")
            if not new_budget_id:
                ui.notify("Failed to create cloned budget", type="negative")
                return

            # Copy bills from source budget
            bb_resp = requests.get(f"{API_URL}/budgets/{source_id}/bills")
            if bb_resp.status_code != 200:
                ui.notify(handle_error(bb_resp), type="negative")
                return

            budget_bills = bb_resp.json()
            all_bills = fetch_bills()
            bill_lookup = {str(b.get("id")): b for b in all_bills}
            failed_bills = []
            for bb in budget_bills:
                bill_id_str = str(bb.get("bill_id"))
                bill_payload = {
                    "bill_id": bill_id_str,
                    "account_id": str(bb.get("account_id", "")),
                }
                if bb.get("budgeted_amount") is not None:
                    bill_payload["budgeted_amount"] = float(bb.get("budgeted_amount", 0.0))

                add_resp = requests.post(
                    f"{API_URL}/budgets/{new_budget_id}/bills",
                    json=bill_payload,
                )
                if add_resp.status_code != 200:
                    bill_name = bill_lookup.get(bill_id_str, {}).get("name", "Bill")
                    try:
                        detail = add_resp.json().get("detail", str(add_resp.status_code))
                    except Exception:
                        detail = str(add_resp.status_code)
                    failed_bills.append(f"'{bill_name}' ({detail})")
                    continue

            if failed_bills:
                ui.notify(f"Budget cloned. Failed to copy: {', '.join(failed_bills)}", type="warning")
            else:
                ui.notify("Budget cloned", type="positive")
            clone_budget_name_input.value = ""
            clone_budget_start_input.value = None
            clone_budget_end_input.value = None
            clone_budget_description_input.value = ""
            clone_budget_dialog.close()
            refresh_budgets()

        with ui.row().classes("gap-2 justify-end w-full mt-2"):
            ui.button("Cancel", on_click=clone_budget_dialog.close).props("flat color=grey")
            ui.button("Clone", on_click=clone_budget_submit).props("color=primary")

    def open_create_budget_dialog():
        today = ui_utils.datetime.datetime.now(ui_utils.datetime.timezone.utc).date()
        start_str = ui_utils.format_date(ui_utils.datetime.datetime.combine(today, ui_utils.datetime.datetime.min.time()))
        end_str = ui_utils.format_date(ui_utils.datetime.datetime.combine(today + timedelta(days=15), ui_utils.datetime.datetime.min.time()))
        budget_name_input.value = ""
        budget_description_input.value = ""
        budget_start_date_input.value = start_str
        budget_end_date_input.value = end_str
        budget_start_date_picker.value = start_str
        budget_end_date_picker.value = end_str
        create_budget_dialog.open()

    def open_clone_budget_dialog(budget: Dict[str, Any]):
        clone_budget_dialog.props["source-id"] = budget.get("id")
        base_name = budget.get("name", "Budget")
        clone_budget_name_input.value = f"{base_name} Copy"

        start_raw = budget.get("start_date")
        end_raw = budget.get("end_date_raw") or budget.get("end_date")
        start_dt = parse_date(start_raw)
        end_dt = parse_date(end_raw)

        today = datetime.now(timezone.utc).date()
        default_start = start_dt.date() if start_dt else today
        default_end = end_dt.date() if end_dt else (today + timedelta(days=15))

        clone_budget_start_input.value = default_start.isoformat()
        clone_budget_start_picker.value = default_start.isoformat()
        clone_budget_end_input.value = default_end.isoformat()
        clone_budget_end_picker.value = default_end.isoformat()
        clone_budget_description_input.value = budget.get("description", "")

        clone_budget_dialog.open()

    create_budget_btn.on_click(open_create_budget_dialog)

    # Projected balance graph at the top
    
    def render_projected_balance_chart():
        """Render a chart showing projected account balances over time."""
        # Fetch accounts
        accounts_resp = requests.get(f"{API_URL}/accounts/")
        if accounts_resp.status_code != 200:
            return

        all_accounts = accounts_resp.json()
        active_accounts = [a for a in all_accounts if a.get("enabled", True)]

        if not active_accounts:
            return

        # Fetch budgets
        budgets_resp = requests.get(f"{API_URL}/budgets/")
        if budgets_resp.status_code != 200:
            return

        budgets = budgets_resp.json()

        # Fetch income sources
        income_resp = requests.get(f"{API_URL}/income/")
        income_sources = []
        if income_resp.status_code == 200:
            income_sources = [inc for inc in income_resp.json() if not inc.get("deleted", False) and inc.get("enabled", True)]

        # Get all bills for all budgets
        budget_bills_map = {}  # budget_id -> [bills]
        for budget in budgets:
            bb_resp = requests.get(f"{API_URL}/budgets/{budget['id']}/bills")
            if bb_resp.status_code == 200:
                budget_bills_map[budget['id']] = bb_resp.json()

        # Calculate projected balances over current and next month
        import plotly.graph_objects as go
        from datetime import timedelta

        today = datetime.datetime.now(timezone.utc)
        date_range = []
        
        # Calculate total days across all active budgets and find earliest start date
        active_budgets = [b for b in budgets if b.get("enabled", True)]
        total_days = 0
        earliest_start = None
        
        for budget in active_budgets:
            budget_start = parse_date(budget.get("start_date"))
            budget_end = parse_date(budget.get("end_date"))
            
            # Ensure datetimes are timezone-aware for comparison
            if budget_start and budget_start.tzinfo is None:
                budget_start = budget_start.replace(tzinfo=timezone.utc)
            if budget_end and budget_end.tzinfo is None:
                budget_end = budget_end.replace(tzinfo=timezone.utc)
            
            if budget_start and budget_end:
                days_in_budget = (budget_end - budget_start).days
                total_days += days_in_budget
                # Track earliest start date
                if earliest_start is None or budget_start < earliest_start:
                    earliest_start = budget_start
        
        # Start projection from earliest budget start date, or yesterday if no active budgets
        if earliest_start:
            current = earliest_start.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            current = today.replace(hour=0, minute=0, second=0, microsecond=0)
            current = current - timedelta(days=1)
        
        # Use total days or fallback to 60 days from today
        projection_days = total_days if total_days > 0 else 60
        end_date = current + timedelta(days=projection_days)

        while current <= end_date:
            date_range.append(current)
            current += timedelta(days=1)

        # Helper function to calculate income occurrences
        def calculate_income_on_date(income, date):
            """Calculate if income occurs on a given date based on frequency and start_freq."""
            if not income.get("enabled", True):
                return 0.0

            start_freq_str = income.get("start_freq")
            if not start_freq_str:
                return 0.0

            try:
                start_freq = parse_date(start_freq_str)
                if not start_freq:
                    return 0.0
                # Ensure start_freq is timezone-aware
                if start_freq.tzinfo is None:
                    start_freq = start_freq.replace(tzinfo=timezone.utc)
            except Exception:
                return 0.0

            # Only count if date is on or after start date
            if date < start_freq:
                return 0.0

            frequency = income.get("frequency", "monthly")
            days_since_start = (date.date() - start_freq.date()).days

            if frequency == "daily":
                return float(income.get("amount", 0.0))
            elif frequency == "weekly":
                if days_since_start % 7 == 0:
                    return float(income.get("amount", 0.0))
            elif frequency == "biweekly":
                if days_since_start % 14 == 0:
                    return float(income.get("amount", 0.0))
            elif frequency == "semimonthly":
                # Semimonthly: occurs on 1st and 15th of each month
                if date.day in (1, 15):
                    return float(income.get("amount", 0.0))
                return 0.0
            elif frequency == "monthly":
                # Same day each month
                if date.day == start_freq.day:
                    return float(income.get("amount", 0.0))
            elif frequency == "yearly":
                # Same day each year
                if date.month == start_freq.month and date.day == start_freq.day:
                    return float(income.get("amount", 0.0))

            return 0.0

        # Build projection for each active account
        fig = go.Figure()

        for account in active_accounts:
            account_id = account["id"]
            account_name = account["name"]
            starting_balance = float(account.get("balance", 0.0))

            balances = []
            current_balance = starting_balance

            for date in date_range:
                # Find bills due on this date
                daily_outflow = 0.0
                daily_inflow = 0.0

                for budget in budgets:
                    budget_bills = budget_bills_map.get(budget['id'], [])
                    for bb in budget_bills:
                        # Use paid_on date and paid_amount if paid, otherwise due_date and budgeted_amount
                        date_to_check = parse_date(bb.get("paid_on")) if bb.get("paid_on") else parse_date(bb.get("due_date"))
                        amount = float(bb.get("paid_amount", 0.0)) if bb.get("paid_on") else float(bb.get("budgeted_amount", 0.0))
                        
                        if date_to_check and date_to_check.date() == date.date() and amount > 0:
                            # Check if this is a transfer bill (has transfer_account_id)
                            transfer_account_id = bb.get("transfer_account_id")
                            
                            # Deduct from source account
                            if str(bb.get("account_id")) == str(account_id):
                                daily_outflow += amount
                            
                            # Add to destination account (transfer)
                            if transfer_account_id and str(transfer_account_id) == str(account_id):
                                daily_inflow += amount

                # Add income for this account
                for income in income_sources:
                    if str(income.get("account_id")) == str(account_id):
                        daily_inflow += calculate_income_on_date(income, date)

                # Update balance
                current_balance = current_balance + daily_inflow - daily_outflow
                balances.append(current_balance)

            # Add trace to figure
            fig.add_trace(go.Scatter(
                x=[d.strftime("%Y-%m-%d") for d in date_range],
                y=balances,
                mode='lines',
                name=account_name,
                line=dict(width=2)
            ))

        # Update layout
        fig.update_layout(
            title="Projected Account Balances",
            xaxis_title="Date",
            yaxis_title="Balance ($)",
            hovermode='x unified',
            height=250,
            template='plotly_white',
            margin=dict(l=40, r=40, t=40, b=40)
        )

        return fig

    with ui.card().classes("w-full max-w-4xl"):
        with ui.row().classes("items-center justify-between w-full mb-2"):
            ui.label("Budgets").classes("text-lg font-semibold")
            with ui.row().classes("items-center gap-2"):
                ui.label("Show all active budgets").classes("text-sm")
                show_all_budgets_toggle = ui.switch(value=True)

        budgets_table = ui.table(
            columns=[
                {"name": "name", "label": "Name", "field": "name", "sortable": True},
                {"name": "month", "label": "Month", "field": "month", "sortable": True},
                {"name": "year", "label": "Year", "field": "year", "sortable": True},
                {"name": "end_date", "label": "End Date", "field": "end_date", "sortable": True},
                {"name": "bills", "label": "Bills", "field": "bills", "align": "center", "sortable": True},
                {"name": "total", "label": "Total Budget", "field": "total", "align": "right", "sortable": True},
                {"name": "actions", "label": "Actions", "field": "actions", "align": "center"},
            ],
            rows=[],
            row_key="id",
        ).classes("w-full")

        # Add row styling for current budget
        budgets_table.add_slot(
            'body',
            r'''
            <q-tr :props="props" :class="{'bg-green-1': props.row.is_current}">
                <q-td v-for="col in props.cols" :key="col.name" :props="props">
                    <div v-if="col.name === 'name'">
                        <q-btn flat dense no-caps :color="props.row.enabled ? 'primary' : 'orange-8'" :label="props.row.name"
                               @click="$parent.$emit('manage-budget', props.row)"
                               class="text-left"
                               :style="{opacity: props.row.enabled ? 1 : 0.6}">
                        </q-btn>
                    </div>
                    <div v-else-if="col.name === 'actions'">
                        <q-btn flat dense round color="primary" icon="settings"
                               @click="$parent.$emit('manage-budget', props.row)">
                            <q-tooltip>Manage Budget</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round color="secondary" icon="content_copy" class="q-ml-sm"
                               @click="$parent.$emit('clone-budget', props.row)">
                            <q-tooltip>Clone Budget</q-tooltip>
                        </q-btn>
                        <q-btn flat dense round color="accent" icon="receipt" class="q-ml-sm"
                               @click="$parent.$emit('view-transactions', props.row)">
                            <q-tooltip>View Transactions</q-tooltip>
                        </q-btn>
                    </div>
                    <div v-else>
                        {{ col.value }}
                    </div>
                </q-td>
            </q-tr>
            '''
        )

        def handle_manage_budget(event):
            budget = event.args
            open_budget_manage(budget)

        budgets_table.on('manage-budget', handle_manage_budget)

        def handle_clone_budget(event):
            budget = event.args
            open_clone_budget_dialog(budget)

        budgets_table.on('clone-budget', handle_clone_budget)

        # View transactions dialog
        view_transactions_dialog = ui.dialog()
        with view_transactions_dialog, ui.card().classes("w-full max-w-4xl"):
            view_txn_title = ui.label("Transactions for Budget").classes("text-lg font-semibold mb-4")

            view_txn_columns = [
                {"name": "occurred_at", "label": "Date", "field": "occurred_at", "sortable": True, "align": "left"},
                {"name": "account", "label": "Account", "field": "account", "sortable": True, "align": "left"},
                {"name": "type", "label": "Type", "field": "type", "sortable": True, "align": "left"},
                {"name": "bill", "label": "Bill", "field": "bill", "sortable": True, "align": "left"},
                {"name": "amount", "label": "Amount", "field": "amount", "sortable": True, "align": "right"},
                {"name": "note", "label": "Note", "field": "note", "sortable": False, "align": "left"},
            ]

            view_txn_table = ui.table(
                columns=view_txn_columns,
                rows=[],
                row_key="id",
            ).classes("w-full")

            with ui.row().classes("justify-end mt-4"):
                ui.button("Close", on_click=view_transactions_dialog.close)

        def handle_view_transactions(event):
            budget = event.args
            budget_id = budget.get("id")
            budget_name = budget.get("name", "Budget")
            view_txn_title.text = f"Transactions for: {budget_name}"

            # Get all budgetbills for this budget
            bb_resp = requests.get(f"{API_URL}/budgets/{budget_id}/bills")
            if bb_resp.status_code != 200:
                view_txn_table.rows = []
                view_transactions_dialog.open()
                return

            budgetbills = bb_resp.json()
            budgetbill_ids = [bb["id"] for bb in budgetbills]

            if not budgetbill_ids:
                view_txn_table.rows = []
                view_transactions_dialog.open()
                return

            # Get all transactions
            txn_resp = requests.get(f"{API_URL}/transactions/")
            if txn_resp.status_code != 200:
                view_txn_table.rows = []
                view_transactions_dialog.open()
                return

            transactions = txn_resp.json()

            # Filter transactions by budgetbill_ids
            budget_transactions = [
                txn for txn in transactions 
                if txn.get("budgetbill_id") in budgetbill_ids
            ]

            # Build lookup maps
            accounts = fetch_accounts()
            account_map = {acc["id"]: acc["name"] for acc in accounts}

            bills = fetch_bills()
            bill_map = {}
            for bb in budgetbills:
                bill_id = bb.get("bill_id")
                if bill_id:
                    bill = next((b for b in bills if b["id"] == bill_id), None)
                    if bill:
                        bill_map[bb["id"]] = bill["name"]

            # Format rows
            rows = []
            for txn in budget_transactions:
                occurred_at = parse_date(txn.get("occurred_at"))
                date_str = format_datetime(occurred_at) if occurred_at else "N/A"

                account_id = txn.get("account_id")
                account_name = account_map.get(account_id, f"Unknown ({account_id[:8]}...)" if account_id else "Unknown")

                budgetbill_id = txn.get("budgetbill_id")
                bill_name = bill_map.get(budgetbill_id, "-")

                amount = txn.get("amount", 0.0)
                txn_type = txn.get("transaction_type", "").capitalize()

                rows.append({
                    "id": txn.get("id"),
                    "occurred_at": date_str,
                    "occurred_at_datetime": occurred_at,  # Store datetime for sorting
                    "account": account_name,
                    "type": txn_type,
                    "bill": bill_name,
                    "amount": f"${amount:,.2f}",
                    "note": txn.get("note", ""),
                })

            # Sort by datetime descending (most recent first)
            rows.sort(key=lambda r: r["occurred_at_datetime"] if r["occurred_at_datetime"] else datetime.min, reverse=True)

            view_txn_table.rows = rows
            view_transactions_dialog.open()

        budgets_table.on('view-transactions', handle_view_transactions)

        # Budget management dialog
        budget_manage_container = ui.column().classes("w-full max-w-4xl gap-4 hidden")

        with budget_manage_container:
            with ui.row().classes("items-center justify-between w-full mb-2"):
                budget_manage_title = ui.label("Manage Budget").classes("text-2xl font-semibold")
                ui.button("Back to Budgets", on_click=lambda: (budget_manage_container.classes(add="hidden"), refresh_budgets())).props("flat")


            budget_description_label = ui.label("").classes("text-sm text-gray-600 mb-2")
            with ui.row().classes("items-center gap-4"):
                budget_start_label = ui.label("Start: -").classes("text-md")
                budget_end_label = ui.label("End: -").classes("text-md")

            with ui.row().classes("items-center gap-4 mb-4"):
                budget_total_label = ui.label("Total Budget: $0.00").classes("text-md text-blue-600 font-semibold")
                budget_total_paid_label = ui.label("Total Paid: $0.00").classes("text-md text-green-600 font-semibold")
                budget_total_unpaid_label = ui.label("Total Unpaid Balance: $0.00").classes("text-md text-purple-700 font-semibold")
                budget_delta_label = ui.label("Over/Under Budget: $0.00").classes("text-md font-semibold")

            budget_account_breakdown_container = ui.column().classes("gap-1 mt-2 w-full")

            with ui.card().classes("w-full"):
                ui.label("Add Bill to Budget").classes("text-md font-semibold mb-2")
                with ui.row().classes("items-center gap-2 w-full"):
                    budget_bill_select = ui.select(
                        options=[],
                        label="Select Bill",
                    ).classes("flex-grow")
                    budget_bill_amount = ui.number(
                        label="Amount",
                        format="%.2f",
                        value=None,
                    ).props("dense")

                    def add_bill_to_budget():
                        budget_id = getattr(budget_manage_container, '_budget_id', None)
                        if not budget_id or not budget_bill_select.value:
                            ui.notify("Please select a bill", type="warning")
                            return

                        # Convert bill name to ID and get account_id
                        all_bills = fetch_bills()
                        selected_bill = next((b for b in all_bills if b["name"] == budget_bill_select.value), None)
                        if not selected_bill:
                            ui.notify("Bill not found", type="warning")
                            return

                        bill_id = str(selected_bill["id"])
                        account_id = str(selected_bill.get("account_id", ""))

                        payload = {
                            "bill_id": bill_id,
                            "account_id": account_id,
                        }
                        amt = budget_bill_amount.value
                        if amt is None or float(amt) == 0:
                            default_amt = selected_bill.get("budgeted_amount")
                            if default_amt is not None:
                                payload["budgeted_amount"] = float(default_amt)
                        else:
                            payload["budgeted_amount"] = float(amt)

                        resp = requests.post(
                            f"{API_URL}/budgets/{budget_id}/bills",
                            json=payload,
                        )
                        if resp.status_code != 200:
                            ui.notify(handle_error(resp), type="negative")
                            return

                        ui.notify("Bill added to budget", type="positive")
                        refresh_budget_bills(budget_id)

                    ui.button("Add", on_click=add_bill_to_budget).props("dense color=primary")

            ui.separator().classes("my-4")
            ui.label("Bills in Budget").classes("text-md font-semibold")

            budget_bills_container = ui.column().classes("gap-2 w-full")

            def refresh_budget_bills(budget_id: str):
                resp = requests.get(f"{API_URL}/budgets/{budget_id}/bills")
                if resp.status_code != 200:
                    budget_bills_container.clear()
                    with budget_bills_container:
                        ui.label("No bills in this budget")
                    budget_total_label.text = "Total Budget: $0.00"
                    budget_total_paid_label.text = "Total Paid: $0.00"
                    budget_total_unpaid_label.text = "Total Unpaid Balance: $0.00"
                    budget_delta_label.text = "Under Budget: $0.00"
                    budget_delta_label.classes(remove="text-red-600 text-black")
                    budget_delta_label.classes(add="text-black")
                    delete_budget_btn.classes(add="hidden")
                    return

                budget_bills = resp.json()

                if budget_bills:
                    delete_budget_btn.classes(add="hidden")
                else:
                    delete_budget_btn.classes(remove="hidden")

                # Update total budget, total paid, and total unpaid labels
                total_budget = sum(float(bb["budgeted_amount"]) for bb in budget_bills)
                total_paid = sum(float(bb["paid_amount"]) for bb in budget_bills if bb.get("paid_on") and bb.get("paid_amount") > 0)
                total_unpaid = sum(
                    float(bb["budgeted_amount"]) - (float(bb.get("paid_amount", 0.0)) if bb.get("paid_on") else 0.0)
                    for bb in budget_bills
                )
                budget_total_label.text = f"Total Budget: {format_currency(total_budget)}"
                budget_total_paid_label.text = f"Total Paid: {format_currency(total_paid)}"
                budget_total_unpaid_label.text = f"Total Unpaid Balance: {format_currency(total_unpaid)}"

                # Update delta (over/under budget) using total_paid and total_unpaid
                delta = total_paid - (total_paid + total_unpaid)
                delta_text = f"Over Budget: {format_currency(-delta)}" if delta < 0 else f"Under Budget: {format_currency(delta)}"
                budget_delta_label.text = delta_text
                budget_delta_label.classes(remove="text-red-600 text-black")
                if delta < 0:
                    budget_delta_label.classes(add="text-red-600")
                else:
                    budget_delta_label.classes(add="text-black")

                # Get all bills to map IDs to names
                all_bills = fetch_bills()
                bill_map = {str(b["id"]): b for b in all_bills}

                # Update available bills dropdown
                bills_in_budget = {str(bb["bill_id"]) for bb in budget_bills}
                available_bills = [b for b in all_bills if str(b["id"]) not in bills_in_budget]
                budget_bill_select.options = [b["name"] for b in available_bills]
                budget_bill_select.update()
                budget_bill_amount.value = 0.0

                # Get accounts for bank names and balances
                accounts = fetch_accounts()
                account_map = {str(a["id"]): a["name"] for a in accounts}
                account_balance_map = {str(a["id"]): float(a.get("balance", 0.0)) for a in accounts}

                # Update account breakdown - calculate both paid and unpaid amounts per account
                budget_account_breakdown_container.clear()
                account_paid_totals = {}
                account_budgeted_totals = {}

                for bb in budget_bills:
                    account_id = str(bb.get("account_id", ""))
                    account_name = account_map.get(account_id, "Unknown")

                    # Track total budgeted amount per account
                    budgeted_amt = float(bb.get("budgeted_amount", 0.0))
                    account_budgeted_totals[account_id] = account_budgeted_totals.get(account_id, 0.0) + budgeted_amt

                    # Track paid amounts
                    if bb.get("paid_on") and bb.get("paid_amount", 0.0) > 0:
                        paid_amt = float(bb.get("paid_amount", 0.0))
                        account_paid_totals[account_id] = account_paid_totals.get(account_id, 0.0) + paid_amt

                with budget_account_breakdown_container:
                    # Collect all accounts involved
                    all_account_ids = set(account_budgeted_totals.keys())

                    if all_account_ids:
                        ui.label("Account Impact:").classes("text-sm font-semibold text-gray-700 mt-1 mb-2")
                        for account_id in sorted(all_account_ids, key=lambda aid: account_map.get(aid, "Unknown")):
                            account_name = account_map.get(account_id, "Unknown")
                            paid_amount = account_paid_totals.get(account_id, 0.0)
                            budgeted_amount = account_budgeted_totals.get(account_id, 0.0)
                            current_balance = account_balance_map.get(account_id, 0.0)

                            # Calculate what balance would be if all bills were fully paid
                            # Current balance already has paid_amount deducted, so add it back to get original
                            # Then subtract total budgeted to see final balance
                            original_balance = current_balance + paid_amount
                            estimated_remaining = original_balance - budgeted_amount

                            # Format as a card with bulleted list
                            balance_color = "text-green-600" if estimated_remaining >= 0 else "text-red-600"
                            with ui.card().classes("w-full p-2 mb-2 bg-gray-50"):
                                ui.label(f"{account_name}").classes("text-sm font-semibold text-gray-800")
                                ui.label(f"  • Paid: {format_currency(paid_amount)} of {format_currency(budgeted_amount)} budgeted").classes("text-xs text-gray-600")
                                ui.label(f"  • Current Balance: {format_currency(current_balance)}").classes("text-xs text-gray-600")
                                ui.label(f"  • After All Bills: {format_currency(estimated_remaining)}").classes(f"text-xs font-semibold {balance_color}")


                budget_bills_container.clear()
                with budget_bills_container:
                    if not budget_bills:
                        ui.label("No bills in this budget").classes("text-sm text-gray-500")
                    else:
                        for bb in budget_bills:
                            bill_id = str(bb["bill_id"])
                            bill = bill_map.get(bill_id, {})
                            bill_name = bill.get("name", "Unknown")
                            budgeted_amount = bb["budgeted_amount"]
                            paid_amount = bb.get("paid_amount", 0.0)
                            account_name = account_map.get(str(bb.get("account_id", "")), "Unknown")

                            # Get payment method and convert to display label using helper
                            payment_method_value = bill.get("payment_method", "manual")
                            payment_method_label = get_payment_method_label(payment_method_value)

                            paid_on = bb.get("paid_on")
                            paid_date_str = ""
                            if paid_on:
                                parsed_paid = parse_date(paid_on)
                                paid_date_str = f" on {parsed_paid.date().isoformat()}" if parsed_paid else ""

                            due_raw = bb.get("due_date")
                            due_dt = parse_date(due_raw)
                            due_str = due_dt.date().isoformat() if due_dt else "N/A"
                            is_overdue = False
                            if due_dt:
                                today = datetime.datetime.now().date()
                                is_overdue = due_dt.date() < today and (not paid_amount or paid_amount <= 0)

                            # Get bill frequency
                            bill_frequency = bill.get("frequency", "").capitalize()

                            card_classes = "w-full p-2"
                            if paid_amount and paid_amount > 0:
                                card_classes += " bg-green-50"
                            elif is_overdue:
                                card_classes += " bg-amber-50"

                            with ui.card().classes(card_classes):
                                with ui.row().classes("items-center justify-between w-full"):
                                    with ui.column().classes("flex-grow"):
                                        ui.label(f"{bill_name}").classes("font-semibold")
                                        ui.label(f"Due: {due_str} ({bill_frequency})").classes("text-sm")
                                        ui.label(f"Budgeted: {format_currency(budgeted_amount)} | Paid: {format_currency(paid_amount)}{paid_date_str}").classes("text-sm")
                                        ui.label(f"Account: {account_name} | Payment: {payment_method_label}").classes("text-sm text-gray-600")

                                    with ui.column().classes("gap-1 items-start"):
                                        # If bill is unpaid, show amount paid input and mark paid button
                                        if not paid_amount or paid_amount == 0:
                                            with ui.row().classes("gap-1 items-center"):
                                                amount_paid_input = ui.number(label="Amount", value=0.0, min=0, step=0.01).classes("w-24")

                                                def mark_bill_paid(budget_bill_id_capture=bb["id"], bill_id_capture=bill_id, bb_capture=bb, input_capture=amount_paid_input):
                                                    try:
                                                        amount = float(input_capture.value)
                                                        if amount <= 0:
                                                            ui.notify("Please enter a valid amount", type="warning")
                                                            return

                                                        # Update budget bill with paid amount and today's date
                                                        today = datetime.datetime.now().date().isoformat()
                                                        payload = {
                                                            "paid_amount": amount,
                                                            "paid_on": today
                                                        }
                                                        resp = requests.patch(
                                                            f"{API_URL}/budgets/{budget_id}/bills/{budget_bill_id_capture}",
                                                            json=payload
                                                        )
                                                        if resp.status_code != 200:
                                                            ui.notify(handle_error(resp), type="negative")
                                                            return
                                                        ui.notify(f"Marked {bill_name} as paid", type="positive")
                                                        refresh_budget_bills(budget_id)

                                                        # Refresh transactions so new debit/credit entries appear immediately
                                                        for cb in _refresh_transactions_ref:
                                                            try:
                                                                cb()
                                                            except Exception:
                                                                # Ignore individual refresh errors to avoid blocking UI
                                                                pass
                                                    except Exception as e:
                                                        ui.notify(f"Error: {str(e)}", type="negative")

                                                ui.button("Mark Paid", on_click=mark_bill_paid).props("dense flat color=positive")

                                        with ui.row().classes("gap-1"):
                                            def edit_budget_bill(budget_bill_id_capture=bb["id"], budget_id_capture=budget_id):
                                                open_budget_bill_edit_dialog_global(budget_bill_id_capture, budget_id_capture)

                                            ui.button("Edit", on_click=edit_budget_bill).props("dense flat color=primary")

                                            def remove_bill(budget_bill_id=bb["id"]):
                                                resp = requests.delete(
                                                    f"{API_URL}/budgets/{budget_id}/bills/{budget_bill_id}"
                                                )
                                                if resp.status_code != 200:
                                                    ui.notify(handle_error(resp), type="negative")
                                                    return
                                                ui.notify("Bill removed from budget", type="positive")
                                                refresh_budget_bills(budget_id)

                                            ui.button("Remove", on_click=remove_bill).props("dense flat color=negative")

                # Update chart when bills change
                update_chart()

            with ui.row().classes("justify-end gap-2 mt-4"):
                def delete_budget():
                    budget_id = getattr(budget_manage_container, '_budget_id', None)
                    if not budget_id:
                        return
                    resp = requests.delete(f"{API_URL}/budgets/{budget_id}")
                    if resp.status_code != 200:
                        ui.notify(handle_error(resp), type="negative")
                        return
                    ui.notify("Budget deleted", type="positive")
                    budget_manage_container.classes(add="hidden")
                    refresh_budgets()

                delete_budget_btn = ui.button("Delete Budget", on_click=delete_budget).props("color=negative").classes("hidden")
                ui.button("Close", on_click=lambda: (budget_manage_container.classes(add="hidden"), refresh_budgets()))

        # Store reference for global access
        _refresh_budget_bills_ref.append(refresh_budget_bills)

        def open_budget_manage(budget: Dict[str, Any]):
            budget_id = budget.get("id")
            budget_manage_container._budget_id = budget_id
            budget_manage_title.text = f"Manage Budget: {budget.get('name')}"
            budget_description_label.text = budget.get("description", "") or "(no description)"
            start_val = budget.get("start_date")
            end_val = budget.get("end_date_raw") or budget.get("end_date")
            start_dt = parse_date(start_val)
            end_dt = parse_date(end_val)
            budget_start_label.text = f"Start: {start_dt.date().isoformat()}" if start_dt else "Start: -"
            budget_end_label.text = f"End: {end_dt.date().isoformat()}" if end_dt else "End: -"

            # Calculate and display total budget from all bills in this budget
            bb_resp = requests.get(f"{API_URL}/budgets/{budget_id}/bills")
            total = 0.0
            total_paid = 0.0
            total_unpaid = 0.0
            budget_bills = []
            if bb_resp.status_code == 200:
                budget_bills = bb_resp.json()
                total = sum(float(bb["budgeted_amount"]) for bb in budget_bills)
                total_paid = sum(float(bb["paid_amount"]) for bb in budget_bills if bb.get("paid_on"))
                total_unpaid = sum(
                    float(bb["budgeted_amount"]) - (float(bb.get("paid_amount", 0.0)) if bb.get("paid_on") else 0.0)
                    for bb in budget_bills
                )
            budget_total_label.text = f"Total Budget: {format_currency(total)}"
            budget_total_paid_label.text = f"Total Paid: {format_currency(total_paid)}"
            budget_total_unpaid_label.text = f"Total Unpaid Balance: ${total_unpaid:.2f}"

            # Calculate and display delta (over/under budget) using total_paid and total_unpaid
            delta = total_paid - (total_paid + total_unpaid)
            delta_text = f"Over Budget: ${-delta:.2f}" if delta < 0 else f"Under Budget: ${delta:.2f}"
            budget_delta_label.text = delta_text
            budget_delta_label.classes(remove="text-red-600 text-black")
            if delta < 0:
                budget_delta_label.classes(add="text-red-600")
            else:
                budget_delta_label.classes(add="text-black")

            # Populate bill select with bills not already in the budget
            all_bills = fetch_bills()
            bills_in_budget = {str(bb["bill_id"]) for bb in budget_bills}
            available_bills = [b for b in all_bills if str(b["id"]) not in bills_in_budget]
            budget_bill_select.options = [b["name"] for b in available_bills]
            budget_bill_select.update()
            budget_bill_amount.value = 0.0

            refresh_budget_bills(budget_id)

            budget_manage_container.classes(remove="hidden")

        def refresh_budgets():
            # Refresh budgets table
            resp = requests.get(f"{API_URL}/budgets/")
            if resp.status_code != 200:
                budgets_table.rows = []
                return

            budgets = resp.json()

            # Filter based on toggle
            enabled_budgets = [b for b in budgets if b.get("enabled", True) and not b.get("deleted", False)]

            if show_all_budgets_toggle.value:
                # Show all enabled budgets
                filtered_budgets = enabled_budgets
            else:
                # Show all enabled budgets + last N disabled budgets (configurable)
                disabled_budgets = [b for b in budgets if not b.get("enabled", True) and not b.get("deleted", False)]
                recent_disabled = sorted(
                    disabled_budgets,
                    key=lambda b: b.get("created_at", ""),
                    reverse=True
                )[:app_settings["show_num_old_budgets"]]
                filtered_budgets = enabled_budgets + recent_disabled

            rows = []
            for budget in filtered_budgets:
                # Get budget bills to calculate total
                bb_resp = requests.get(f"{API_URL}/budgets/{budget['id']}/bills")
                total = 0.0
                bill_count = 0
                paid_count = 0
                if bb_resp.status_code == 200:
                    budget_bills = bb_resp.json()
                    total = sum(float(bb["budgeted_amount"]) for bb in budget_bills)
                    bill_count = len(budget_bills)
                    paid_count = sum(1 for bb in budget_bills if bb.get("paid_on"))

                # Parse start_date to get month and year for display
                start_date_str = budget.get("start_date", "")
                month_name = ""
                year_str = ""
                if start_date_str:
                    try:
                        start_dt = parse_date(start_date_str)
                        if start_dt:
                            month_names = [
                                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
                            ]
                            month_name = month_names[start_dt.month - 1]
                            year_str = str(start_dt.year)
                    except Exception:
                        pass

                # Parse end_date for display
                end_date_str = budget.get("end_date", "")
                end_date_display = ""
                if end_date_str:
                    try:
                        end_dt = parse_date(end_date_str)
                        if end_dt:
                            end_date_display = end_dt.strftime("%Y-%m-%d")
                    except Exception:
                        pass

                # Check if this is the current budget (today falls within date range)
                is_current = False
                if start_date_str and end_date_str:
                    try:
                        start_dt = parse_date(start_date_str)
                        end_dt = parse_date(end_date_str)
                        today = datetime.datetime.now(timezone.utc)
                        if start_dt and end_dt:
                            # Ensure all datetimes are timezone-aware for comparison
                            if start_dt.tzinfo is None:
                                start_dt = start_dt.replace(tzinfo=timezone.utc)
                            if end_dt.tzinfo is None:
                                end_dt = end_dt.replace(tzinfo=timezone.utc)
                            is_current = start_dt <= today <= end_dt
                    except Exception:
                        pass

                rows.append({
                    "id": budget["id"],
                    "name": budget["name"],
                    "month": month_name,
                    "year": year_str,
                    "start_date": start_date_str,
                    "end_date": end_date_display,
                    "end_date_raw": end_date_str,
                    "bills": f"{paid_count}/{bill_count}",
                    "total": f"${total:.2f}",
                    "enabled": budget.get("enabled", True),
                    "is_current": is_current,
                })

            budgets_table.rows = rows

        # Initial render - chart first, then budgets
        update_chart()
        refresh_budgets()

        # Add chart update to refresh callback
        def refresh_with_chart():
            update_chart()
            refresh_budgets()

        # Override the refresh callback
        register_refresh_callback(refresh_with_chart)

        # Refresh when toggle changes
        show_all_budgets_toggle.on("update:model-value", lambda _: refresh_with_chart())
