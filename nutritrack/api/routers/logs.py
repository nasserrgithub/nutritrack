from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from nutritrack.api.dependencies import get_db_session, get_current_user
from nutritrack.db.repositories import FoodRepository, FoodEntryRepository
from nutritrack.db.schemas import FoodEntryCreate, FoodEntryResponse
from nutritrack.db.models import UserModel
from nutritrack.ai.client import lookup_food_macros
from nutritrack.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=FoodEntryResponse, status_code=status.HTTP_201_CREATED)
async def log_food_entry(
    food_entry: FoodEntryCreate,
    user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> FoodEntryResponse:

    food_repo = FoodRepository(session)
    food = food_repo.get_by_name(food_entry.food_name)

    if not food:
        ai_lookup = await lookup_food_macros(food_entry.food_name)
        food = food_repo.create(
            name=food_entry.food_name,
            protein_per_100g=ai_lookup["protein_per_100g"],
            carbs_per_100g=ai_lookup["carbs_per_100g"],
            fat_per_100g=ai_lookup["fat_per_100g"],
            fiber_per_100g=ai_lookup["fiber_per_100g"],
            source="ai_lookup",
        )

    food_entry_repo = FoodEntryRepository(session)
    food_entry_created = food_entry_repo.create(
        user_id=user.id,
        food_id=food.id,
        weight_g=food_entry.weight_g,
        logged_date=food_entry.logged_date,
        meal_slot=food_entry.meal_slot,
    )

    return FoodEntryResponse.model_validate(food_entry_created)


@router.get("/{log_date}", response_model=list[FoodEntryResponse])
def get_food_entry_by_date(
    log_date: date,
    user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[FoodEntryResponse]:

    food_entry_repo = FoodEntryRepository(session)
    food_entries = food_entry_repo.get_by_user_and_date(user.id, log_date)

    return [FoodEntryResponse.model_validate(food_entry) for food_entry in food_entries]
