#!/usr/bin/env python3
"""
Load sample financial data into the MyBudget API.

This script populates the database with realistic mock data for testing and demonstration.
The API must be running before executing this script.

Usage:
    python scripts/load_sample_data.py [--api-url http://localhost:8000]
"""

import requests
import json
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
import argparse
import sys
from pathlib import Path

# Add parent directory to path so we can import app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.schemas import FrequencyEnum
from app.utils import utc_now


class BudgetAPIClient:
    """Client for interacting with the MyBudget API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _make_request(
        self, method: str, endpoint: str, data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PATCH":
                response = self.session.patch(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            raise

    def create_account(self, name: str, account_type: str, balance: float, description: str = None):
        """Create an account."""
        data = {"name": name, "account_type": account_type, "balance": balance}
        if description:
            data["description"] = description
        return self._make_request("POST", "/accounts/", data)

    def update_account(self, account_id: str, balance: float):
        """Update an account balance."""
        data = {"balance": balance}
        return self._make_request("PATCH", f"/accounts/{account_id}", data)

    def create_bill(
        self,
        account_id: str,
        name: str,
        budgeted_amount: float,
        frequency: str = FrequencyEnum.MONTHLY.value,
        payment_method: str = "manual",
        description: str = None,
        start_freq: str = None,
        category_id: str = None,
        transfer_account_id: str = None,
    ):
        """Create a bill."""
        data = {
            "name": name,
            "budgeted_amount": budgeted_amount,
            "frequency": frequency,
            "payment_method": payment_method,
            "description": description,
            "start_freq": start_freq,
        }
        if category_id:
            data["category_id"] = category_id
        if transfer_account_id:
            data["transfer_account_id"] = transfer_account_id

        return self._make_request("POST", f"/bills/{account_id}", data)

    def create_budget(
        self,
        name: str,
        start_date: str | None = None,
        end_date: str | None = None,
        description: str | None = None,
    ):
        """Create a budget."""
        data = {
            "name": name,
        }
        if start_date:
            data["start_date"] = start_date
        if end_date:
            data["end_date"] = end_date
        if description:
            data["description"] = description

        return self._make_request("POST", "/budgets/", data)

    def add_bill_to_budget(
        self,
        budget_id: str,
        bill_id: str,
        account_id: str,
        budgeted_amount: float,
        due_date: str | None = None,
        paid_amount: float = 0.0,
        paid_on: str | None = None,
    ):
        """Add a bill to a budget with a specific amount."""
        data = {
            "bill_id": bill_id,
            "account_id": account_id,
            "budgeted_amount": budgeted_amount,
            "paid_amount": paid_amount,
        }
        if due_date:
            data["due_date"] = due_date
        if paid_on:
            data["paid_on"] = paid_on
        return self._make_request("POST", f"/budgets/{budget_id}/bills", data)

    def update_budget(self, budget_id: str, data: Dict[str, Any]):
        """Update a budget."""
        return self._make_request("PATCH", f"/budgets/{budget_id}", data)

    def update_budget_bill(
        self,
        budget_id: str,
        budget_bill_id: str,
        data: Dict[str, Any],
    ):
        """Update a budget bill."""
        return self._make_request(
            "PATCH", f"/budgets/{budget_id}/bills/{budget_bill_id}", data
        )

    def create_category(self, name: str, description: str = None):
        """Create a category."""
        data = {"name": name}
        if description:
            data["description"] = description
        return self._make_request("POST", "/categories/", data)

    def create_income(
        self,
        account_id: str,
        name: str,
        amount: float,
        frequency: str = FrequencyEnum.MONTHLY.value,
        start_freq: str = None,
        description: str = None,
    ):
        """Create an income source."""
        data = {
            "name": name,
            "amount": amount,
            "frequency": frequency,
            "start_freq": start_freq,
        }
        if description:
            data["description"] = description
        return self._make_request("POST", f"/income/?account_id={account_id}", data)


def load_sample_data(api_url: str = "http://localhost:8000"):
    """Load comprehensive sample financial data."""
    client = BudgetAPIClient(api_url)
    now = utc_now()

    print("🚀 Starting to load sample data...")
    print(f"📡 API URL: {api_url}\n")

    try:
        # Create primary account
        print("💳 Creating accounts...")
        primary_checking = client.create_account(
            "Primary Checking", "checking", 15500.75, "Primary checking account for daily expenses"
        )
        print(f"   ✓ Created: {primary_checking['name']} (${primary_checking['balance']})")

        savings_account = client.create_account(
            "Emergency Savings", "savings", 25000.00, "Emergency fund for unexpected expenses"
        )
        print(
            f"   ✓ Created: {savings_account['name']} (${savings_account['balance']})"
        )

        investment_account = client.create_account(
            "Investment Account", "investment", 50000.00, "Long-term investment portfolio"
        )
        print(
            f"   ✓ Created: {investment_account['name']} (${investment_account['balance']})"
        )

        account_id = primary_checking["id"]
        
        # Store all accounts for random selection
        all_accounts = [primary_checking, savings_account, investment_account]

        # Add income to accounts (creates credit transactions automatically)
        print("\n💰 Adding income to accounts...")
        for account in all_accounts:
            new_balance = account["balance"] + 500.00
            client.update_account(account["id"], new_balance)
            print(f"   ✓ Added $500 income to {account['name']} (new balance: ${new_balance:,.2f})")

        # Create categories
        print("\n🏷️  Creating bill categories...")
        housing_category = client.create_category(
            "Housing", "Rent, mortgage, and home maintenance"
        )
        print(f"   ✓ Created category: {housing_category['name']}")

        utilities_category = client.create_category(
            "Utilities", "Electric, water, gas, trash, internet"
        )
        print(f"   ✓ Created category: {utilities_category['name']}")

        food_category = client.create_category(
            "Food & Groceries", "Groceries, restaurants, and delivery"
        )
        print(f"   ✓ Created category: {food_category['name']}")

        transportation_category = client.create_category(
            "Transportation", "Fuel, maintenance, insurance, and transit"
        )
        print(f"   ✓ Created category: {transportation_category['name']}")

        insurance_category = client.create_category(
            "Insurance", "Health, auto, home, and life insurance"
        )
        print(f"   ✓ Created category: {insurance_category['name']}")

        entertainment_category = client.create_category(
            "Entertainment", "Streaming, movies, music, and hobbies"
        )
        print(f"   ✓ Created category: {entertainment_category['name']}")

        healthcare_category = client.create_category(
            "Healthcare", "Medical expenses, prescriptions, dental, and vision"
        )
        print(f"   ✓ Created category: {healthcare_category['name']}")

        personal_care_category = client.create_category(
            "Personal Care", "Haircuts, gym, wellness, and self-care"
        )
        print(f"   ✓ Created category: {personal_care_category['name']}")

        shopping_category = client.create_category(
            "Shopping", "Clothing, household items, and general purchases"
        )
        print(f"   ✓ Created category: {shopping_category['name']}")

        dining_category = client.create_category(
            "Dining & Takeout", "Restaurants, bars, coffee, and food delivery"
        )
        print(f"   ✓ Created category: {dining_category['name']}")

        subscriptions_category = client.create_category(
            "Subscriptions & Memberships", "Apps, software, memberships, and recurring services"
        )
        print(f"   ✓ Created category: {subscriptions_category['name']}")

        education_category = client.create_category(
            "Education", "Tuition, courses, books, and learning materials"
        )
        print(f"   ✓ Created category: {education_category['name']}")

        pets_category = client.create_category(
            "Pets", "Pet food, vet bills, toys, and supplies"
        )
        print(f"   ✓ Created category: {pets_category['name']}")

        gifts_donations_category = client.create_category(
            "Gifts & Donations", "Gifts, charitable donations, and contributions"
        )
        print(f"   ✓ Created category: {gifts_donations_category['name']}")

        misc_category = client.create_category(
            "Cash & Misc", "Cash withdrawals and miscellaneous"
        )
        print(f"   ✓ Created category: {misc_category['name']}")

        # Create income sources
        print("\n💸 Creating income sources...")
        income_start_freq = (now - timedelta(days=90)).isoformat()  # Start 90 days ago
        
        paycheck_income = client.create_income(
            primary_checking["id"],
            "Biweekly Paycheck",
            3500.00,
            frequency="biweekly",
            start_freq=income_start_freq,
            description="Regular biweekly employment income"
        )
        print(f"   ✓ Created income: {paycheck_income['name']} (${paycheck_income['amount']} biweekly)")

        cash_income = client.create_income(
            primary_checking["id"],
            "Cash Income",
            500.00,
            frequency="monthly",
            start_freq=income_start_freq,
            description="Miscellaneous cash earnings"
        )
        print(f"   ✓ Created income: {cash_income['name']} (${cash_income['amount']} monthly)")

        # Create bills tied directly to the account
        print("\n📋 Creating bills...")
        due_date_next_month = (now + timedelta(days=30)).isoformat()
        
        # Payment method options for random selection
        payment_methods = ["manual", "automatic", "other"]

        bills = []
        start_freq_date = (now - timedelta(days=90)).isoformat()  # Start 90 days ago

        bills.append(
            client.create_bill(
                random.choice(all_accounts)["id"],
                "Mortgage Payment",
                2500.00,
                "monthly",
                payment_method=random.choice(payment_methods),
                description="30-year fixed mortgage",
                start_freq=start_freq_date,
                            category_id=housing_category["id"],
            )
        )
        print(f"   ✓ Created bill: {bills[-1]['name']} (${bills[-1]['budgeted_amount']})")

        bills.append(
            client.create_bill(
                random.choice(all_accounts)["id"],
                "Electric Bill",
                150.00,
                "monthly",
                payment_method=random.choice(payment_methods),
                description="Monthly electricity",
                                category_id=utilities_category["id"],
                start_freq=start_freq_date,
            )
        )
        print(f"   ✓ Created bill: {bills[-1]['name']} (${bills[-1]['budgeted_amount']})")

        bills.append(
            client.create_bill(
                random.choice(all_accounts)["id"],
                "Water Bill",
                75.00,
                "monthly",
                payment_method=random.choice(payment_methods),
                description="Monthly water",
                                category_id=utilities_category["id"],
                start_freq=start_freq_date,
            )
        )
        print(f"   ✓ Created bill: {bills[-1]['name']} (${bills[-1]['budgeted_amount']})")

        bills.append(
            client.create_bill(
                random.choice(all_accounts)["id"],
                "Gas Bill",
                100.00,
                "monthly",
                payment_method=random.choice(payment_methods),
                description="Monthly gas",
                                category_id=utilities_category["id"],
                start_freq=start_freq_date,
            )
        )
        print(f"   ✓ Created bill: {bills[-1]['name']} (${bills[-1]['budgeted_amount']})")

        bills.append(
            client.create_bill(
                random.choice(all_accounts)["id"],
                "Weekly Groceries",
                140.00,
                "weekly",
                payment_method=random.choice(payment_methods),
                description="Regular grocery shopping",
                    category_id=food_category["id"],
                start_freq=start_freq_date,
            )
        )
        print(f"   ✓ Created bill: {bills[-1]['name']} (${bills[-1]['budgeted_amount']})")

        bills.append(
            client.create_bill(
                random.choice(all_accounts)["id"],
                "Car Maintenance",
                150.00,
                "monthly",
                payment_method=random.choice(payment_methods),
                description="Oil changes and repairs",
                                category_id=transportation_category["id"],
                start_freq=start_freq_date,
            )
        )
        print(f"   ✓ Created bill: {bills[-1]['name']} (${bills[-1]['budgeted_amount']})")

        bills.append(
            client.create_bill(
                random.choice(all_accounts)["id"],
                "Health Insurance",
                350.00,
                "monthly",
                payment_method=random.choice(payment_methods),
                description="Employee health insurance",
                                category_id=insurance_category["id"],
                start_freq=start_freq_date,
            )
        )
        print(f"   ✓ Created bill: {bills[-1]['name']} (${bills[-1]['budgeted_amount']})")

        bills.append(
            client.create_bill(
                random.choice(all_accounts)["id"],
                "Auto Insurance",
                125.00,
                "monthly",
                payment_method=random.choice(payment_methods),
                description="Vehicle insurance premium",
                                category_id=insurance_category["id"],
                start_freq=start_freq_date,
            )
        )
        print(f"   ✓ Created bill: {bills[-1]['name']} (${bills[-1]['budgeted_amount']})")

        bills.append(
            client.create_bill(
                random.choice(all_accounts)["id"],
                "Streaming Services",
                27.98,
                "monthly",
                payment_method=random.choice(payment_methods),
                description="Combined Netflix and Spotify",
                                category_id=entertainment_category["id"],
                start_freq=start_freq_date,
            )
        )
        print(f"   ✓ Created bill: {bills[-1]['name']} (${bills[-1]['budgeted_amount']})")

        bills.append(
            client.create_bill(
                random.choice(all_accounts)["id"],
                "Cash Withdrawal",
                100.00,
                FrequencyEnum.ALWAYS.value,
                payment_method=random.choice(payment_methods),
                description="Regular cash withdrawals",
                start_freq=start_freq_date,
                    category_id=misc_category["id"],
            )
        )
        print(f"   ✓ Created bill: {bills[-1]['name']} (${bills[-1]['budgeted_amount']})")

        # Create a transfer bill (from checking to savings account)
        bills.append(
            client.create_bill(
                primary_checking["id"],
                "Monthly Transfer to Savings",
                300.00,
                "always",
                payment_method="transfer",
                description="Automatic transfer to savings account",
                start_freq=start_freq_date,
                transfer_account_id=savings_account["id"],
            )
        )
        print(f"   ✓ Created bill: {bills[-1]['name']} (${bills[-1]['budgeted_amount']}) [Transfer to {savings_account['name']}]")

        # Store budget bills for reference
        budget_bills_created = []  # Store budget bills for reference

        # Create budgets
        print("\n📊 Creating budgets...")
        budgets = []

        # Create budget for current month
        current_month = now.month
        current_year = now.year
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        # Create start_date and end_date for current month (first half: days 1-15)
        current_month_start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_start = current_month_start_dt.isoformat()
        current_month_mid = (current_month_start_dt + timedelta(days=15)).isoformat()

        # Create budget for current month (first half)
        budgets.append(
            client.create_budget(
                f"{month_names[current_month - 1]} {current_year} (1 of 2)",
                start_date=current_month_start,
                end_date=current_month_mid,
                description="First half of month budget",
            )
        )
        print(f"   ✓ Created budget: {budgets[-1]['name']}")

        # Add bills to current month budget (first half) with some paid
        budget_bills_added = 0
        for i, bill in enumerate(bills[:7]):  # Add first 7 bills to budget (including transfer)
            # Due dates for first half: days 3-10
            due_date = (current_month_start_dt + timedelta(days=2 + i)).isoformat()
            
            # First, create the budget bill without payment info
            budget_bill = client.add_bill_to_budget(
                budgets[0]["id"],
                bill["id"],
                account_id,
                bill["budgeted_amount"],
                due_date=due_date,
            )
            budget_bills_created.append(budget_bill)
            
            # Then, if this bill should be paid, update it to mark as paid (triggers transaction)
            if i < 4:  # First 4 bills are paid
                client.update_budget_bill(
                    budgets[0]["id"],
                    budget_bill["id"],
                    {
                        "paid_amount": bill["budgeted_amount"],
                        "paid_on": (now - timedelta(days=i)).isoformat(),
                    },
                )
            budget_bills_added += 1
        print(f"   ✓ Added {budget_bills_added} bills to {month_names[current_month - 1]} (1 of 2) budget (4 paid)")

        # Create budget for current month (second half: days 16-end)
        current_month_mid_dt = current_month_start_dt + timedelta(days=15)
        current_month_mid_start = current_month_mid_dt.isoformat()
        # Get last day of current month
        if current_month == 12:
            current_month_end_dt = now.replace(year=current_year + 1, month=1, day=1) - timedelta(days=1)
        else:
            current_month_end_dt = now.replace(month=current_month + 1, day=1) - timedelta(days=1)
        current_month_end = current_month_end_dt.isoformat()

        budgets.append(
            client.create_budget(
                f"{month_names[current_month - 1]} {current_year} (2 of 2)",
                start_date=current_month_mid_start,
                end_date=current_month_end,
                description="Second half of month budget",
            )
        )
        print(f"   ✓ Created budget: {budgets[-1]['name']}")

        # Add bills to current month budget (second half) with some paid
        budget_bills_added = 0
        for i, bill in enumerate(bills[3:8]):  # Add bills 3-7 to second half (different bills)
            due_date = (current_month_start_dt + timedelta(days=16 + i)).isoformat()
            budget_bill = client.add_bill_to_budget(
                budgets[1]["id"],
                bill["id"],
                account_id,
                bill["budgeted_amount"],
                due_date=due_date,
            )
            budget_bills_added += 1
        print(f"   ✓ Added {budget_bills_added} bills to budget (0 paid)")

        # Transactions are automatically created when bills are marked as paid

        # Create budget for next month (first half)
        next_month = current_month + 1 if current_month < 12 else 1
        next_year = current_year if current_month < 12 else current_year + 1
        
        # Create start_date and end_date for next month (first half: days 1-15)
        if next_month == 1:
            next_month_start_dt = now.replace(year=next_year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month_start_dt = now.replace(month=next_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month_start = next_month_start_dt.isoformat()
        next_month_mid = (next_month_start_dt + timedelta(days=15)).isoformat()

        budgets.append(
            client.create_budget(
                f"{month_names[next_month - 1]} {next_year} (1 of 2)",
                start_date=next_month_start,
                end_date=next_month_mid,
                description="First half of month budget",
            )
        )
        print(f"   ✓ Created budget: {budgets[-1]['name']}")

        # Add bills to next month budget (first half, all unpaid)
        budget_bills_added = 0
        for i, bill in enumerate(bills[:7]):  # Include transfer bill
            due_date = (next_month_start_dt + timedelta(days=5 + i)).isoformat()
            client.add_bill_to_budget(
                budgets[2]["id"],
                bill["id"],
                account_id,
                bill["budgeted_amount"],
                due_date=due_date,
            )
            budget_bills_added += 1
        print(f"   ✓ Added {budget_bills_added} bills to next month budget (0 paid)")

        # Create budget for next month (second half)
        next_month_mid_dt = next_month_start_dt + timedelta(days=15)
        next_month_mid_start = next_month_mid_dt.isoformat()
        # Get last day of next month
        if next_month == 12:
            next_month_end_dt = now.replace(year=next_year + 1, month=1, day=1) - timedelta(days=1)
        else:
            next_month_end_dt = now.replace(year=next_year, month=next_month + 1, day=1) - timedelta(days=1)
        next_month_end = next_month_end_dt.isoformat()

        budgets.append(
            client.create_budget(
                f"{month_names[next_month - 1]} {next_year} (2 of 2)",
                start_date=next_month_mid_start,
                end_date=next_month_end,
                description="Second half of month budget",
            )
        )
        print(f"   ✓ Created budget: {budgets[-1]['name']}")

        # Add bills to next month budget (second half, all unpaid)
        budget_bills_added = 0
        for i, bill in enumerate(bills[3:8]):  # Add bills 3-7
            due_date = (next_month_start_dt + timedelta(days=16 + i)).isoformat()
            client.add_bill_to_budget(
                budgets[3]["id"],
                bill["id"],
                account_id,
                bill["budgeted_amount"],
                due_date=due_date,
            )
            budget_bills_added += 1
        print(f"   ✓ Added {budget_bills_added} bills to next month budget (0 paid)")

        # Create budgets for previous 2 months (disabled, all bills paid)
        for months_back in [1, 2]:
            prev_month = current_month - months_back
            prev_year = current_year
            if prev_month <= 0:
                prev_month += 12
                prev_year -= 1
            
            # Create start_date and end_date for previous month (first half: days 1-15)
            prev_month_start_dt = now.replace(year=prev_year, month=prev_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            prev_month_start = prev_month_start_dt.isoformat()
            prev_month_mid = (prev_month_start_dt + timedelta(days=15)).isoformat()

            budget = client.create_budget(
                f"{month_names[prev_month - 1]} {prev_year} (1 of 2)",
                start_date=prev_month_start,
                end_date=prev_month_mid,
                description="Previous month budget (completed)",
            )
            budgets.append(budget)
            print(f"   ✓ Created budget: {budget['name']}")

            # Mark budget as disabled/inactive
            client.update_budget(budget["id"], {"enabled": False})

            # Add bills to previous month budgets with all paid
            budget_bills_added = 0
            for i, bill in enumerate(bills[:7]):  # Include transfer bill
                # Calculate due date for previous month
                paid_date = (now - timedelta(days=30 * months_back - i)).isoformat()
                
                # First, create the budget bill without payment info
                budget_bill = client.add_bill_to_budget(
                    budget["id"],
                    bill["id"],
                    account_id,
                    bill["budgeted_amount"],
                    due_date=paid_date,
                )
                
                # Then, update it to mark as paid (triggers transaction)
                client.update_budget_bill(
                    budget["id"],
                    budget_bill["id"],
                    {
                        "paid_amount": bill["budgeted_amount"],
                        "paid_on": paid_date,
                    },
                )
                budget_bills_added += 1
            print(f"   ✓ Added {budget_bills_added} bills to {month_names[prev_month - 1]} (all paid)")

        print(f"\n✅ Loaded sample data")
        print(f"   Budgets: {len(budgets)}")
        print(f"   Transactions will be created automatically when bills are marked as paid or account balances are adjusted")
        print("\n💡 Tip: Visit http://localhost:8000/docs to explore the API")

    except Exception as e:
        print(f"\n❌ Error loading data: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Load sample financial data into the MyBudget API"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)",
    )

    args = parser.parse_args()

    try:
        load_sample_data(args.api_url)
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
