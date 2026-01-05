#!/usr/bin/env python3
"""
Bootstrap script for MyBudget application.

This script initializes the MyBudget application with:
- Default categories
- Application settings

Usage:
    python scripts/bootstrap.py [--api-url http://localhost:8000]
"""

import requests
import argparse
import sys
from pathlib import Path

# Add parent directory to path so we can import app module
sys.path.insert(0, str(Path(__file__).parent.parent))


class BudgetAPIClient:
    """Client for interacting with the MyBudget API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
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
            print(f"API request failed: {e}")
            raise

    def get_categories(self):
        """Get all categories."""
        return self._make_request("GET", "/categories/")

    def create_category(self, name: str, description: str = None):
        """Create a category."""
        data = {"name": name}
        if description:
            data["description"] = description
        return self._make_request("POST", "/categories/", data)

    def get_settings(self):
        """Get application settings."""
        return self._make_request("GET", "/settings/")

    def update_settings(self, settings: dict):
        """Update application settings."""
        return self._make_request("PATCH", "/settings/", settings)


def bootstrap_app(api_url: str = "http://localhost:8000"):
    """Bootstrap the application with default categories and settings."""
    client = BudgetAPIClient(api_url)

    print("🚀 Bootstrapping MyBudget application...")
    print(f"📡 API URL: {api_url}\n")

    try:
        # Get existing categories
        existing_categories = client.get_categories()
        existing_category_names = {cat['name'] for cat in existing_categories}

        # Create categories
        print("🏷️  Setting up bill categories...")
        categories_to_create = [
            ("Housing", "Rent, mortgage, and home maintenance"),
            ("Utilities", "Electric, water, gas, trash, internet"),
            ("Food & Groceries", "Groceries, restaurants, and delivery"),
            ("Transportation", "Fuel, maintenance, insurance, and transit"),
            ("Insurance", "Health, auto, home, and life insurance"),
            ("Entertainment", "Streaming, movies, music, and hobbies"),
            ("Healthcare", "Medical expenses, prescriptions, dental, and vision"),
            ("Personal Care", "Haircuts, gym, wellness, and self-care"),
            ("Shopping", "Clothing, household items, and general purchases"),
            ("Dining & Takeout", "Restaurants, bars, coffee, and food delivery"),
            ("Subscriptions & Memberships", "Apps, software, memberships, and recurring services"),
        ]

        created_count = 0
        skipped_count = 0
        for name, description in categories_to_create:
            if name in existing_category_names:
                print(f"   ⊙ Skipped (already exists): {name}")
                skipped_count += 1
            else:
                try:
                    category = client.create_category(name, description)
                    print(f"   ✓ Created: {category['name']}")
                    created_count += 1
                except Exception as e:
                    print(f"   ✗ Failed to create '{name}': {e}")

        # Initialize settings with defaults
        print("\n⚙️  Verifying application settings...")
        try:
            current_settings = client.get_settings()
            print(f"   ✓ Settings initialized:")
            print(f"      Currency Symbol: {current_settings.get('currency_symbol', '$')}")
            print(f"      Decimal Places: {current_settings.get('decimal_places', '2')}")
            print(f"      Number Format: {current_settings.get('number_format', 'comma')}")
            print(f"      Timezone: {current_settings.get('timezone', 'America/New_York')}")
            print(f"      Show Old Budgets: {current_settings.get('show_num_old_budgets', '3')}")
            print(f"      Prune Budgets After: {current_settings.get('prune_budgets_after_months', '24')} months")
        except Exception as e:
            print(f"   ⚠️  Could not verify settings: {e}")

        print(f"\n✅ Bootstrap complete")
        print(f"   Categories: {created_count} created, {skipped_count} already existed")
        print("\n💡 Tip: Visit http://localhost:8000/docs to explore the API")

    except Exception as e:
        print(f"\n❌ Error bootstrapping: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Bootstrap MyBudget application with default categories and settings"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)",
    )

    args = parser.parse_args()

    try:
        bootstrap_app(args.api_url)
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
