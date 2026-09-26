import sys
from pathlib import Path

import pytest

# Allow importing api-gateway/app.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "api-gateway"))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "CloudCart API Gateway is running!"


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["service"] == "api-gateway"
    assert data["status"] == "healthy"


def test_products(client, monkeypatch):
    class MockResponse:
        status_code = 200

        def json(self):
            return [
                {
                    "id": 1,
                    "name": "Laptop",
                    "price": 65000
                }
            ]

    monkeypatch.setattr(
        "app.requests.get",
        lambda url: MockResponse()
    )

    response = client.get("/products")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["name"] == "Laptop"


def test_users(client, monkeypatch):
    class MockResponse:
        status_code = 200

        def json(self):
            return [
                {
                    "id": 1,
                    "name": "Test User"
                }
            ]

    monkeypatch.setattr(
        "app.requests.get",
        lambda url: MockResponse()
    )

    response = client.get("/users")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["name"] == "Test User"


def test_get_orders(client, monkeypatch):
    class MockResponse:
        status_code = 200

        def json(self):
            return [
                {
                    "id": 1,
                    "user_id": 1,
                    "product_id": 1,
                    "status": "PLACED"
                }
            ]

    monkeypatch.setattr(
        "app.requests.get",
        lambda url: MockResponse()
    )

    response = client.get("/orders")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["status"] == "PLACED"


def test_create_order(client, monkeypatch):
    class MockResponse:
        status_code = 201

        def json(self):
            return {
                "id": 1,
                "user_id": 1,
                "product_id": 1,
                "status": "PLACED"
            }

    monkeypatch.setattr(
        "app.requests.post",
        lambda url, json: MockResponse()
    )

    response = client.post(
        "/orders",
        json={
            "user_id": 1,
            "product_id": 1
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["status"] == "PLACED"
    assert data["user_id"] == 1
    assert data["product_id"] == 1
