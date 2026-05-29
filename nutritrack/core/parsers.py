import csv

from pathlib import Path
from typing import Generator
from itertools import groupby
from collections import Counter

from nutritrack.core.models import Food, FoodEntry, MacroGoal


def parse_food_csv(filepath: str | Path) -> Generator[Food, None, None]:
    """
    Lazily yields Food objects from a CSV file one row at a time.
    Never loads the entire file into memory.
    """
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield Food(
                name=row["name"],
                protein_per_100g=float(row["protein_per_100g"]),
                carbs_per_100g=float(row["carbs_per_100g"]),
                fat_per_100g=float(row["fat_per_100g"]),
                fiber_per_100g=(
                    float(row["fiber_per_100g"]) if row["fiber_per_100g"] else None
                ),
                source="csv",
            )


def get_daily_totals(entries: list[FoodEntry]) -> Generator[dict, None, None]:
    # sorted descending so first iteration = most recent day
    sorted_entries = sorted(entries, key=lambda entry: entry.logged_date, reverse=True)
    for logged_date, members in groupby(
        sorted_entries, key=lambda entry: entry.logged_date
    ):
        logged_date_entries = list(members)
        yield {
            "date": logged_date,
            "total_calories": sum(
                logged_date_entry.scaled_calories()
                for logged_date_entry in logged_date_entries
            ),
            "total_protein": sum(
                logged_date_entry.scaled_protein()
                for logged_date_entry in logged_date_entries
            ),
            "total_carbs": sum(
                logged_date_entry.scaled_carbs()
                for logged_date_entry in logged_date_entries
            ),
            "total_fat": sum(
                logged_date_entry.scaled_fat()
                for logged_date_entry in logged_date_entries
            ),
            "entry_count": len(logged_date_entries),
            "foods": [
                logged_date_entry.food for logged_date_entry in logged_date_entries
            ],
        }


class MacroAggregator:
    def __init__(self, food_entries: list[FoodEntry], macro_goal: MacroGoal) -> None:
        self.macro_goal = macro_goal
        self.total_calories = 0
        self.total_protein = 0
        self.total_carbs = 0
        self.total_fat = 0
        self.food_counter: Counter[str] = Counter()
        self.latest_food_entry = None
        is_first = True

        # Get total macros per entry date
        daily_totals = get_daily_totals(food_entries)

        # Increment macros per day intake
        for daily_total in daily_totals:

            # Store latest entry as this will be the basis for computation of remaining macros for the day
            if is_first:
                self.latest_food_entry = daily_total
                is_first = False

            self.total_calories += daily_total["total_calories"]
            self.total_protein += daily_total["total_protein"]
            self.total_carbs += daily_total["total_carbs"]
            self.total_fat += daily_total["total_fat"]

            # Count the foods per day
            for food in daily_total["foods"]:
                self.food_counter[food.name] += 1

    def remaining_macros(self, today_only: bool = True) -> dict:
        if today_only:
            if self.latest_food_entry is None:
                raise ValueError("No food entries logged yet")

            return {
                "calories": self.macro_goal.calories
                - self.latest_food_entry["total_calories"],
                "protein": self.macro_goal.protein_g
                - self.latest_food_entry["total_protein"],
                "carbs": self.macro_goal.carbs_g
                - self.latest_food_entry["total_carbs"],
                "fat": self.macro_goal.fat_g - self.latest_food_entry["total_fat"],
            }

        return {
            "calories": self.macro_goal.calories - self.total_calories,
            "protein": self.macro_goal.protein_g - self.total_protein,
            "carbs": self.macro_goal.carbs_g - self.total_carbs,
            "fat": self.macro_goal.fat_g - self.total_fat,
        }

    def top_foods(self, n: int = 5) -> list:
        return self.food_counter.most_common(n)
