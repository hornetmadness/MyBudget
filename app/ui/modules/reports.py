"""Reports Module - Financial Analysis and Reporting UI

This module provides financial reporting and analysis including:
- Multi-budget comparison
- Spending trend analysis
- Category-based expense breakdown
- Budget vs actual comparisons
- Visual charts and graphs
- Export capabilities
"""

import sys
from typing import Any, Dict, List
from pathlib import Path

# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import requests
from app.config import API_URL
from app.ui.utils import fetch_accounts, fetch_bills, fetch_categories, parse_date


def build_reports_tab(ui, requests, API_URL, _refresh_dashboard_ref, register_refresh_callback, format_currency, datetime, timezone, open_budget_bill_edit_dialog_global, _refresh_budget_bills_ref, _refresh_transactions_ref, *args) -> None:
    """Build the complete reports tab UI with financial analysis tools.
    
    Creates:
        - Budget selector for comparison
        - Spending trend charts
        - Category breakdown analysis
        - Budget comparison table
        - Visual data representations
    
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
    ui.label("Reports").classes("text-2xl font-bold mb-4")

    with ui.card().classes("w-full max-w-6xl mb-4"):
        ui.label("Select Budgets to Compare").classes("text-lg font-semibold mb-2")

        # Budget selector (multi-select)
        budget_selector = ui.select(
            options=[],
            label="Budgets",
            multiple=True,
        ).classes("w-full mb-4")

        generate_report_btn = ui.button("Generate Report", color="primary")

        # Report containers
        report_summary = ui.column().classes("w-full mt-4")
        report_details = ui.column().classes("w-full mt-4")

    # Store budget mapping for lookups
    budget_id_map = {}  # name -> id
    budget_name_map = {}  # id -> name

    def refresh_budget_options():
        """Refresh available budgets for selection."""
        nonlocal budget_id_map, budget_name_map

        resp = requests.get(f"{API_URL}/budgets/")
        if resp.status_code != 200:
            budget_selector.options = []
            return

        budgets = resp.json()
        # Filter enabled budgets
        enabled_budgets = [b for b in budgets if b.get("enabled", True)]

        # Build lookup maps
        budget_id_map = {b["name"]: b["id"] for b in enabled_budgets}
        budget_name_map = {b["id"]: b["name"] for b in enabled_budgets}

        # Use list of names for display
        budget_selector.options = [b["name"] for b in enabled_budgets]
        budget_selector.update()

    def generate_report():
        """Generate report for selected budgets."""
        selected_budget_names = budget_selector.value if isinstance(budget_selector.value, list) else ([budget_selector.value] if budget_selector.value else [])

        if not selected_budget_names:
            ui.notify("Please select at least one budget", type="warning")
            return

        # Convert budget names to IDs
        selected_budget_ids = [budget_id_map[name] for name in selected_budget_names if name in budget_id_map]

        if not selected_budget_ids:
            ui.notify("Failed to resolve budget selections", type="negative")
            return

        # Fetch budget data
        all_budgets = []
        for budget_id in selected_budget_ids:
            resp = requests.get(f"{API_URL}/budgets/{budget_id}")
            if resp.status_code == 200:
                all_budgets.append(resp.json())

        if not all_budgets:
            ui.notify("Failed to fetch budget data", type="negative")
            return

        # Collect budget bills and calculate totals
        total_budgeted = 0.0
        total_paid = 0.0
        bill_breakdown = {}
        account_breakdown = {}

        for budget in all_budgets:
            budget_id = budget["id"]
            bb_resp = requests.get(f"{API_URL}/budgets/{budget_id}/bills")

            if bb_resp.status_code == 200:
                budget_bills = bb_resp.json()

                for bb in budget_bills:
                    budgeted_amt = float(bb.get("budgeted_amount", 0.0))
                    paid_amt = float(bb.get("paid_amount", 0.0)) if bb.get("paid_on") else 0.0

                    total_budgeted += budgeted_amt
                    total_paid += paid_amt

                    # Breakdown by bill
                    bill_id = bb.get("bill_id")
                    if bill_id:
                        bills = fetch_bills()
                        bill = next((b for b in bills if b["id"] == bill_id), None)
                        if bill:
                            bill_name = bill["name"]
                            if bill_name not in bill_breakdown:
                                bill_breakdown[bill_name] = {"budgeted": 0.0, "paid": 0.0}
                            bill_breakdown[bill_name]["budgeted"] += budgeted_amt
                            bill_breakdown[bill_name]["paid"] += paid_amt

                    # Breakdown by account
                    account_id = bb.get("account_id")
                    if account_id:
                        accounts = fetch_accounts()
                        account = next((a for a in accounts if a["id"] == account_id), None)
                        if account:
                            account_name = account["name"]
                            if account_name not in account_breakdown:
                                account_breakdown[account_name] = {"budgeted": 0.0, "paid": 0.0}
                            account_breakdown[account_name]["budgeted"] += budgeted_amt
                            account_breakdown[account_name]["paid"] += paid_amt

        # Calculate statistics
        remaining = total_budgeted - total_paid
        percent_spent = (total_paid / total_budgeted * 100) if total_budgeted > 0 else 0

        # Clear previous report
        report_summary.clear()
        report_details.clear()

        # Render summary
        with report_summary:
            ui.label("Summary").classes("text-xl font-bold mb-2")
            with ui.row().classes("gap-8"):
                with ui.card().classes("p-4"):
                    ui.label("Total Budgeted").classes("text-sm text-gray-600")
                    ui.label(f"${total_budgeted:,.2f}").classes("text-2xl font-bold text-blue-600")
                with ui.card().classes("p-4"):
                    ui.label("Total Paid").classes("text-sm text-gray-600")
                    ui.label(f"${total_paid:,.2f}").classes("text-2xl font-bold text-green-600")
                with ui.card().classes("p-4"):
                    ui.label("Remaining").classes("text-sm text-gray-600")
                    ui.label(f"${remaining:,.2f}").classes("text-2xl font-bold text-orange-600")
                with ui.card().classes("p-4"):
                    ui.label("% Spent").classes("text-sm text-gray-600")
                    ui.label(f"{percent_spent:.1f}%").classes("text-2xl font-bold text-purple-600")

        # Render detailed breakdowns
        with report_details:
            # Breakdown by Bill
            if bill_breakdown:
                ui.label("Breakdown by Bill").classes("text-xl font-bold mt-4 mb-2")
                bill_columns = [
                    {"name": "bill", "label": "Bill", "field": "bill", "sortable": True, "align": "left"},
                    {"name": "budgeted", "label": "Budgeted", "field": "budgeted", "sortable": True, "align": "right"},
                    {"name": "paid", "label": "Paid", "field": "paid", "sortable": True, "align": "right"},
                    {"name": "remaining", "label": "Remaining", "field": "remaining", "sortable": True, "align": "right"},
                    {"name": "percent", "label": "% Spent", "field": "percent", "sortable": True, "align": "right"},
                ]
                bill_rows = []
                for bill_name, amounts in sorted(bill_breakdown.items()):
                    budgeted = amounts["budgeted"]
                    paid = amounts["paid"]
                    remaining = budgeted - paid
                    percent = (paid / budgeted * 100) if budgeted > 0 else 0
                    bill_rows.append({
                        "bill": bill_name,
                        "budgeted": f"${budgeted:,.2f}",
                        "paid": f"${paid:,.2f}",
                        "remaining": f"${remaining:,.2f}",
                        "percent": f"{percent:.1f}%",
                    })
                ui.table(columns=bill_columns, rows=bill_rows, row_key="bill").classes("w-full")

            # Breakdown by Account
            if account_breakdown:
                ui.label("Breakdown by Account").classes("text-xl font-bold mt-4 mb-2")
                account_columns = [
                    {"name": "account", "label": "Account", "field": "account", "sortable": True, "align": "left"},
                    {"name": "budgeted", "label": "Budgeted", "field": "budgeted", "sortable": True, "align": "right"},
                    {"name": "paid", "label": "Paid", "field": "paid", "sortable": True, "align": "right"},
                    {"name": "remaining", "label": "Remaining", "field": "remaining", "sortable": True, "align": "right"},
                    {"name": "percent", "label": "% Spent", "field": "percent", "sortable": True, "align": "right"},
                ]
                account_rows = []
                for account_name, amounts in sorted(account_breakdown.items()):
                    budgeted = amounts["budgeted"]
                    paid = amounts["paid"]
                    remaining = budgeted - paid
                    percent = (paid / budgeted * 100) if budgeted > 0 else 0
                    account_rows.append({
                        "account": account_name,
                        "budgeted": f"${budgeted:,.2f}",
                        "paid": f"${paid:,.2f}",
                        "remaining": f"${remaining:,.2f}",
                        "percent": f"{percent:.1f}%",
                    })
                ui.table(columns=account_columns, rows=account_rows, row_key="account").classes("w-full")

            # Breakdown by Category with Pie Chart
            bills = fetch_bills()
            category_breakdown = {}
            for bill in bills:
                if not bill.get("deleted", False) and bill.get("enabled", True):
                    category_id = bill.get("category_id")
                    category_name = "Uncategorized"
                    if category_id:
                        try:
                            categories = fetch_categories()
                            cat = next((c for c in categories if c["id"] == category_id), None)
                            if cat:
                                category_name = cat.get("name", "Uncategorized")
                        except Exception:
                            pass

                    budgeted_amt = float(bill.get("budgeted_amount", 0.0))
                    if budgeted_amt > 0:
                        if category_name not in category_breakdown:
                            category_breakdown[category_name] = 0.0
                        category_breakdown[category_name] += budgeted_amt

            if category_breakdown:
                ui.label("Budget by Category").classes("text-xl font-bold mt-4 mb-4")

                # Prepare data for pie chart
                category_labels = list(category_breakdown.keys())
                category_values = list(category_breakdown.values())

                # Create pie chart using ui.html and Chart.js
                import json
                chart_data = json.dumps({
                    "labels": category_labels,
                    "datasets": [{
                        "data": category_values,
                        "backgroundColor": [
                            "rgba(255, 99, 132, 0.7)",
                            "rgba(54, 162, 235, 0.7)",
                            "rgba(255, 206, 86, 0.7)",
                            "rgba(75, 192, 192, 0.7)",
                            "rgba(153, 102, 255, 0.7)",
                            "rgba(255, 159, 64, 0.7)",
                            "rgba(199, 199, 199, 0.7)",
                            "rgba(83, 102, 255, 0.7)",
                        ],
                        "borderColor": [
                            "rgba(255, 99, 132, 1)",
                            "rgba(54, 162, 235, 1)",
                            "rgba(255, 206, 86, 1)",
                            "rgba(75, 192, 192, 1)",
                            "rgba(153, 102, 255, 1)",
                            "rgba(255, 159, 64, 1)",
                            "rgba(199, 199, 199, 1)",
                            "rgba(83, 102, 255, 1)",
                        ],
                        "borderWidth": 1,
                    }]
                })

                # Render category table
                category_columns = [
                    {"name": "category", "label": "Category", "field": "category", "sortable": True, "align": "left"},
                    {"name": "amount", "label": "Budgeted Amount", "field": "amount", "sortable": True, "align": "right"},
                    {"name": "percent", "label": "% of Total", "field": "percent", "sortable": True, "align": "right"},
                ]
                category_rows = []
                total_category = sum(category_values)
                for category_name in sorted(category_breakdown.keys()):
                    amount = category_breakdown[category_name]
                    percent = (amount / total_category * 100) if total_category > 0 else 0
                    category_rows.append({
                        "category": category_name,
                        "amount": f"${amount:,.2f}",
                        "percent": f"{percent:.1f}%",
                    })

                with ui.row().classes("gap-8 w-full"):
                    with ui.column().classes("flex-1"):
                        ui.table(columns=category_columns, rows=category_rows, row_key="category").classes("w-full")

                    with ui.column().classes("flex-1 items-center"):
                        ui.html('''
                        <div style="width: 300px; height: 300px;">
                            <canvas id="category-pie-chart"></canvas>
                        </div>
                        ''')

                        # Use add_body_html for script tags
                        import json
                        chart_config = {
                            "labels": category_labels,
                            "datasets": [{
                                "data": category_values,
                                "backgroundColor": [
                                    "rgba(255, 99, 132, 0.7)",
                                    "rgba(54, 162, 235, 0.7)",
                                    "rgba(255, 206, 86, 0.7)",
                                    "rgba(75, 192, 192, 0.7)",
                                    "rgba(153, 102, 255, 0.7)",
                                    "rgba(255, 159, 64, 0.7)",
                                    "rgba(199, 199, 199, 0.7)",
                                    "rgba(83, 102, 255, 0.7)",
                                ],
                                "borderColor": [
                                    "rgba(255, 99, 132, 1)",
                                    "rgba(54, 162, 235, 1)",
                                    "rgba(255, 206, 86, 1)",
                                    "rgba(75, 192, 192, 1)",
                                    "rgba(153, 102, 255, 1)",
                                    "rgba(255, 159, 64, 1)",
                                    "rgba(199, 199, 199, 1)",
                                    "rgba(83, 102, 255, 1)",
                                ],
                                "borderWidth": 1,
                            }]
                        }
                        chart_json = json.dumps(chart_config)
                        ui.add_body_html(f'''
                        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                        <script>
                            const ctx = document.getElementById('category-pie-chart').getContext('2d');
                            new Chart(ctx, {{
                                type: 'pie',
                                data: {chart_json},
                                options: {{
                                    responsive: true,
                                    maintainAspectRatio: true,
                                    plugins: {{
                                        legend: {{
                                            position: 'bottom',
                                        }},
                                        tooltip: {{
                                            callbacks: {{
                                                label: function(context) {{
                                                    const label = context.label || '';
                                                    const value = '$' + context.parsed.toFixed(2).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ',');
                                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                                    const percent = ((context.parsed / total) * 100).toFixed(1);
                                                    return label + ': ' + value + ' (' + percent + '%)';
                                                }}
                                            }}
                                        }}
                                    }}
                                }}
                            }});
                        </script>
                        ''')

    generate_report_btn.on_click(generate_report)

    # Initial load of budget options
    refresh_budget_options()
