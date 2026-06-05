from pathlib import Path
from nutritrack.core.logger import setup_logging, get_logger
from nutritrack.core.parsers import parse_food_csv
from nutritrack.db.repositories import FoodRepository
from nutritrack.db.database import get_session

setup_logging()
logger = get_logger(__name__)


def seed_foods():
    # Yield Food objects
    csv_file = Path(__file__).parent.parent.parent / "data" / "foods.csv"
    parsed_foods = parse_food_csv(csv_file)

    # Counters for skipped and inserted
    skipped = 0
    inserted = 0

    # Establish psql session for inserting all entries
    with get_session() as session:
        fr = FoodRepository(session)

        # Iterate through the yielded Food objects
        for parsed_food in parsed_foods:
            food_name = parsed_food.name

            # Skip if food already exists in the database
            if fr.get_by_name(food_name):
                logger.info(
                    f"Skipping, food {food_name} already exists in the database."
                )
                skipped += 1
                continue

            # Create food entry in the database
            fr.create(
                name=food_name,
                protein_per_100g=parsed_food.protein_per_100g,
                carbs_per_100g=parsed_food.carbs_per_100g,
                fat_per_100g=parsed_food.fat_per_100g,
                fiber_per_100g=parsed_food.fiber_per_100g,
                source=parsed_food.source,
            )
            inserted += 1

    # Log summary
    logger.info(
        f"Seeding has finished. Total entries inserted: {inserted}, skipped: {skipped}"
    )


if __name__ == "__main__":
    seed_foods()
