import pytest

from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from nutritrack.db.base import Base
from nutritrack.db.models import UserModel
from nutritrack.db.repositories import UserRepository
from nutritrack.api.settings import get_settings
from nutritrack.api.main import app
from nutritrack.api.auth_utils import hash_password
from nutritrack.api.dependencies import get_current_user, get_db_session
from nutritrack.core.models import Food, FoodEntry, MacroGoal

settings = get_settings()


# Generic Fixtures
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


# Fixtures for DB connection
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


# Fixtures for FastAPI endpoints tests
@pytest.fixture
def client(db_session):

    user_repo = UserRepository(db_session)
    test_user = user_repo.create(
        email="fixture_user@example.com",
        hashed_password=hash_password("testpass123"),
        weight_kg=75.0,
        height_cm=175.0,
        age=28,
        gender="male",
    )

    def override_get_current_user():
        return test_user

    def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db_session] = override_get_db_session

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    user_data = {
        "email": "fixture_user@example.com",
        "password": "testpass123",
        "weight_kg": 75.0,
        "height_cm": 175.0,
        "age": 28,
        "gender": "male",
    }
    client.post("/auth/register", json=user_data)
    return user_data
