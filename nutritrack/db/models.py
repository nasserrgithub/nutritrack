from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from nutritrack.db.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(72), nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    activity_level: Mapped[str] = mapped_column(
        String(20), nullable=False, default="sedentary"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # relationships
    food_entries: Mapped[list["FoodEntryModel"]] = relationship(back_populates="user")
    macro_goals: Mapped[list["MacroGoalModel"]] = relationship(back_populates="user")
    weight_entries: Mapped[list["WeightEntryModel"]] = relationship(
        back_populates="user"
    )


class FoodModel(Base):
    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    protein_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    fat_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    fiber_per_100g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # relationships
    food_entries: Mapped[list["FoodEntryModel"]] = relationship(back_populates="food")


class FoodEntryModel(Base):
    __tablename__ = "food_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    food_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("foods.id"), nullable=False, index=True
    )
    weight_g: Mapped[float] = mapped_column(Float, nullable=False)
    meal_slot: Mapped[str] = mapped_column(String(20), default="unspecified")
    logged_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # relationships
    user: Mapped["UserModel"] = relationship(back_populates="food_entries")
    food: Mapped["FoodModel"] = relationship(back_populates="food_entries")


class MacroGoalModel(Base):
    __tablename__ = "macro_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    calories: Mapped[float] = mapped_column(Float, nullable=False)
    protein_g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_g: Mapped[float] = mapped_column(Float, nullable=False)
    fat_g: Mapped[float] = mapped_column(Float, nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # relationships
    user: Mapped["UserModel"] = relationship(back_populates="macro_goals")


class WeightEntryModel(Base):
    __tablename__ = "weight_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    logged_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # relationships
    user: Mapped["UserModel"] = relationship(back_populates="weight_entries")
