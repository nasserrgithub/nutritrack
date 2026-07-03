from datetime import date, timedelta

from unittest.mock import patch, AsyncMock
from nutritrack.core.exceptions import AIServiceError, FoodNotFoundError


def test_food_not_found_returns_404(client):
    response = client.get("/foods/99999")
    assert response.status_code == 404


def test_ai_service_error(client):
    with patch(
        "nutritrack.api.routers.logs.parse_natural_language_meal",
        new_callable=AsyncMock,
        side_effect=AIServiceError("Service unavailable"),
    ):
        response = client.post(
            "/log/natural",
            json={
                "text": "I had chicken breast for lunch",
                "meal_slot": "lunch",
                "logged_date": str(date.today()),
            },
        )
        assert response.status_code == 503


def test_goal_not_set_error(client):
    response = client.get(f"/summary/{date.today() + timedelta(days=9999)}")
    assert response.status_code == 404
