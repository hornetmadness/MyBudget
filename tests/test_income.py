"""Tests for income endpoints."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta

from main import app
from app.models.database import Account, Income, create_db_and_tables
from app.models.schemas import FrequencyEnum

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Set up test database."""
    create_db_and_tables()
    yield


def test_create_income(client: TestClient):
    """Test creating an income source."""
    # Create an account first
    account = client.post(
        "/accounts/",
        json={
            "name": "Test Account",
            "account_type": '{"name": "Checking", "description": ""}',
            "balance": 5000.0,
        },
    )
    assert account.status_code == 200
    account_id = account.json()["id"]
    
    # Create income
    income = client.post(
        f"/income/?account_id={account_id}",
        json={
            "name": "Salary",
            "description": "Monthly salary",
            "amount": 5000.0,
            "frequency": "monthly",
            "start_freq": "2025-01-01T00:00:00Z",
        },
    )
    assert income.status_code == 201
    income_data = income.json()
    assert income_data["name"] == "Salary"
    assert income_data["amount"] == 5000.0
    assert income_data["frequency"] == "monthly"
    assert income_data["enabled"] == True


def test_get_income(client: TestClient):
    """Test retrieving income source."""
    # Create account and income
    account = client.post(
        "/accounts/",
        json={
            "name": "Test Account",
            "account_type": '{"name": "Checking", "description": ""}',
            "balance": 5000.0,
        },
    )
    account_id = account.json()["id"]
    
    income = client.post(
        f"/income/?account_id={account_id}",
        json={
            "name": "Freelance Income",
            "amount": 2000.0,
            "frequency": "weekly",
            "start_freq": "2025-01-01T00:00:00Z",
        },
    )
    income_id = income.json()["id"]
    
    # Retrieve income
    response = client.get(f"/income/{income_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Freelance Income"
    assert data["amount"] == 2000.0


def test_list_income(client: TestClient):
    """Test listing income sources."""
    # Create account
    account = client.post(
        "/accounts/",
        json={
            "name": "Test Account",
            "account_type": '{"name": "Checking", "description": ""}',
            "balance": 5000.0,
        },
    )
    account_id = account.json()["id"]
    
    # Create multiple income sources
    client.post(
        f"/income/?account_id={account_id}",
        json={"name": "Salary", "amount": 5000.0, "frequency": "monthly", "start_freq": "2025-01-01T00:00:00Z"},
    )
    client.post(
        f"/income/?account_id={account_id}",
        json={"name": "Bonus", "amount": 1000.0, "frequency": "yearly", "start_freq": "2025-01-01T00:00:00Z"},
    )
    
    # List all income
    response = client.get("/income/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_get_income_by_account(client: TestClient):
    """Test getting income sources for specific account."""
    # Create two accounts
    account1 = client.post(
        "/accounts/",
        json={
            "name": "Account 1",
            "account_type": '{"name": "Checking", "description": ""}',
            "balance": 5000.0,
        },
    ).json()
    
    account2 = client.post(
        "/accounts/",
        json={
            "name": "Account 2",
            "account_type": '{"name": "Savings", "description": ""}',
            "balance": 10000.0,
        },
    ).json()
    
    # Add income to both accounts
    client.post(
        f"/income/?account_id={account1['id']}",
        json={"name": "Salary", "amount": 5000.0, "frequency": "monthly", "start_freq": "2025-01-01T00:00:00Z"},
    )
    client.post(
        f"/income/?account_id={account2['id']}",
        json={"name": "Interest", "amount": 50.0, "frequency": "monthly", "start_freq": "2025-01-01T00:00:00Z"},
    )
    
    # Get income for account1
    response = client.get(f"/income/account/{account1['id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Salary"


def test_update_income(client: TestClient):
    """Test updating income source."""
    # Create account and income
    account = client.post(
        "/accounts/",
        json={
            "name": "Test Account",
            "account_type": '{"name": "Checking", "description": ""}',
            "balance": 5000.0,
        },
    ).json()
    
    income = client.post(
        f"/income/?account_id={account['id']}",
        json={
            "name": "Salary",
            "amount": 5000.0,
            "frequency": "monthly",
            "start_freq": "2025-01-01T00:00:00Z",
        },
    ).json()
    
    # Update income
    response = client.patch(
        f"/income/{income['id']}",
        json={"amount": 6000.0, "description": "Updated salary"},
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["amount"] == 6000.0
    assert updated["description"] == "Updated salary"


def test_delete_income(client: TestClient):
    """Test soft deleting income source."""
    # Create account and income
    account = client.post(
        "/accounts/",
        json={
            "name": "Test Account",
            "account_type": '{"name": "Checking", "description": ""}',
            "balance": 5000.0,
        },
    ).json()
    
    income = client.post(
        f"/income/?account_id={account['id']}",
        json={"name": "Salary", "amount": 5000.0, "frequency": "monthly", "start_freq": "2025-01-01T00:00:00Z"},
    ).json()
    
    # Delete income
    response = client.delete(f"/income/{income['id']}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/income/{income['id']}")
    assert get_response.status_code == 404


def test_cannot_add_income_to_disabled_account(client: TestClient):
    """Test that income cannot be added to disabled account."""
    # Create account
    account = client.post(
        "/accounts/",
        json={
            "name": "Disabled Account",
            "account_type": '{"name": "Checking", "description": ""}',
            "balance": 5000.0,
        },
    ).json()
    
    # Disable the account
    client.patch(
        f"/accounts/{account['id']}",
        json={"enabled": False},
    )
    
    # Try to add income
    response = client.post(
        f"/income/?account_id={account['id']}",
        json={"name": "Salary", "amount": 5000.0, "frequency": "monthly", "start_freq": "2025-01-01T00:00:00Z"},
    )
    assert response.status_code == 400
    assert "disabled" in response.json()["detail"].lower()


def test_income_frequency_options(client: TestClient):
    """Test various frequency options for income."""
    account = client.post(
        "/accounts/",
        json={
            "name": "Test Account",
            "account_type": '{"name": "Checking", "description": ""}',
            "balance": 5000.0,
        },
    ).json()
    
    frequencies = ["daily", "weekly", "biweekly", "monthly", "yearly"]
    
    for freq in frequencies:
        response = client.post(
            f"/income/?account_id={account['id']}",
            json={
                "name": f"Income {freq}",
                "amount": 1000.0,
                "frequency": freq,
                "start_freq": "2025-01-01T00:00:00Z",
            },
        )
        assert response.status_code == 201
        assert response.json()["frequency"] == freq
