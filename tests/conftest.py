import pytest
from datetime import date, timedelta
from nutritrack.core.models import Food, FoodEntry, MacroGoal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from nutritrack.db.base import Base
from nutritrack.api.settings import get_settings

settings = get_settings()


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


@pytest.fixture
def multi_day_food_entries(sample_food: Food, sample_food2: Food) -> list[FoodEntry]:
    today = date.today()
    yesterday = today - timedelta(days=1)
    return [
        FoodEntry(food=sample_food, weight_g=100, logged_date=today, meal_slot="lunch"),
        FoodEntry(
            food=sample_food2, weight_g=150, logged_date=yesterday, meal_slot="dinner"
        ),
        FoodEntry(
            food=sample_food, weight_g=200, logged_date=yesterday, meal_slot="breakfast"
        ),
    ]


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()