from unittest.mock import patch, AsyncMock
from datetime import date


def test_register(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "weight_kg": 75.0,
            "height_cm": 175.0,
            "age": 28,
            "gender": "male",
        },
    )
    assert response.status_code == 201


def test_login(client, registered_user):
    response = client.post(
        "/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_log_natural_meal(client, registered_user):
    mock_parsed = [
        {
            "food_name": "chicken breast",
            "protein_per_100g": 31.0,
            "carbs_per_100g": 0.0,
            "fat_per_100g": 3.6,
            "fiber_per_100g": 0.0,
            "weight_g": 150.0,
        }
    ]

    with patch(
        "nutritrack.api.routers.logs.parse_natural_language_meal",
        new_callable=AsyncMock,
        return_value=mock_parsed,
    ):
        response = client.post(
            "/log/natural",
            json={
                "text": "I had chicken breast for lunch",
                "meal_slot": "lunch",
                "logged_date": str(date.today()),
            },
        )

    assert response.status_code == 201
    assert len(response.json()) == 1
    assert response.json()[0]["food_name"] == "chicken breast"
