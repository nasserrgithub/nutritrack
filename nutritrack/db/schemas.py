from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class FoodCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    protein_per_100g: float = Field(..., ge=0)
    carbs_per_100g: float = Field(..., ge=0)
    fat_per_100g: float = Field(..., ge=0)
    fiber_per_100g: Optional[float] = Field(default=None, ge=0)
    source: str = Field(default="manual", max_length=20)

    """
    example field_validator, but this is redundant since we already have set ge=0 constraint above

    @field_validator("protein_per_100g", "carbs_per_100g", "fat_per_100g")
    @classmethod
    def validate_macros(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Macro values cannot be negative")
        return v

    """


class FoodResponse(BaseModel):
    id: int
    name: str
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    fiber_per_100g: Optional[float]
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=72)
    weight_kg: float = Field(..., ge=0)
    height_cm: float = Field(..., ge=0)
    age: int = Field(..., ge=1, le=120)
    gender: str = Field(..., min_length=1, max_length=10)
    activity_level: str = Field(default="sedentary")

    @field_validator("email")
    @classmethod
    def validate_email(cls, email: str) -> str:
        if "@" not in email:
            raise ValueError("Invalid email, it should contain '@'")
        return email


class UserResponse(BaseModel):
    id: int
    email: str
    weight_kg: float
    height_cm: float
    age: int
    gender: str
    activity_level: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class FoodEntryCreate(BaseModel):
    food_name: str = Field(..., min_length=1, max_length=255)
    weight_g: float = Field(..., gt=0)
    meal_slot: str = Field(min_length=1, max_length=20, default="unspecified")
    logged_date: date = Field(default_factory=date.today)


class FoodEntryResponse(BaseModel):
    id: int
    user_id: int
    food_id: int
    weight_g: float
    meal_slot: str
    logged_date: date
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
