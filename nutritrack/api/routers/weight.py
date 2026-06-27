from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from nutritrack.api.dependencies import get_db_session, get_current_user
from nutritrack.db.repositories import WeightEntryRepository
from nutritrack.db.schemas import WeightEntryCreate, WeightEntryResponse
from nutritrack.db.models import UserModel
from nutritrack.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=WeightEntryResponse, status_code=201)
def log_weight(
    weight_data: WeightEntryCreate,
    user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> WeightEntryResponse:
    repo = WeightEntryRepository(session)
    entry = repo.create(
        user_id=user.id,
        weight_kg=weight_data.weight_kg,
        logged_date=weight_data.logged_date,
        note=weight_data.note,
    )
    return WeightEntryResponse.model_validate(entry)


@router.get("/", response_model=list[WeightEntryResponse])
def get_weight_history(
    days: int = 30,
    user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[WeightEntryResponse]:
    end = date.today()
    start = end - timedelta(days=days)
    repo = WeightEntryRepository(session)
    entries = repo.get_by_user_and_date_range(user.id, start, end)
    return [WeightEntryResponse.model_validate(entry) for entry in entries]
