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


@pytest.fixture
def bill_setup(client: TestClient, account_setup):
    """Create a bill for testing."""
    account_id = account_setup
    response = client.post(
        f"/bills/{account_id}",
        json={
            "name": "Electric Bill",
            "budgeted_amount": 150.0,
            "start_freq": "2025-01-01T00:00:00Z",
        },
    )
    return response.json()["id"]


def test_create_budget(client: TestClient, account_setup):
    """Test creating a new budget."""
    start_date = "2025-01-01T00:00:00Z"
    end_date = "2025-01-31T23:59:59Z"
    response = client.post(
        "/budgets/",
        json={
            "name": "January 2025 Budget",
            "start_date": start_date,
            "end_date": end_date,
            "description": "Monthly budget for January",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "January 2025 Budget"
    assert data["start_date"] is not None
    assert data["description"] == "Monthly budget for January"
    assert data["enabled"] is True
    assert data["deleted"] is False


def test_list_budgets(client: TestClient, account_setup):
    """Test listing all budgets."""
    
    client.post(
        "/budgets/",
        json={
            "name": "January 2025 Budget",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z",
        },
    )
    client.post(
        "/budgets/",
        json={
            "name": "February 2025 Budget",
            "start_date": "2025-02-01T00:00:00Z",
            "end_date": "2025-02-28T23:59:59Z",
        },
    )
    
    response = client.get("/budgets/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_budget(client: TestClient, account_setup):
    """Test getting a specific budget."""
    
    create_response = client.post(
        "/budgets/",
        json={
            "name": "January 2025 Budget",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z",
        },
    )
    budget_id = create_response.json()["id"]
    
    response = client.get(f"/budgets/{budget_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "January 2025 Budget"
    assert data["start_date"] is not None


def test_get_budget_not_found(client: TestClient):
    """Test getting a non-existent budget."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/budgets/{fake_uuid}")
    assert response.status_code == 404


def test_update_budget(client: TestClient, account_setup):
    """Test updating a budget."""
    
    create_response = client.post(
        "/budgets/",
        json={
            "name": "January 2025 Budget",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z",
        },
    )
    budget_id = create_response.json()["id"]
    
    response = client.patch(
        f"/budgets/{budget_id}",
        json={"name": "Updated January Budget", "description": "New description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated January Budget"
    assert data["description"] == "New description"


def test_create_budget_with_overlap_fails(client: TestClient, account_setup):
    """Test that creating a budget that overlaps with an existing one fails."""
    # Create first budget
    client.post(
        "/budgets/",
        json={
            "name": "January 2025 Budget",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z",
        },
    )
    
    # Try to create overlapping budget - should fail
    response = client.post(
        "/budgets/",
        json={
            "name": "Mid-January Budget",
            "start_date": "2025-01-15T00:00:00Z",
            "end_date": "2025-02-15T23:59:59Z",
        },
    )
    assert response.status_code == 400
    assert "overlaps" in response.json()["detail"].lower()


def test_create_budget_no_overlap_adjacent_dates(client: TestClient, account_setup):
    """Test that creating budgets with adjacent dates (no overlap) succeeds."""
    # Create first budget
    client.post(
        "/budgets/",
        json={
            "name": "January 2025 Budget",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z",
        },
    )
    
    # Create adjacent budget - should succeed (Feb 1 starts when Jan 31 ends)
    response = client.post(
        "/budgets/",
        json={
            "name": "February 2025 Budget",
            "start_date": "2025-02-01T00:00:00Z",
            "end_date": "2025-02-28T23:59:59Z",
        },
    )
    assert response.status_code == 200


def test_update_budget_with_overlap_fails(client: TestClient, account_setup):
    """Test that updating a budget to overlap with another fails."""
    # Create two non-overlapping budgets
    budget1_resp = client.post(
        "/budgets/",
        json={
            "name": "January 2025 Budget",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z",
        },
    )
    budget1_id = budget1_resp.json()["id"]
    
    client.post(
        "/budgets/",
        json={
            "name": "March 2025 Budget",
            "start_date": "2025-03-01T00:00:00Z",
            "end_date": "2025-03-31T23:59:59Z",
        },
    )
    
    # Try to update budget1 to overlap with March budget - should fail
    response = client.patch(
        f"/budgets/{budget1_id}",
        json={
            "end_date": "2025-03-15T23:59:59Z"
        },
    )
    assert response.status_code == 400
    assert "would overlap" in response.json()["detail"].lower()


def test_delete_budget(client: TestClient, account_setup):
    """Test deleting a budget."""
    
    create_response = client.post(
        "/budgets/",
        json={
            "name": "January 2025 Budget",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z",
        },
    )
    budget_id = create_response.json()["id"]
    
    response = client.delete(f"/budgets/{budget_id}")
    assert response.status_code == 200
    
    get_response = client.get(f"/budgets/{budget_id}")
    assert get_response.status_code == 404


def test_delete_budget_with_bills_fails(client: TestClient, account_setup, bill_setup):
    """Deleting a budget that has bills should be blocked."""
    account_id = account_setup
    bill_id = bill_setup

    # Create budget
    budget_resp = client.post(
        "/budgets/",
        json={
            "name": "January 2025 Budget",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z",
        },
    )
    budget_id = budget_resp.json()["id"]

    # Attach a bill
    add_resp = client.post(
        f"/budgets/{budget_id}/bills",
        json={"bill_id": bill_id, "account_id": account_id},
    )
    assert add_resp.status_code == 200

    # Attempt delete should fail with 400
    delete_resp = client.delete(f"/budgets/{budget_id}")
    assert delete_resp.status_code == 400
    assert "Budget has bills" in delete_resp.json()["detail"]


def test_add_bill_to_budget(client: TestClient, account_setup, bill_setup):
    """Test adding a bill to a budget."""
    account_id = account_setup
    bill_id = bill_setup
    
    # Create budget
    budget_response = client.post(
        "/budgets/",
        json={
            "name": "January 2025 Budget",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z",
        },
    )
    budget_id = budget_response.json()["id"]
    
    # Add bill to budget
    response = client.post(
        f"/budgets/{budget_id}/bills",
        json={
            "bill_id": bill_id,
            "account_id": account_id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["budget_id"] == budget_id
    assert data["bill_id"] == bill_id
    assert data["account_id"] == account_id
    # Defaults to bill's budgeted_amount when omitted
    assert data["budgeted_amount"] == 150.0


def test_add_bill_to_budget_invalid_budget(client: TestClient, account_setup, bill_setup):
    """Test adding bill to non-existent budget."""
    account_id = account_setup
    bill_id = bill_setup
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    
    response = client.post(
        f"/budgets/{fake_uuid}/bills",
        json={
            "bill_id": bill_id,
            "account_id": account_id,
            "budgeted_amount": 150.0,
        },
    )
    assert response.status_code == 404
    assert "Budget not found" in response.json()["detail"]


def test_add_bill_to_budget_invalid_bill(client: TestClient, account_setup):
    """Test adding non-existent bill to budget."""
    account_id = account_setup
    
    # Create budget
    budget_response = client.post(
        "/budgets/",
        json={
            "name": "January 2025 Budget",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z",
        },
    )
    budget_id = budget_response.json()["id"]
    
    fake_bill_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.post(
        f"/budgets/{budget_id}/bills",
        json={
            "bill_id": fake_bill_uuid,
            "account_id": account_id,
            "budgeted_amount": 150.0,
        },
    )
    assert response.status_code == 404
    assert "Bill not found" in response.json()["detail"]


def test_get_budget_bills(client: TestClient, account_setup, bill_setup):
    """Test getting all bills in a budget."""
    account_id = account_setup
    bill_id = bill_setup
    
    # Create budget
    budget_response = client.post(
        "/budgets/",
        json={
            "name": "January 2025 Budget",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z",
        },
    )
    budget_id = budget_response.json()["id"]
    
    # Add bill to budget
    client.post(
        f"/budgets/{budget_id}/bills",
        json={
            "bill_id": bill_id,
            "account_id": account_id,
            "budgeted_amount": 150.0,
        },
    )
    
    # Get budget bills
    response = client.get(f"/budgets/{budget_id}/bills")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["bill_id"] == bill_id
    assert data[0]["budgeted_amount"] == 150.0


def test_update_budget_bill(client: TestClient, account_setup, bill_setup):
    """Test updating a budget-bill association."""
    account_id = account_setup
    bill_id = bill_setup
    
    # Create budget
    budget_response = client.post(
        "/budgets/",
        json={
            "name": "January 2025 Budget",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z",
        },
    )
    budget_id = budget_response.json()["id"]
    
    # Add bill to budget
    add_response = client.post(
        f"/budgets/{budget_id}/bills",
        json={
            "bill_id": bill_id,
            "account_id": account_id,
            "budgeted_amount": 150.0,
        },
    )
    budget_bill_id = add_response.json()["id"]
    
    # Update budget bill
    response = client.patch(
        f"/budgets/{budget_id}/bills/{budget_bill_id}",
        json={"budgeted_amount": 175.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["budgeted_amount"] == 175.0


def test_remove_bill_from_budget(client: TestClient, account_setup, bill_setup):
    """Test removing a bill from a budget."""
    account_id = account_setup
    bill_id = bill_setup
    
    # Create budget
    budget_response = client.post(
        "/budgets/",
        json={
            "name": "January 2025 Budget",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z",
        },
    )
    budget_id = budget_response.json()["id"]
    
    # Add bill to budget
    add_response = client.post(
        f"/budgets/{budget_id}/bills",
        json={
            "bill_id": bill_id,
            "account_id": account_id,
            "budgeted_amount": 150.0,
        },
    )
    budget_bill_id = add_response.json()["id"]
    
    # Remove bill from budget
    response = client.delete(f"/budgets/{budget_id}/bills/{budget_bill_id}")
    assert response.status_code == 200
    
    # Verify it's removed
    get_response = client.get(f"/budgets/{budget_id}/bills")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 0


def test_budget_with_multiple_bills(client: TestClient, account_setup):
    """Test a budget with multiple bills."""
    account_id = account_setup
    
    # Create multiple bills
    bill1_response = client.post(
        f"/bills/{account_id}",
        json={"name": "Electric Bill", "budgeted_amount": 150.0, "start_freq": "2025-01-01T00:00:00Z"},
    )
    bill1_id = bill1_response.json()["id"]
    
    bill2_response = client.post(
        f"/bills/{account_id}",
        json={"name": "Water Bill", "budgeted_amount": 60.0, "start_freq": "2025-01-01T00:00:00Z"},
    )
    bill2_id = bill2_response.json()["id"]
    
    # Create budget
    budget_response = client.post(
        "/budgets/",
        json={
            "name": "January 2025 Budget",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-01-31T23:59:59Z",
        },
    )
    budget_id = budget_response.json()["id"]
    
    # Add both bills
    client.post(
        f"/budgets/{budget_id}/bills",
        json={"bill_id": bill1_id, "account_id": account_id, "budgeted_amount": 150.0},
    )
    client.post(
        f"/budgets/{budget_id}/bills",
        json={"bill_id": bill2_id, "account_id": account_id, "budgeted_amount": 60.0},
    )
    
    # Get all bills in budget
    response = client.get(f"/budgets/{budget_id}/bills")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Verify total
    total = sum(bb["budgeted_amount"] for bb in data)
    assert total == 210.0
