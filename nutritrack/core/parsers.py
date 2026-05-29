import csv

from pathlib import Path
from typing import Generator
from itertools import groupby

from nutritrack.core.models import Food, FoodEntry


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


def daily_totals(entries: list[FoodEntry]) -> Generator[dict, None, None]:
    sorted_entries = sorted(entries, key=lambda entry: entry.logged_date)
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
        }
