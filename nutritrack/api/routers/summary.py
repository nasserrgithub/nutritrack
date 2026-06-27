from fastapi import APIRouter, Depends
from datetime import date
from sqlalchemy.orm import Session

from nutritrack.db.models import FoodEntryModel, UserModel
from nutritrack.db.schemas import (
    DailySummaryResponse,
    SuggestionRequest,
    SuggestionResponse,
)
from nutritrack.db.repositories import (
    FoodEntryRepository,
    MacroGoalRepository,
    FoodRepository,
)
from nutritrack.api.dependencies import get_current_user, get_db_session
from nutritrack.core.models import FoodEntry, Food, MacroGoal
from nutritrack.core.parsers import MacroAggregator
from nutritrack.core.logger import get_logger
from nutritrack.core.exceptions import FoodNotFoundError
from nutritrack.ai.client import lookup_food_macros, get_food_suggestions

logger = get_logger(__name__)
router = APIRouter()


def orm_to_food_entry(entry: FoodEntryModel) -> FoodEntry:
    food = Food(
        name=entry.food.name,
        protein_per_100g=entry.food.protein_per_100g,
        carbs_per_100g=entry.food.carbs_per_100g,
        fat_per_100g=entry.food.fat_per_100g,
        fiber_per_100g=entry.food.fiber_per_100g,
        source=entry.food.source,
    )
    return FoodEntry(
        food=food,
        weight_g=entry.weight_g,
        logged_date=entry.logged_date,
        meal_slot=entry.meal_slot,
    )


@router.get("/{summary_date}", response_model=DailySummaryResponse)
def get_daily_summary(
    summary_date: date,
    user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> DailySummaryResponse:

    # Fetch food entries
    food_entry_repo = FoodEntryRepository(session)
    food_entries_db = food_entry_repo.get_by_user_and_date(user.id, summary_date)
    food_entries = [orm_to_food_entry(food_entry) for food_entry in food_entries_db]

    # Fetch active macro goal
    macro_goal_repo = MacroGoalRepository(session)
    macro_goal_model = macro_goal_repo.get_active(user.id, summary_date)
    macro_goal = MacroGoal(
        calories=macro_goal_model.calories,
        protein_g=macro_goal_model.protein_g,
        carbs_g=macro_goal_model.carbs_g,
        fat_g=macro_goal_model.fat_g,
        effective_date=macro_goal_model.effective_date,
    )

    macro_aggregator = MacroAggregator(
        food_entries=food_entries, macro_goal=macro_goal, num_days=1
    )
    remaining_macros = macro_aggregator.remaining_macros()

    return DailySummaryResponse(
        date=summary_date,
        total_calories=macro_aggregator.total_calories,
        total_protein=macro_aggregator.total_protein,
        total_carbs=macro_aggregator.total_carbs,
        total_fat=macro_aggregator.total_fat,
        entry_count=macro_aggregator.entry_count,
        remaining_calories=remaining_macros["calories"],
        remaining_protein=remaining_macros["protein"],
        remaining_carbs=remaining_macros["carbs"],
        remaining_fat=remaining_macros["fat"],
    )


@router.post("/{summary_date}/suggestions", response_model=list[SuggestionResponse])
async def get_daily_suggestions(
    summary_date: date,
    suggestion_data: SuggestionRequest,
    user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[SuggestionResponse]:

    # Fetching food entries
    food_entry_repo = FoodEntryRepository(session)
    food_entries_db = food_entry_repo.get_by_user_and_date(user.id, summary_date)
    food_entries = [orm_to_food_entry(food_entry) for food_entry in food_entries_db]

    # Fetching macro goal
    macro_goal_repo = MacroGoalRepository(session)
    macro_goal_db = macro_goal_repo.get_active(user.id, summary_date)
    macro_goal = MacroGoal(
        calories=macro_goal_db.calories,
        protein_g=macro_goal_db.protein_g,
        carbs_g=macro_goal_db.carbs_g,
        fat_g=macro_goal_db.fat_g,
        effective_date=summary_date,
    )

    # Calculating remaining macros
    macro_aggregator = MacroAggregator(food_entries=food_entries, macro_goal=macro_goal)
    remaining = macro_aggregator.remaining_macros()

    # Food lookup (both in DB and via AI)
    food_repo = FoodRepository(session)
    available_foods = [
        food.strip()
        for food in suggestion_data.available_foods.split(",")
        if food.strip()
    ]
    available_foods_macros = []

    if (
        available_foods
    ):  # Check 0th element if not an empty string. If so, we skip the lookup and let AI service decide for the suggested foods
        for available_food in available_foods:
            food = food_repo.get_by_name(available_food)

            if not food:
                try:
                    ai_lookup = await lookup_food_macros(available_food)
                except FoodNotFoundError:
                    logger.info(
                        f"Skipping unrecognized food in suggestions input: {available_food}"
                    )
                    continue  # skip this one, keep processing the rest
                food = food_repo.create(
                    name=available_food,
                    protein_per_100g=ai_lookup["protein_per_100g"],
                    carbs_per_100g=ai_lookup["carbs_per_100g"],
                    fat_per_100g=ai_lookup["fat_per_100g"],
                    fiber_per_100g=ai_lookup["fiber_per_100g"],
                    source="ai_lookup",
                )

            available_foods_macros.append(
                {
                    "name": food.name,
                    "protein_per_100g": food.protein_per_100g,
                    "carbs_per_100g": food.carbs_per_100g,
                    "fat_per_100g": food.fat_per_100g,
                }
            )

    foods = await get_food_suggestions(
        remaining,
        {
            "calories": macro_goal.calories,
            "protein_g": macro_goal.protein_g,
            "carbs_g": macro_goal.carbs_g,
            "fat_g": macro_goal.fat_g,
        },
        available_foods_macros,
    )

    return [SuggestionResponse.model_validate(food) for food in foods]
