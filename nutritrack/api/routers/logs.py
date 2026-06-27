from datetime import date
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from nutritrack.api.dependencies import get_db_session, get_current_user
from nutritrack.db.repositories import (
    FoodRepository,
    FoodEntryRepository,
)
from nutritrack.db.schemas import (
    FoodEntryCreate,
    FoodEntryResponse,
    NaturalMealLog,
)
from nutritrack.db.models import UserModel, FoodEntryModel
from nutritrack.ai.client import (
    lookup_food_macros,
    parse_natural_language_meal,
)
from nutritrack.api.routers.summary import orm_to_food_entry
from nutritrack.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


# Helpers
def build_entry_response(food_entry: FoodEntryModel) -> FoodEntryResponse:
    fe = orm_to_food_entry(food_entry)
    return FoodEntryResponse(
        id=food_entry.id,
        user_id=food_entry.user_id,
        food_id=food_entry.food_id,
        food_name=food_entry.food.name,
        weight_g=food_entry.weight_g,
        meal_slot=food_entry.meal_slot,
        logged_date=food_entry.logged_date,
        created_at=food_entry.created_at,
        calories=fe.scaled_calories(),
        protein_g=fe.scaled_protein(),
        carbs_g=fe.scaled_carbs(),
        fat_g=fe.scaled_fat(),
    )


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

    return build_entry_response(food_entry_created)


@router.get("/{log_date}", response_model=list[FoodEntryResponse])
def get_food_entry_by_date(
    log_date: date,
    user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[FoodEntryResponse]:

    food_entry_repo = FoodEntryRepository(session)
    food_entries = food_entry_repo.get_by_user_and_date(user.id, log_date)

    return [build_entry_response(food_entry) for food_entry in food_entries]


@router.post(
    "/natural",
    response_model=list[FoodEntryResponse],
    status_code=status.HTTP_201_CREATED,
)
async def log_natural_meal(
    meal_log: NaturalMealLog,
    user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[FoodEntryResponse]:

    food_repo = FoodRepository(session)
    food_entry_repo = FoodEntryRepository(session)
    food_entry_responses = []

    ai_lookup_foods = await parse_natural_language_meal(meal_log.text)
    for ai_lookup in ai_lookup_foods:
        food = food_repo.get_by_name(ai_lookup["food_name"])
        if not food:
            food = food_repo.create(
                name=ai_lookup["food_name"],
                protein_per_100g=ai_lookup["protein_per_100g"],
                carbs_per_100g=ai_lookup["carbs_per_100g"],
                fat_per_100g=ai_lookup["fat_per_100g"],
                fiber_per_100g=ai_lookup["fiber_per_100g"],
                source="ai_lookup",
            )

        food_entry_created = food_entry_repo.create(
            user_id=user.id,
            food_id=food.id,
            weight_g=ai_lookup["weight_g"],
            logged_date=meal_log.logged_date,
            meal_slot=meal_log.meal_slot,
        )

        food_entry_responses.append(build_entry_response(food_entry_created))

    return food_entry_responses
