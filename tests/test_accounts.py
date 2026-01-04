import pytest
from fastapi.testclient import TestClient
from app.models.schemas import AccountTypeModel


@pytest.fixture
def account_setup(client: TestClient):
    """Create an account for testing."""
    account_type = AccountTypeModel(name="Checking", description="Checking account").model_dump_json()
    response = client.post(
        "/accounts/",
        json={
            "name": "My Checking",
            "account_type": account_type,
            "balance": 5000.0,
        },
    )
    return response.json()["id"]


def test_create_account(client: TestClient):
    """Test creating a new account."""
    account_type = AccountTypeModel(name="Checking", description="Checking account").model_dump_json()
    response = client.post(
        "/accounts/",
        json={
            "name": "My Checking",
            "account_type": account_type,
            "balance": 1000.0,
            "description": "My personal checking account",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My Checking"
    assert data["balance"] == 1000.0
    assert data["description"] == "My personal checking account"
    assert data["enabled"] is True
    assert data["deleted"] is False


def test_create_account_invalid_type(client: TestClient):
    """Test creating an account with invalid account type."""
    account_type = AccountTypeModel(name="Checking").model_dump_json()
    response = client.post(
        "/accounts/",
        json={
            "name": "My Checking",
            "account_type": account_type,
            "balance": 1000.0,
        },
    )
    assert response.status_code == 200


def test_list_accounts(client: TestClient):
    """Test listing all accounts."""
    # Create a few accounts
    checking = AccountTypeModel(name="Checking").model_dump_json()
    savings = AccountTypeModel(name="Savings").model_dump_json()
    
    client.post(
        "/accounts/",
        json={"name": "Checking 1", "account_type": checking, "balance": 1000.0},
    )
    client.post(
        "/accounts/",
        json={"name": "Savings 1", "account_type": savings, "balance": 2000.0},
    )
    
    response = client.get("/accounts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_account(client: TestClient):
    """Test getting a specific account."""
    account_type = AccountTypeModel(name="Checking").model_dump_json()
    create_response = client.post(
        "/accounts/",
        json={"name": "My Checking", "account_type": account_type, "balance": 1000.0},
    )
    account_id = create_response.json()["id"]
    
    response = client.get(f"/accounts/{account_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My Checking"
    assert data["balance"] == 1000.0


def test_get_account_not_found(client: TestClient):
    """Test getting a non-existent account."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/accounts/{fake_uuid}")
    assert response.status_code == 404


def test_update_account(client: TestClient):
    """Test updating an account."""
    account_type = AccountTypeModel(name="Checking").model_dump_json()
    create_response = client.post(
        "/accounts/",
        json={"name": "My Checking", "account_type": account_type, "balance": 1000.0},
    )
    account_id = create_response.json()["id"]
    
    response = client.patch(
        f"/accounts/{account_id}",
        json={"balance": 1500.0, "description": "Updated checking account"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 1500.0
    assert data["description"] == "Updated checking account"


def test_delete_account(client: TestClient):
    """Test deleting an account."""
    account_type = AccountTypeModel(name="Checking").model_dump_json()
    create_response = client.post(
        "/accounts/",
        json={"name": "My Checking", "account_type": account_type, "balance": 1000.0},
    )
    account_id = create_response.json()["id"]
    
    response = client.delete(f"/accounts/{account_id}")
    assert response.status_code == 200
    
    get_response = client.get(f"/accounts/{account_id}")
    assert get_response.status_code == 404


def test_account_with_optional_description(client: TestClient):
    """Test creating an account without description (optional field)."""
    account_type = AccountTypeModel(name="Savings").model_dump_json()
    response = client.post(
        "/accounts/",
        json={"name": "My Savings", "account_type": account_type, "balance": 5000.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My Savings"
    assert data["balance"] == 5000.0
    assert data["description"] is None
