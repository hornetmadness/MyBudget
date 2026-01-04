"""Tests for category API endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_create_category(client: TestClient):
    """Test creating a new category."""
    response = client.post(
        "/categories/",
        json={
            "name": "Utilities",
            "description": "Electric, water, gas bills",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Utilities"
    assert data["description"] == "Electric, water, gas bills"
    assert data["enabled"] is True


def test_create_category_duplicate_name(client: TestClient):
    """Test creating a category with duplicate name fails."""
    # Create first category
    client.post(
        "/categories/",
        json={
            "name": "Utilities",
            "description": "Electric, water, gas bills",
        },
    )
    
    # Try to create another with same name
    response = client.post(
        "/categories/",
        json={
            "name": "Utilities",
            "description": "Different description",
        },
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_list_categories(client: TestClient):
    """Test listing all categories."""
    # Create some categories
    client.post(
        "/categories/",
        json={"name": "Utilities", "description": "Utility bills"},
    )
    client.post(
        "/categories/",
        json={"name": "Entertainment", "description": "Fun stuff"},
    )
    
    response = client.get("/categories/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    names = [c["name"] for c in data]
    assert "Utilities" in names
    assert "Entertainment" in names


def test_get_category(client: TestClient):
    """Test getting a specific category."""
    create_response = client.post(
        "/categories/",
        json={"name": "Food", "description": "Groceries and restaurants"},
    )
    category_id = create_response.json()["id"]
    
    response = client.get(f"/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == "Food"
    assert data["description"] == "Groceries and restaurants"


def test_get_category_not_found(client: TestClient):
    """Test getting a non-existent category."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/categories/{fake_uuid}")
    assert response.status_code == 404


def test_update_category(client: TestClient):
    """Test updating a category."""
    create_response = client.post(
        "/categories/",
        json={"name": "Transportation", "description": "Gas and car maintenance"},
    )
    category_id = create_response.json()["id"]
    
    response = client.patch(
        f"/categories/{category_id}",
        json={
            "description": "Gas, car maintenance, and insurance",
            "enabled": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Transportation"
    assert data["description"] == "Gas, car maintenance, and insurance"
    assert data["enabled"] is False


def test_delete_category(client: TestClient):
    """Test deleting a category."""
    create_response = client.post(
        "/categories/",
        json={"name": "Healthcare", "description": "Medical expenses"},
    )
    category_id = create_response.json()["id"]
    
    response = client.delete(f"/categories/{category_id}")
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = client.get(f"/categories/{category_id}")
    assert get_response.status_code == 404
