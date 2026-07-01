import pytest
from datetime import date
from nutritrack.core.models import Food, FoodEntry, MacroGoal


@pytest.fixture
def sample_food() -> Food:
    return Food(
        name="chicken breast",
        protein_per_100g=31.0,
        carbs_per_100g=0.0,
        fat_per_100g=3.6,
    )


@pytest.fixture
def sample_food2() -> Food:
    return Food(
        name="boiled egg",
        protein_per_100g=12.5,
        carbs_per_100g=1.1,
        fat_per_100g=10.6,
    )


@pytest.fixture
def sample_food_entry(sample_food: Food) -> FoodEntry:
    return FoodEntry(
        food=sample_food,
        weight_g=150,
        logged_date=date.today(),
        meal_slot="lunch",
    )


@pytest.fixture
def sample_macro_goal() -> MacroGoal:
    return MacroGoal(
        calories=1800,
        protein_g=150,
        carbs_g=200,
        fat_g=60,
        effective_date=date.today(),
    )


@pytest.fixture
def sample_food_entries(sample_food: Food, sample_food2: Food) -> list[FoodEntry]:
    return [
        FoodEntry(
            food=sample_food, weight_g=100, logged_date=date.today(), meal_slot="lunch"
        ),
        FoodEntry(
            food=sample_food2, weight_g=150, logged_date=date.today(), meal_slot="lunch"
        ),
        FoodEntry(
            food=sample_food, weight_g=150, logged_date=date.today(), meal_slot="lunch"
        ),
    ]
