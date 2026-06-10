from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from nutritrack.api.dependencies import get_db_session, get_current_user
from nutritrack.db.repositories import MacroGoalRepository
from nutritrack.db.schemas import MacroGoalCreate, MacroGoalResponse
from nutritrack.db.models import UserModel
from nutritrack.core.exceptions import GoalNotSetError
from nutritrack.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=MacroGoalResponse, status_code=status.HTTP_201_CREATED)
def create_macro_goal(
    macro_goal: MacroGoalCreate,
    user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> MacroGoalResponse:

    repo = MacroGoalRepository(session)
    created_macro_goal = repo.create(
        user_id=user.id,
        calories=macro_goal.calories,
        protein_g=macro_goal.protein_g,
        carbs_g=macro_goal.carbs_g,
        fat_g=macro_goal.fat_g,
        effective_date=macro_goal.effective_date,
    )

    return MacroGoalResponse.model_validate(created_macro_goal)


@router.get("/active", response_model=MacroGoalResponse)
def get_active_macro_goal(
    user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> MacroGoalResponse:

    repo = MacroGoalRepository(session)
    return MacroGoalResponse.model_validate(repo.get_active(user.id, date.today()))
