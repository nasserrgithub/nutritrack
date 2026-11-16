from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from nutritrack.api.dependencies import get_current_user, get_db_session
from nutritrack.db.models import UserModel
from nutritrack.db.schemas import CoachAnswer, CoachQuestion
from nutritrack.knowledge.coach import ask_coach

router = APIRouter()


@router.post("/ask", response_model=CoachAnswer)
async def ask(
    body: CoachQuestion,
    user: UserModel = Depends(get_current_user),  # only logged-in users
    session: Session = Depends(get_db_session),
) -> CoachAnswer:
    return await ask_coach(body.question, session)
