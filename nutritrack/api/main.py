import time

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request as StarletteRequest

from nutritrack.core.logger import setup_logging, get_logger
from nutritrack.core.exceptions import (
    FoodNotFoundError,
    UserNotFoundError,
    GoalNotSetError,
    InvalidMacroError,
    AIServiceError,
)
from nutritrack.api.routers import auth, foods, logs, goals, summary, weight

logger = get_logger(__name__)


# App setup
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


# Middlewares
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: StarletteRequest, call_next: RequestResponseEndpoint
    ):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        logger.info(
            f"{request.method} {request.url.path} "
            f"→ {response.status_code} ({duration:.3f}s)"
        )
        return response


app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(FoodNotFoundError)
async def food_not_found_handler(request: Request, exc: FoodNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(GoalNotSetError)
async def goal_not_set_handler(request: Request, exc: GoalNotSetError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InvalidMacroError)
async def invalid_macro_handler(request: Request, exc: InvalidMacroError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(AIServiceError)
async def ai_service_handler(request: Request, exc: AIServiceError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(foods.router, prefix="/foods", tags=["foods"])
app.include_router(logs.router, prefix="/log", tags=["logs"])
app.include_router(goals.router, prefix="/goals", tags=["goals"])
app.include_router(summary.router, prefix="/summary", tags=["summary"])
app.include_router(weight.router, prefix="/weight", tags=["weight"])


# Default endpoints
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "nutritrack"}
