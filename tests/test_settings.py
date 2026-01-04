import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from main import app
from app.models.database import get_session


def test_get_settings_creates_default(client):
    """Test getting settings creates default if they don't exist."""
    response = client.get("/settings/")
    assert response.status_code == 200
    data = response.json()
    assert data["currency_symbol"]["value"] == "$"
    assert data["currency_symbol"]["display_name"] == "Currency Symbol"
    assert data["decimal_places"]["value"] == 2
    assert data["decimal_places"]["display_name"] == "Decimal Places"
    assert data["number_format"]["value"] == "comma"
    assert data["number_format"]["display_name"] == "Number Format"


def test_update_settings(client):
    """Test updating application settings."""
    payload = {
        "currency_symbol": "€",
        "decimal_places": 3,
        "number_format": "period",
    }
    response = client.patch("/settings/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["currency_symbol"]["value"] == "€"
    assert data["decimal_places"]["value"] == 3
    assert data["number_format"]["value"] == "period"


def test_get_updated_settings(client):
    """Test retrieving previously updated settings."""
    # First update settings
    payload = {
        "currency_symbol": "£",
        "decimal_places": 2,
        "number_format": "comma",
    }
    client.patch("/settings/", json=payload)
    
    # Then retrieve them
    response = client.get("/settings/")
    assert response.status_code == 200
    data = response.json()
    assert data["currency_symbol"]["value"] == "£"
    assert data["decimal_places"]["value"] == 2


def test_partial_update_settings(client):
    """Test partially updating settings."""
    # Get current settings first
    response = client.get("/settings/")
    original = response.json()
    
    # Update only currency
    payload = {"currency_symbol": "$"}
    response = client.patch("/settings/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["currency_symbol"]["value"] == "$"
    # Other fields should be unchanged
    assert data["decimal_places"]["value"] == original["decimal_places"]["value"]
