from dataclasses import dataclass, field
from typing import Optional
from datetime import date

from nutritrack.core.utils import calculate_calories, calculate_macro_ratio
from nutritrack.core.exceptions import InvalidMacroError, GoalNotSetError


@dataclass
class Food:
    name: str
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    fiber_per_100g: Optional[float] = None
    source: str = "manual"

    def __post_init__(self):
        for field_name, value in [
            ("protein_per_100g", self.protein_per_100g),
            ("carbs_per_100g", self.carbs_per_100g),
            ("fat_per_100g", self.fat_per_100g),
            ("fiber_per_100g", self.fiber_per_100g),
        ]:
            if value is not None and value < 0:
                raise InvalidMacroError(field_name, value)

    def calories_per_100g(self) -> float:
        return calculate_calories(
            self.protein_per_100g,
            self.carbs_per_100g,
            self.fat_per_100g,
            self.fiber_per_100g,
        )


@dataclass
class FoodEntry:
    food: Food
    weight_g: float
    logged_date: date = field(default_factory=date.today)
    meal_slot: str = "unspecified"

    def __post_init__(self):
        if self.weight_g <= 0:
            raise InvalidMacroError("weight_g", self.weight_g)

    def scaled_protein(self) -> float:
        return round(self.food.protein_per_100g * self.weight_g / 100, 2)

    def scaled_carbs(self) -> float:
        return round(self.food.carbs_per_100g * self.weight_g / 100, 2)

    def scaled_fat(self) -> float:
        return round(self.food.fat_per_100g * self.weight_g / 100, 2)

    def scaled_calories(self) -> float:
        return round(self.food.calories_per_100g() * self.weight_g / 100, 2)


@dataclass(frozen=True)
class MacroGoal:
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    effective_date: date = field(default_factory=date.today)

    def __post_init__(self):
        if self.calories <= 0:
            raise GoalNotSetError()

        for field_name, value in [
            ("protein_g", self.protein_g),
            ("carbs_g", self.carbs_g),
            ("fat_g", self.fat_g),
        ]:
            if value < 0:
                raise InvalidMacroError(field_name, value)

    def protein_ratio(self) -> float:
        return calculate_macro_ratio(self.protein_g, self.calories, 4)

    def carbs_ratio(self) -> float:
        return calculate_macro_ratio(self.carbs_g, self.calories, 4)

    def fat_ratio(self) -> float:
        return calculate_macro_ratio(self.fat_g, self.calories, 9)


@dataclass(frozen=True)
class WeightEntry:
    weight_kg: float
    logged_date: date = field(default_factory=date.today)
    note: Optional[str] = None


@dataclass
class User:
    id: int
    email: str
    weight_kg: float
    height_cm: float
    age: int
    gender: str
    activity_level: str = "sedentary"
    is_active: bool = True
    created_date: date = field(default_factory=date.today)
