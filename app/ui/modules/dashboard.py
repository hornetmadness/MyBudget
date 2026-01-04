try:
    from app.ui.utils import fetch_budgetbills, fetch_bills, parse_date, format_date, format_datetime
except ImportError:
    from ..utils import fetch_budgetbills, fetch_bills, parse_date, format_date, format_datetime


def build_dashboard_tab(
    ui,
    requests,
    API_URL,
    _refresh_dashboard_ref,
    register_refresh_callback,
    format_currency,
    datetime,
    timezone,
    open_budget_bill_edit_dialog_global,
    _refresh_budget_bills_ref,
    _refresh_transactions_ref,
    *args,
):
    """Build the dashboard tab UI."""
    dashboard_content = ui.column().classes("w-full")

    # Dashboard budgetbill detail dialog
    dashboard_bb_dialog = ui.dialog()
    with dashboard_bb_dialog, ui.card().classes("w-full max-w-lg"):
        dashboard_bb_title = ui.label("Budget Bill Details").classes("text-lg font-semibold mb-4")
        dashboard_bb_content = ui.column().classes("w-full")
        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Close", on_click=dashboard_bb_dialog.close)

    def show_budgetbill_dialog(bb_id):
        """Show budget bill details in dialog."""
        budgetbills = fetch_budgetbills()
        budgetbill = next((bb for bb in budgetbills if bb["id"] == bb_id), None)

        if not budgetbill:
            ui.notify("Budget bill not found", type="warning")
            return

        bill_id = budgetbill.get("bill_id")
        bill_name = "Unknown"
        if bill_id:
            bills = fetch_bills()
            bill = next((b for b in bills if b["id"] == bill_id), None)
            if bill:
                bill_name = bill.get("name", "Unknown")

        dashboard_bb_content.clear()
        dashboard_bb_title.text = f"Budget Bill: {bill_name}"

        with dashboard_bb_content:
            ui.label(f"Amount Budgeted: {format_currency(budgetbill.get('budgeted_amount', 0.0))}").classes("mb-2")
            ui.label(f"Amount Paid: {format_currency(budgetbill.get('paid_amount', 0.0))}").classes("mb-2")

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

        dashboard_bb_dialog.open()
    def refresh_dashboard() -> None:
        """Refresh dashboard with latest data."""
        dashboard_content.clear()
        try:
            with dashboard_content:
                # Header
                ui.label("Financial Overview").classes("text-2xl font-bold mb-4")

                # Summary cards row (all in one line)
                with ui.row().classes("w-full gap-4 mb-6"):
                    # Total Accounts Balance
                    accounts_resp = requests.get(f"{API_URL}/accounts/")
                    total_balance = 0.0
                    account_count = 0
                    if accounts_resp.status_code == 200:
                        accounts = accounts_resp.json()
                        account_count = len(accounts)
                        total_balance = sum(float(a.get("balance", 0.0)) for a in accounts)

                    with ui.card().classes("flex-1"):
                        ui.label("Total Account Balance").classes("text-sm text-gray-600")
                        ui.label(format_currency(total_balance)).classes("text-2xl font-bold text-green-600")
                        ui.label(f"{account_count} accounts").classes("text-xs text-gray-500 mt-1")

                    # Active Budgets
                    budgets_resp = requests.get(f"{API_URL}/budgets/")
                    active_budget_count = 0
                    total_budgeted = 0.0
                    if budgets_resp.status_code == 200:
                        budgets = budgets_resp.json()
                        enabled_budgets = [b for b in budgets if b.get("enabled", True)]
                        active_budget_count = len(enabled_budgets)
                        for budget in enabled_budgets:
                            bb_resp = requests.get(f"{API_URL}/budgets/{budget['id']}/bills")
                            if bb_resp.status_code == 200:
                                budget_bills = bb_resp.json()
                                total_budgeted += sum(float(bb.get("budgeted_amount", 0.0)) for bb in budget_bills)

                    with ui.card().classes("flex-1"):
                        ui.label("Current Budget").classes("text-sm text-gray-600")
                        ui.label(format_currency(total_budgeted)).classes("text-2xl font-bold text-blue-600")
                        ui.label(f"{active_budget_count} budgets").classes("text-xs text-gray-500 mt-1")

                    # Total Bills
                    bills_resp = requests.get(f"{API_URL}/bills/")
                    bill_count = 0
                    if bills_resp.status_code == 200:
                        bills = bills_resp.json()
                        bill_count = len(bills)

                    with ui.card().classes("flex-1"):
                        ui.label("Total Bills").classes("text-sm text-gray-600")
                        ui.label(f"{bill_count}").classes("text-2xl font-bold text-purple-600")
                        ui.label("recurring").classes("text-xs text-gray-500 mt-1")

                # Unpaid Budget Bills (in active budgets)
                ui.label("Unpaid Bills").classes("text-lg font-semibold mb-2 mt-6")

                today = datetime.datetime.now(timezone.utc)

                budgets_resp = requests.get(f"{API_URL}/budgets/")
                unpaid_bills = []

                if budgets_resp.status_code == 200:
                    budgets = budgets_resp.json()
                    for budget in budgets:
                        start_date = parse_date(budget.get("start_date"))
                        end_date = parse_date(budget.get("end_date"))

                        if start_date and start_date.tzinfo is None:
                            start_date = start_date.replace(tzinfo=timezone.utc)
                        if end_date and end_date.tzinfo is None:
                            end_date = end_date.replace(tzinfo=timezone.utc)

                        if start_date and end_date and start_date <= today <= end_date:
                            bb_resp = requests.get(f"{API_URL}/budgets/{budget['id']}/bills")
                            if bb_resp.status_code == 200:
                                budget_bills = bb_resp.json()
                                for bb in budget_bills:
                                    budgeted = float(bb.get("budgeted_amount", 0.0))
                                    paid = float(bb.get("paid_amount", 0.0))
                                    if paid < budgeted or not bb.get("paid_on"):
                                        bb["budget_name"] = budget.get("name", "Unknown Budget")
                                        bb["budget_id"] = budget["id"]
                                        unpaid_bills.append(bb)

                # Sort by due_date
                unpaid_bills.sort(key=lambda b: b.get("due_date", "") or "9999-12-31")

                if unpaid_bills:
                    with ui.card().classes("w-full"):
                        # Get account and bill names for display
                        accounts_map = {}
                        accounts_resp = requests.get(f"{API_URL}/accounts/")
                        if accounts_resp.status_code == 200:
                            for acc in accounts_resp.json():
                                accounts_map[acc["id"]] = acc["name"]

                        bills_map = {}
                        bills_resp = requests.get(f"{API_URL}/bills/")
                        if bills_resp.status_code == 200:
                            for bill in bills_resp.json():
                                bills_map[bill["id"]] = bill["name"]

                        with ui.grid(columns="repeat(6, 1fr)").classes("w-full gap-2"):
                            ui.label("Due Date").classes("font-semibold text-sm")
                            ui.label("Bill").classes("font-semibold text-sm")
                            ui.label("Budget").classes("font-semibold text-sm")
                            ui.label("Amount Due").classes("font-semibold text-sm")
                            ui.label("Paid").classes("font-semibold text-sm")
                            ui.label("Actions").classes("font-semibold text-sm text-center")

                            for bb in unpaid_bills:
                                due_date = parse_date(bb.get("due_date"))
                                due_date_str = format_date(due_date) if due_date else "No date"
                                ui.label(due_date_str).classes("text-sm")

                                # Bill name as clickable link
                                bill_name = bills_map.get(bb["bill_id"], f"ID: {bb['bill_id']}")

                                def open_edit_from_dashboard(bb_id=bb["id"], budget_id=bb["budget_id"]):
                                    open_budget_bill_edit_dialog_global(bb_id, budget_id)

                                ui.label(bill_name).classes("text-sm text-blue-600 cursor-pointer hover:underline").on("click", open_edit_from_dashboard)

                                # Budget name
                                ui.label(bb.get("budget_name", "N/A")).classes("text-sm")

                                # Amount Due (budgeted - paid)
                                budgeted = float(bb.get("budgeted_amount", 0.0))
                                paid = float(bb.get("paid_amount", 0.0))
                                remaining = budgeted - paid
                                ui.label(format_currency(remaining)).classes("text-sm font-semibold text-orange-600")

                                # Paid amount
                                ui.label(format_currency(paid)).classes("text-sm text-gray-600")

                                # Actions
                                with ui.row().classes("justify-center gap-1"):
                                    def view_bb_detail(bb_id=bb["id"]):
                                        show_budgetbill_dialog(bb_id)

                                    ui.button(icon="info", on_click=view_bb_detail).props("flat dense size=sm").style("color: #2196F3")
                else:
                # Show message when no unpaid bills are present
                    ui.label("No unpaid bills").classes("text-gray-500")

                # Recent transactions
                ui.label("Recent Transactions").classes("text-lg font-semibold mb-2 mt-6")

                trans_resp = requests.get(f"{API_URL}/transactions/?limit=5")
                if trans_resp.status_code == 200:
                    transactions = trans_resp.json()
                    if transactions:
                        transactions.sort(key=lambda t: t.get("occurred_at", ""), reverse=True)

                        with ui.card().classes("w-full"):
                            accounts_map = {}
                            accounts_resp = requests.get(f"{API_URL}/accounts/")
                            if accounts_resp.status_code == 200:
                                for acc in accounts_resp.json():
                                    accounts_map[acc["id"]] = acc["name"]

                            with ui.grid(columns="repeat(6, 1fr)").classes("w-full gap-2"):
                                ui.label("Date").classes("font-semibold text-sm")
                                ui.label("Account").classes("font-semibold text-sm")
                                ui.label("Type").classes("font-semibold text-sm")
                                ui.label("Amount").classes("font-semibold text-sm")
                                ui.label("Note").classes("font-semibold text-sm")
                                ui.label("Actions").classes("font-semibold text-sm text-center")

                                for trans in transactions:
                                    occurred_at = parse_date(trans.get("occurred_at"))
                                    trans_date = format_datetime(occurred_at) if occurred_at else "N/A"
                                    ui.label(trans_date).classes("text-sm")

                                    account_name = accounts_map.get(trans["account_id"], f"ID: {trans['account_id']}")
                                    ui.label(account_name).classes("text-sm")

                                    trans_type = trans.get("transaction_type", "").capitalize()
                                    ui.label(trans_type).classes("text-sm")

                                    amount = float(trans.get("amount", 0.0))
                                    color = "text-green-600" if trans.get("transaction_type") == "credit" else "text-red-600"
                                    ui.label(format_currency(amount)).classes(f"text-sm font-semibold {color}")

                                    note = trans.get("note", "")[:30]
                                    ui.label(note).classes("text-sm text-gray-600")

                                    budgetbill_id = trans.get("budgetbill_id")
                                    with ui.row().classes("justify-center"):
                                        if budgetbill_id:
                                            def view_budgetbill_detail(bb_id=budgetbill_id):
                                                show_budgetbill_dialog(bb_id)

                                            ui.button(icon="info", on_click=view_budgetbill_detail).props("flat dense size=sm").style("color: #2196F3")
                    else:
                        ui.label("No transactions yet").classes("text-gray-500")
                else:
                    ui.label("Unable to load transactions").classes("text-gray-500")

        except Exception as e:
            dashboard_content.clear()
            with dashboard_content:
                ui.label(f"Error loading dashboard: {e}").classes("text-red-500")
                print(f"Dashboard error: {e}")
                import traceback
                traceback.print_exc()

    _refresh_dashboard_ref.append(refresh_dashboard)
    register_refresh_callback(refresh_dashboard)
    refresh_dashboard()
