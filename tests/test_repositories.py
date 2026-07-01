import pytest
from datetime import date
from nutritrack.db.repositories import FoodRepository, UserRepository, FoodEntryRepository
from nutritrack.db.models import FoodModel, UserModel
from nutritrack.core.exceptions import FoodNotFoundError
from nutritrack.api.auth_utils import hash_password


def test_food_repository_create(db_session):
    repo = FoodRepository(db_session)
    food = repo.create(
        name="test food",
        protein_per_100g=10.0,
        carbs_per_100g=20.0,
        fat_per_100g=5.0,
        source="manual",
    )
    assert food.id is not None
    assert food.name == "test food"


def test_delete_own_entry_succeeds(db_session):
    user_repo = UserRepository(db_session)
    user = user_repo.create(
        email='test@gmail.com',
        hashed_password=hash_password('test123'),
        weight_kg=80.0,
        height_cm=170.0,
        age=25,
        gender='male'
    )

    food_repo = FoodRepository(db_session)
    food = food_repo.create(
        name="test food",
        protein_per_100g=10.0,
        carbs_per_100g=20.0,
        fat_per_100g=5.0,
        source="manual",
    )

    food_entry_repo = FoodEntryRepository(db_session)
    food_entry = food_entry_repo.create(
        user_id=user.id,
        food_id=food.id,
        weight_g=200,
        logged_date=date.today()
    )

    result = food_entry_repo.delete(food_entry.id, user.id)
    assert result is None


def test_delete_other_users_entry_raises(db_session):
    user_repo = UserRepository(db_session)
    user = user_repo.create(
        email='test@gmail.com',
        hashed_password=hash_password('test123'),
        weight_kg=80.0,
        height_cm=170.0,
        age=25,
        gender='male'
    )
    user2 = user_repo.create(
        email='tes2t@gmail.com',
        hashed_password=hash_password('test1232'),
        weight_kg=82.0,
        height_cm=172.0,
        age=22,
        gender='male'
    )

    food_repo = FoodRepository(db_session)
    food = food_repo.create(
        name="test food",
        protein_per_100g=10.0,
        carbs_per_100g=20.0,
        fat_per_100g=5.0,
        source="manual",
    )

    food_entry_repo = FoodEntryRepository(db_session)
    food_entry = food_entry_repo.create(
        user_id=user.id,
        food_id=food.id,
        weight_g=200,
        logged_date=date.today()
    )
    
    with pytest.raises(FoodNotFoundError):
        food_entry_repo.delete(food_entry.id, user2.id)