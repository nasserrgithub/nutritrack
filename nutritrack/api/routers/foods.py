from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from nutritrack.core.logger import get_logger
from nutritrack.db.schemas import FoodResponse, FoodCreate
from nutritrack.db.repositories import FoodRepository
from nutritrack.db.models import UserModel
from nutritrack.api.dependencies import get_db_session, get_current_user
from nutritrack.core.exceptions import FoodNotFoundError

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=list[FoodResponse])
def get_foods(session: Session = Depends(get_db_session)) -> list[FoodResponse]:
    repo = FoodRepository(session)
    return [FoodResponse.model_validate(food) for food in repo.get_all()]


@router.get("/{food_id}", response_model=FoodResponse)
def get_food(food_id: int, session: Session = Depends(get_db_session)) -> FoodResponse:
    repo = FoodRepository(session)
    return FoodResponse.model_validate(repo.get_by_id(food_id))


@router.post("/", response_model=FoodResponse, status_code=status.HTTP_201_CREATED)
def create_food(
    food_data: FoodCreate,
    _user: UserModel = Depends(
        get_current_user
    ),  # gate only - not used, check first before setting up db session
    session: Session = Depends(get_db_session),
) -> FoodResponse:
    repo = FoodRepository(session)
    food = repo.create(
        name=food_data.name,
        protein_per_100g=food_data.protein_per_100g,
        carbs_per_100g=food_data.carbs_per_100g,
        fat_per_100g=food_data.fat_per_100g,
        fiber_per_100g=food_data.fiber_per_100g,
        source=food_data.source,
    )

    return FoodResponse.model_validate(food)
