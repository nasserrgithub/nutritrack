from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from sqlalchemy.orm import Session
from nutritrack.db.database import SessionLocal
from nutritrack.db.models import UserModel
from nutritrack.core.logger import get_logger
from nutritrack.api.auth_utils import decode_access_token

logger = get_logger(__name__)

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") # Used for OAuth2PasswordBearer which expects JSON data for auth
# security = oath2_scheme
security = HTTPBearer()  # Used for HTTPAuthorizationCredentials


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_current_user(
    # token: str = Depends(security), session: Session = Depends(get_db_session)) -> UserModel: # Used for OAuth2PasswordBearer which expects JSON data for auth
    token: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_db_session),
) -> UserModel:

    token_ = token.credentials
    user_id = decode_access_token(token_)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = session.get(UserModel, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user
