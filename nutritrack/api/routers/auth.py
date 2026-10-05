from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.responses import RedirectResponse
from nutritrack.api.settings import get_settings

from nutritrack.api.dependencies import get_db_session, get_current_user
from nutritrack.api.auth_utils import (
    hash_password,
    create_access_token,
    verify_password,
)
from nutritrack.db.repositories import UserRepository
from nutritrack.db.schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    ProfileComplete,
)
from nutritrack.db.models import UserModel

from nutritrack.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


settings = get_settings()

# We use Google as the authorization server / identity provider
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    # discovery document
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/google")
async def login_via_google(request: Request):
    return await oauth.google.authorize_redirect(
        request,
        settings.google_redirect_uri,
    )


@router.get("/google/callback")
async def auth_via_google(
    request: Request,
    session: Session = Depends(get_db_session),
):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    google_id = user_info["sub"]
    email = user_info["email"]
    avatar_url = user_info.get("picture")

    repo = UserRepository(session)

    # check if user already exists by Google ID
    user = repo.get_by_google_id(google_id)

    if not user:
        # check if email already registered (via email/password)
        existing = repo.get_by_email(email)
        if existing:
            # link Google account to existing user
            existing.google_id = google_id
            existing.avatar_url = avatar_url
            session.flush()
            user = existing
        else:
            # create new Google user
            user = repo.create_google_user(
                email=email,
                google_id=google_id,
                avatar_url=avatar_url,
            )

    # issue JWT
    access_token = create_access_token(user.id)

    # redirect to frontend with token and profile_complete status
    frontend_url = settings.frontend_url
    return RedirectResponse(
        url=f"{frontend_url}/auth/callback?token={access_token}&profile_complete={str(user.profile_complete).lower()}&user_id={user.id}"
    )


@router.post("/profile", response_model=UserResponse)
def complete_profile(
    profile_data: ProfileComplete,
    user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> UserResponse:
    repo = UserRepository(session)
    updated_user = repo.complete_profile(
        user_id=user.id,
        weight_kg=profile_data.weight_kg,
        height_cm=profile_data.height_cm,
        age=profile_data.age,
        gender=profile_data.gender,
    )
    return UserResponse.model_validate(updated_user)


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
def login(
    user_credentials: LoginRequest, session: Session = Depends(get_db_session)
):  # Used for OAuth2PasswordBearer which expects JSON
    # def login(user_credentials: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db_session)): # Used for OAuth2PasswordRequestForm which expects form data
    repo = UserRepository(session)

    # check if email already exists
    existing = repo.get_by_email(
        user_credentials.email
    )  # Used for OAuth2PasswordBearer
    # existing = repo.get_by_email(user_credentials.username) # Used for OAuth2PasswordRequestForm
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized, user not found",
        )

    if not existing.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account uses Google login. Please sign in with Google.",
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


@router.get("/me", response_model=UserResponse)
def get_me(
    user: UserModel = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(user)
