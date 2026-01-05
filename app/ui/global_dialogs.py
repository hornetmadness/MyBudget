"""Global dialogs and utilities accessible from all tabs."""
import sys
from pathlib import Path
# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.ui.utils import fetch_accounts, parse_date, format_datetime, datetime as dtmod
import requests
from app.config import API_URL


try:
    from app.models.schemas import FrequencyEnum
except ImportError:
    from ..models.schemas import FrequencyEnum

def setup_test_frequency_dialog(ui, title: str = "Test Income Frequency"):
    """
    Set up the global Test Frequency Helper dialog and return the open function.
    Args:
        ui: NiceGUI ui instance
        title: Dialog title label text (default: 'Test Income Frequency')
    Returns:
        test_freq_dialog: The dialog instance
        open_test_freq_dialog: Function to open the dialog
    """
    test_freq_dialog = ui.dialog()
    with test_freq_dialog, ui.card().classes("w-full max-w-md"):
        ui.label(title).classes("text-lg font-semibold mb-2")

        test_freq_select = ui.select(
            label="Frequency",
            options=[freq.value for freq in FrequencyEnum],
            value="monthly"
        )
        test_start_date_input = ui.input(label="Start Date (YYYY-MM-DD)").classes("w-full")
        test_start_date_picker = ui.date(mask="YYYY-MM-DD").props("dense outlined").classes("w-full hidden")
        def toggle_test_start_picker():
            test_start_date_picker.classes(toggle="hidden")
        test_start_date_input.on("click", toggle_test_start_picker)
        def on_test_start_selected():
            if test_start_date_picker.value:
                date_str = test_start_date_picker.value.isoformat() if hasattr(test_start_date_picker.value, 'isoformat') else str(test_start_date_picker.value)
                test_start_date_input.value = date_str
                test_start_date_picker.classes(add="hidden")
        test_start_date_picker.on_value_change(on_test_start_selected)
        test_freq_results = ui.column().classes("gap-1 mt-2")
        def run_test_frequency():
            freq = test_freq_select.value
            start_str = test_start_date_input.value
            start_dt = parse_date(start_str)
            if not start_dt:
                test_freq_results.clear()
                with test_freq_results:
                    ui.label("Invalid start date").classes("text-red-600")
                return
            dates = []
            current = start_dt
            count = 0
            while count < 12:
                dates.append(format_datetime(current, "%Y-%m-%d"))
                if freq == "weekly":
                    current += dtmod.timedelta(days=7)
                elif freq == "biweekly":
                    current += dtmod.timedelta(days=14)
                elif freq == "semimonthly":
                    if current.day < 15:
                        current = current.replace(day=15)
                    else:
                        month = current.month + 1 if current.month < 12 else 1
                        year = current.year + 1 if month == 1 else current.year
                        current = current.replace(year=year, month=month, day=1)
                elif freq == "monthly":
                    month = current.month + 1 if current.month < 12 else 1
                    year = current.year + 1 if month == 1 else current.year
                    try:
                        current = current.replace(year=year, month=month)
                    except ValueError:
                        from calendar import monthrange
                        last_day = monthrange(year, month)[1]
                        current = current.replace(year=year, month=month, day=last_day)
                elif freq == "yearly":
                    current = current.replace(year=current.year + 1)
                count += 1
            test_freq_results.clear()
            with test_freq_results:
                ui.label("Next 12 Occurrences:").classes("font-semibold mb-1")
                for d in dates:
                    ui.label(d).classes("text-sm")
        ui.button("Test Frequency", color="accent", on_click=run_test_frequency).classes("mt-2")
        with test_freq_results:
            ui.label("")
    def open_test_freq_dialog():
        test_freq_dialog.open()
    return test_freq_dialog, open_test_freq_dialog

def setup_budget_bill_edit_dialog(ui, requests, API_URL, _parse_date, _handle_error, _refresh_dashboard_ref, _refresh_budget_bills_ref, _refresh_transactions_ref):
    """
    Set up the global budget bill edit dialog and return the open function.
    
    Returns:
        function: open_budget_bill_edit_dialog_global function
    """
    # Global Edit Bill Payment Dialog (accessible from any tab)
    budget_bill_edit_dialog_global = ui.dialog()
    with budget_bill_edit_dialog_global, ui.card().classes("w-full max-w-lg"):
        ui.label("Edit Bill Payment").classes("text-lg font-semibold")
        budget_bill_edit_name_global = ui.label("").classes("text-md mb-2")
        with ui.row().classes("items-center gap-2"):
            budget_bill_edit_due_global = ui.number(label="Amount Due", format="%.2f", value=0.0)
            ui.label("Due Date")
            budget_bill_edit_due_date_global = ui.input(label="Date (YYYY-MM-DD)").classes("w-32")
            budget_bill_edit_due_date_picker_global = ui.date(mask="YYYY-MM-DD").props("dense outlined").classes("hidden")
            def toggle_due_date_picker_global():
                budget_bill_edit_due_date_picker_global.classes(toggle="hidden")
            budget_bill_edit_due_date_global.on("click", toggle_due_date_picker_global)
            def on_due_date_selected_global():
                if budget_bill_edit_due_date_picker_global.value:
                    date_str = budget_bill_edit_due_date_picker_global.value.isoformat() if hasattr(budget_bill_edit_due_date_picker_global.value, 'isoformat') else str(budget_bill_edit_due_date_picker_global.value)
                    budget_bill_edit_due_date_global.value = date_str
                    budget_bill_edit_due_date_picker_global.classes(add="hidden")
            budget_bill_edit_due_date_picker_global.on_value_change(on_due_date_selected_global)
        with ui.row().classes("items-center gap-2"):
            budget_bill_edit_paid_global = ui.number(label="Paid Amount", format="%.2f", value=0.0)
            ui.label("Paid On")
            budget_bill_edit_paid_on_global = ui.input(label="Date (YYYY-MM-DD)").classes("w-32")
            budget_bill_edit_paid_on_picker_global = ui.date(mask="YYYY-MM-DD").props("dense outlined").classes("hidden")
            def toggle_paid_on_picker_global():
                budget_bill_edit_paid_on_picker_global.classes(toggle="hidden")
            budget_bill_edit_paid_on_global.on("click", toggle_paid_on_picker_global)
            def on_paid_on_date_selected_global():
                if budget_bill_edit_paid_on_picker_global.value:
                    date_str = budget_bill_edit_paid_on_picker_global.value.isoformat() if hasattr(budget_bill_edit_paid_on_picker_global.value, 'isoformat') else str(budget_bill_edit_paid_on_picker_global.value)
                    budget_bill_edit_paid_on_global.value = date_str
                    budget_bill_edit_paid_on_picker_global.classes(add="hidden")
            budget_bill_edit_paid_on_picker_global.on_value_change(on_paid_on_date_selected_global)
        budget_bill_edit_account_global = ui.select(label="Account", options=[]).props("dense outlined")
        budget_bill_edit_note_global = ui.input(label="Note (optional)").classes("w-full")
        
        def save_budget_bill_edit_global():
            budget_bill_id = budget_bill_edit_dialog_global.props.get("data-budget-bill-id")
            bill_id = budget_bill_edit_dialog_global.props.get("data-bill-id")
            budget_id = budget_bill_edit_dialog_global.props.get("data-budget-id")
            if not budget_bill_id or not bill_id or not budget_id:
                budget_bill_edit_dialog_global.close()
                return
            
            # Get selected account ID from name
            accounts = fetch_accounts()
            account_lookup_local = {a["name"]: str(a["id"]) for a in accounts}
            selected_account_id = account_lookup_local.get(budget_bill_edit_account_global.value)
            
            # Update budget bill (paid amount, budgeted amount, date, due date, and account)
            budget_bill_payload = {
                "paid_amount": float(budget_bill_edit_paid_global.value or 0.0),
                "budgeted_amount": float(budget_bill_edit_due_global.value or 0.0),
            }
            if budget_bill_edit_note_global.value:
                budget_bill_payload["note"] = budget_bill_edit_note_global.value
            if budget_bill_edit_paid_on_global.value:
                budget_bill_payload["paid_on"] = budget_bill_edit_paid_on_global.value
            if budget_bill_edit_due_date_global.value:
                budget_bill_payload["due_date"] = budget_bill_edit_due_date_global.value
            if selected_account_id:
                budget_bill_payload["account_id"] = selected_account_id
            
            resp = requests.patch(
                f"{API_URL}/budgets/{budget_id}/bills/{budget_bill_id}",
                json=budget_bill_payload
            )
            if resp.status_code != 200:
                _handle_error(resp)
                return
            
            ui.notify("Bill updated", type="positive")
            # Refresh dashboard if refresh function exists
            if _refresh_dashboard_ref:
                _refresh_dashboard_ref[0]()
            # Refresh budget bills if in budgets tab
            if _refresh_budget_bills_ref:
                _refresh_budget_bills_ref[0](budget_id)
            # Refresh transactions if available
            if _refresh_transactions_ref:
                _refresh_transactions_ref[0]()
            budget_bill_edit_dialog_global.close()
        
        with ui.row().classes("justify-end gap-2"):
            ui.button("Cancel", on_click=budget_bill_edit_dialog_global.close)
            ui.button("Save", color="primary", on_click=save_budget_bill_edit_global)
    
    # Global function to open edit dialog (defined here so it's accessible from all tabs)
    def open_budget_bill_edit_dialog_global(budget_bill_id: str, budget_id: str = None):
        """Open the edit bill payment dialog for a specific budget bill."""
        # Fetch the budget bill details
        if not budget_id:
            # Find budget_id by querying all budgets
            budgets_resp = requests.get(f"{API_URL}/budgets/")
            if budgets_resp.status_code == 200:
                budgets = budgets_resp.json()
                for budget in budgets:
                    bb_resp = requests.get(f"{API_URL}/budgets/{budget['id']}/bills")
                    if bb_resp.status_code == 200:
                        budget_bills = bb_resp.json()
                        for bb in budget_bills:
                            if str(bb["id"]) == str(budget_bill_id):
                                budget_id = budget["id"]
                                break
                    if budget_id:
                        break
        
        if not budget_id:
            ui.notify("Could not find budget for this bill", type="warning")
            return
        
        # Fetch budget bill details
        bb_resp = requests.get(f"{API_URL}/budgets/{budget_id}/bills")
        if bb_resp.status_code != 200:
            ui.notify("Could not load budget bill details", type="warning")
            return
        
        budget_bills = bb_resp.json()
        bb = next((b for b in budget_bills if str(b["id"]) == str(budget_bill_id)), None)
        
        if not bb:
            ui.notify("Budget bill not found", type="warning")
            return
        
        # Fetch bill details
        bill_id = bb["bill_id"]
        bill_resp = requests.get(f"{API_URL}/bills/{bill_id}")
        if bill_resp.status_code != 200:
            ui.notify("Could not load bill details", type="warning")
            return
        
        bill = bill_resp.json()
        
        # Set dialog data
        budget_bill_edit_dialog_global.props["data-budget-bill-id"] = budget_bill_id
        budget_bill_edit_dialog_global.props["data-bill-id"] = bill_id
        budget_bill_edit_dialog_global.props["data-budget-id"] = budget_id
        
        budget_bill_edit_name_global.text = f"Bill: {bill.get('name', 'Unknown')}"
        budget_bill_edit_due_global.value = bb.get("budgeted_amount", 0.0)
        budget_bill_edit_paid_global.value = bb.get("paid_amount", 0.0)
        
        # Set paid date
        paid_on_val = bb.get("paid_on")
        if paid_on_val:
            parsed = _parse_date(paid_on_val)
            budget_bill_edit_paid_on_global.value = parsed.date().isoformat() if parsed else ""
        else:
            budget_bill_edit_paid_on_global.value = ""
        
        # Set due date
        due_val = bb.get("due_date")
        if due_val:
            parsed_due = _parse_date(due_val)
            budget_bill_edit_due_date_global.value = parsed_due.date().isoformat() if parsed_due else ""
        else:
            budget_bill_edit_due_date_global.value = ""
        
        # Set account options and current value
        accounts = fetch_accounts()
        budget_bill_edit_account_global.options = [a["name"] for a in accounts]
        account_map = {str(a["id"]): a["name"] for a in accounts}
        current_account_id = str(bb.get("account_id", ""))
        current_account_name = account_map.get(current_account_id, "")
        budget_bill_edit_account_global.value = current_account_name
        
        # Set note
        budget_bill_edit_note_global.value = bb.get("note", "")
        
        budget_bill_edit_dialog_global.open()
    
    return open_budget_bill_edit_dialog_global
