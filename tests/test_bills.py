import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone


@pytest.fixture
def account_setup(client: TestClient):
    """Create an account for testing."""
    response = client.post(
        "/accounts/",
        json={
            "name": "My Checking",
            "account_type": "checking",
            "balance": 5000.0,
        },
    )
    return response.json()["id"]


def test_create_bill(client: TestClient, account_setup):
    """Test creating a new bill."""
    account_id = account_setup
    response = client.post(
        f"/bills/{account_id}",
        json={
            "name": "Electric Bill",
            "description": "Monthly electricity",
            "budgeted_amount": 150.0,
            "start_freq": "2025-01-01T00:00:00Z",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Electric Bill"
    assert data["budgeted_amount"] == 150.0
    assert data["enabled"] is True
    assert data["deleted"] is False


def test_create_bill_invalid_bank_account(client: TestClient):
    """Test creating bill with invalid bank account."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.post(
        f"/bills/{fake_uuid}",
        json={
            "name": "Electric Bill",
            "paid_amount": 125.50,
            "start_freq": "2025-01-01T00:00:00Z",
        },
    )
    assert response.status_code == 404
    assert "Account not found" in response.json()["detail"]


def test_list_bills(client: TestClient, account_setup):
    """Test listing all bills."""
    account_id = account_setup
    
    client.post(
        f"/bills/{account_id}",
        json={
            "name": "Electric Bill",
            "budgeted_amount": 125.50,
            "start_freq": "2025-01-01T00:00:00Z",
        },
    )
    client.post(
        f"/bills/{account_id}",
        json={
            "name": "Water Bill",
            "budgeted_amount": 50.0,
            "start_freq": "2025-01-01T00:00:00Z",
        },
    )
    
    response = client.get("/bills/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_bill(client: TestClient, account_setup):
    """Test getting a specific bill."""
    account_id = account_setup
    
    create_response = client.post(
        f"/bills/{account_id}",
        json={
            "name": "Electric Bill",
            "budgeted_amount": 125.50,
            "start_freq": "2025-01-01T00:00:00Z",
        },
    )
    bill_id = create_response.json()["id"]
    
    response = client.get(f"/bills/{bill_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Electric Bill"


def test_get_bill_not_found(client: TestClient):
    """Test getting a non-existent bill."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/bills/{fake_uuid}")
    assert response.status_code == 404


def test_get_bills_by_bank_account(client: TestClient, account_setup):
    """Test getting all bills for a specific account."""
    account_id = account_setup
    
    client.post(
        f"/bills/{account_id}",
        json={
            "name": "Electric Bill",
            "budgeted_amount": 125.50,
            "start_freq": "2025-01-01T00:00:00Z",
        },
    )
    client.post(
        f"/bills/{account_id}",
        json={
            "name": "Water Bill",
            "budgeted_amount": 50.0,
            "start_freq": "2025-01-01T00:00:00Z",
        },
    )
    
    response = client.get(f"/bills/account/{account_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_update_bill(client: TestClient, account_setup):
    """Test updating a bill."""
    account_id = account_setup
    
    create_response = client.post(
        f"/bills/{account_id}",
        json={
            "name": "Electric Bill",
            "budgeted_amount": 125.50,
            "start_freq": "2025-01-01T00:00:00Z",
        },
    )
    bill_id = create_response.json()["id"]
    
    response = client.patch(
        f"/bills/{bill_id}",
        json={"name": "Electric Bill Updated", "budgeted_amount": 150.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["budgeted_amount"] == 150.0


def test_delete_bill(client: TestClient, account_setup):
    """Test deleting a bill."""
    account_id = account_setup
    
    create_response = client.post(
        f"/bills/{account_id}",
        json={
            "name": "Electric Bill",
            "budgeted_amount": 125.50,
            "start_freq": "2025-01-01T00:00:00Z",
        },
    )
    bill_id = create_response.json()["id"]
    
    response = client.delete(f"/bills/{bill_id}")
    assert response.status_code == 200
    
    get_response = client.get(f"/bills/{bill_id}")
    assert get_response.status_code == 404


def test_bill_payment_method(client: TestClient, account_setup):
    """Test creating a bill with different payment methods."""
    account_id = account_setup
    
    # Test with payment_method specified
    for method in ["manual", "automatic", "other"]:
        response = client.post(
            f"/bills/{account_id}",
            json={
                "name": f"Bill with {method} payment",
                "budgeted_amount": 100.0,
                "payment_method": method,
                "start_freq": "2025-01-01T00:00:00Z",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["payment_method"] == method
    
    # Test default payment_method (manual)
    response = client.post(
        f"/bills/{account_id}",
        json={
            "name": "Bill with default payment method",
            "budgeted_amount": 100.0,
            "start_freq": "2025-01-01T00:00:00Z",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["payment_method"] == "manual"


def test_create_bill_with_category(client: TestClient, account_setup):
    """Test creating a bill with a category."""
    account_id = account_setup
    
    # Create a category first
    category_response = client.post(
        "/categories/",
        json={"name": "Utilities", "description": "Utility bills"},
    )
    category_id = category_response.json()["id"]
    
    # Create a bill with the category
    response = client.post(
        f"/bills/{account_id}",
        json={
            "name": "Electric Bill",
            "description": "Monthly electricity",
            "category_id": category_id,
            "budgeted_amount": 150.0,
            "start_freq": "2025-01-01T00:00:00Z",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Electric Bill"
    assert data["category_id"] == category_id


def test_create_bill_with_transfer(client: TestClient):
    """Test creating a bill with transfer payment method."""
    # Create two accounts: Checking and Savings
    checking_response = client.post(
        "/accounts/",
        json={
            "name": "My Checking",
            "account_type": "checking",
            "balance": 5000.0,
        },
    )
    checking_id = checking_response.json()["id"]
    
    savings_response = client.post(
        "/accounts/",
        json={
            "name": "My Savings",
            "account_type": "savings",
            "balance": 10000.0,
        },
    )
    savings_id = savings_response.json()["id"]
    
    # Create a bill on checking account with transfer to savings
    response = client.post(
        f"/bills/{checking_id}",
        json={
            "name": "Transfer to Savings",
            "description": "Automatic transfer to savings",
            "budgeted_amount": 500.0,
            "payment_method": "transfer",
            "transfer_account_id": savings_id,
            "start_freq": "2025-01-01T00:00:00Z",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Transfer to Savings"
    assert data["payment_method"] == "transfer"
    assert data["transfer_account_id"] == savings_id