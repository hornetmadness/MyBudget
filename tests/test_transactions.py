from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi.testclient import TestClient

from app.models.schemas import FrequencyEnum
from app.utils import utc_now


def _create_account(client: TestClient):
    response = client.post(
        "/accounts/",
        json={"name": "Test Bank", "account_type": "checking", "balance": 1000.0},
    )
    assert response.status_code == 200
    return response.json()


def _create_bill(client: TestClient, account_id: str):
    now = utc_now()
    response = client.post(
        f"/bills/{account_id}",
        json={
            "name": "Electric Bill",
            "paid_amount": 150.0,
            "budgeted_amount": 175.0,
            "frequency": FrequencyEnum.MONTHLY.value,
            "start_freq": now.isoformat(),
            "due_date": (now + timedelta(days=5)).isoformat(),
            "paid_on": now.isoformat(),
        },
    )
    assert response.status_code == 200
    return response.json()


def _create_budget(client: TestClient):
    now = utc_now()
    response = client.post(
        "/budgets/",
        json={
            "name": "Test Budget",
            "start_date": now.isoformat(),
            "end_date": (now + timedelta(days=15)).isoformat(),
        },
    )
    assert response.status_code == 200
    return response.json()


def _create_budget_bill(client: TestClient, budget_id: str, bill_id: str, account_id: str):
    response = client.post(
        f"/budgets/{budget_id}/bills",
        json={
            "bill_id": bill_id,
            "account_id": account_id,
            "budgeted_amount": 175.0,
            "due_date": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
        },
    )
    assert response.status_code == 200
    return response.json()


def test_transaction_queries(client: TestClient):
    """Test transaction read-only endpoints."""
    account = _create_account(client)
    bill = _create_bill(client, account["id"])
    budget = _create_budget(client)
    budget_bill = _create_budget_bill(client, budget["id"], bill["id"], account["id"])

    # Mark the budget bill as paid to trigger transaction creation
    client.patch(
        f"/budgets/{budget['id']}/bills/{budget_bill['id']}",
        json={
            "paid_amount": 150.0,
            "paid_on": datetime.now(timezone.utc).isoformat(),
        },
    )

    # Get specific transaction by ID
    all_transactions = client.get("/transactions/").json()
    assert len(all_transactions) >= 1
    transaction = all_transactions[0]

    get_response = client.get(f"/transactions/{transaction['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == transaction["id"]

    # Get transactions by account
    account_list = client.get(f"/transactions/account/{account['id']}")
    assert account_list.status_code == 200
    assert len(account_list.json()) >= 1

    # Get transactions by budget bill
    budgetbill_list = client.get(f"/transactions/budgetbill/{budget_bill['id']}")
    assert budgetbill_list.status_code == 200
    assert len(budgetbill_list.json()) >= 1
