import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Generator
from nutritrack.core.logger import get_logger
from nutritrack.db.base import Base  # noqa: F401 — imported for Alembic to find it

logger = get_logger(__name__)

load_dotenv()


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return url


engine = create_engine(
    get_database_url(),
    echo=False,  # set True to see raw SQL in logs — useful for debugging
    pool_size=5,  # number of connections in the pool
    max_overflow=10,  # extra connections allowed beyond pool_size
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,  # we control commits manually
    autoflush=False,  # we control flushes manually
)

logger.info("Database engine created successfully")


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as err:
        session.rollback()
        raise err
    finally:
        session.close()
