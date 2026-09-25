import os
from pathlib import Path


os.environ["DATABASE_URL"] = (
    "sqlite:///./data/test.db"
)

os.environ["SECRET_KEY"] = (
    "test-secret-key"
)

os.environ["USE_MOCK_AI"] = "true"


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "ok"
    )


def test_register_and_login():
    username = "testuser123"

    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": (
                "testuser123@example.com"
            ),
            "password": "password123",
        },
    )

    assert response.status_code in [
        200,
        400,
    ]

    login_response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    token_data = (
        login_response.json()
    )

    assert "access_token" in token_data


def test_home_recommendation():
    username = "planneruser"

    client.post(
        "/auth/register",
        json={
            "username": username,
            "email": (
                "planneruser@example.com"
            ),
            "password": "password123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    token = (
        login_response.json()
        ["access_token"]
    )

    response = client.post(
        "/generate-home",
        headers={
            "Authorization":
                f"Bearer {token}"
        },
        json={
            "room_type": "Living Room",
            "budget": 30000,
            "style": "Modern",
            "room_size": "Medium",
            "preferred_colors": (
                "White and blue"
            ),
            "additional_requirements": "",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["planner_type"] == "home"
    assert "items" in data
    assert "summary" in data


def teardown_module():
    test_db = Path(
        "data/test.db"
    )

    if test_db.exists():
        test_db.unlink()