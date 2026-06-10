# from typing import Generator

# # 1 — database session for every endpoint that needs DB access
# def get_db_session() -> Generator[Session, None, None]:
#     ...

# # 2 — current authenticated user for every protected endpoint
# def get_current_user(token: str, session: Session) -> UserModel:
#     ...