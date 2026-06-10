from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from nutritrack.api.dependencies import get_db_session
from nutritrack.api.auth_utils import (
    hash_password,
    create_access_token,
    verify_password,
)
from nutritrack.db.repositories import UserRepository
from nutritrack.db.schemas import UserCreate, UserResponse, LoginRequest, TokenResponse
from nutritrack.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_data: UserCreate, session: Session = Depends(get_db_session)):
    repo = UserRepository(session)

    # check if email already exists
    existing = repo.get_by_email(user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # hash the password before storing
    hashed = hash_password(user_data.password)

    # create the user
    user = repo.create(
        email=user_data.email,
        weight_kg=user_data.weight_kg,
        height_cm=user_data.height_cm,
        age=user_data.age,
        gender=user_data.gender,
        activity_level=user_data.activity_level,
        hashed_password=hashed,
    )

    logger.info(f"New user registered: {user.email}")
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(user_credentials: LoginRequest, session: Session = Depends(get_db_session)):
    repo = UserRepository(session)

    # check if email already exists
    existing = repo.get_by_email(user_credentials.email)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized, user not found",
        )

    verified = verify_password(user_credentials.password, existing.hashed_password)
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized, incorrect password provided",
        )

    user_id = existing.id
    access_token = create_access_token(user_id)
    return TokenResponse(access_token=access_token)
