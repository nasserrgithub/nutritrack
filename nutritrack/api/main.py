from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nutritrack.core.logger import setup_logging, get_logger
from nutritrack.api.routers import auth, foods, logs, goals

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    setup_logging()
    logger.info("NutriTrack API starting up")
    yield
    # shutdown
    logger.info("NutriTrack API shutting down")


app = FastAPI(
    title="NutriTrack API",
    description="Food calorie and macro tracker",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,  prefix="/auth",  tags=["auth"])
app.include_router(foods.router, prefix="/foods", tags=["foods"])
app.include_router(logs.router,  prefix="/log",   tags=["logs"])
app.include_router(goals.router, prefix="/goals", tags=["goals"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "nutritrack"}