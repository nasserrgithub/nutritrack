from datetime import date, timedelta
from nutritrack.worker.celery_app import celery_app
from nutritrack.db.database import get_session
from nutritrack.db.repositories import (
    FoodEntryRepository,
    MacroGoalRepository,
    UserRepository,
)
from nutritrack.api.routers.summary import orm_to_food_entry
from nutritrack.worker.utils import send_email, render_html
from nutritrack.core.parsers import MacroAggregator
from nutritrack.core.models import MacroGoal
from nutritrack.core.logger import get_logger

logger = get_logger(__name__)


# Helpers
def get_date_range(end_date: date, lookback_days: int) -> tuple[date, date]:
    start_date = end_date - timedelta(days=lookback_days)
    return start_date, end_date


@celery_app.task
def generate_weekly_report(user_id: int) -> dict:
    start, end = get_date_range(date.today(), lookback_days=7)

    with get_session() as session:
        food_entry_repo = FoodEntryRepository(session)
        food_entries_db = food_entry_repo.get_by_user_and_date_range(
            user_id, start, end
        )
        food_entries = [
            orm_to_food_entry(food_entry_db) for food_entry_db in food_entries_db
        ]

        macro_goal_repo = MacroGoalRepository(session)
        macro_goal_db = macro_goal_repo.get_active(user_id, end)
        macro_goal = MacroGoal(
            calories=macro_goal_db.calories,
            protein_g=macro_goal_db.protein_g,
            carbs_g=macro_goal_db.carbs_g,
            fat_g=macro_goal_db.fat_g,
            effective_date=macro_goal_db.effective_date,
        )

        user_repo = UserRepository(session)
        user = user_repo.get_by_id(user_id)
        user_email = user.email

    macro_aggregator = MacroAggregator(food_entries, macro_goal)
    remaining_macros = macro_aggregator.remaining_macros(today_only=False)
    summary = dict(
        email=user_email,
        start_date=start,
        end_date=end,
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

    logger.info(f"Summary of the weekly report: {summary}")
    return summary


@celery_app.task
def send_weekly_report_email(user_id: int) -> dict:
    summary = generate_weekly_report(user_id)
    email = summary["email"]

    html = render_html(summary_data=summary)
    send_email(to=email, subject="Weekly Macros Summary Report", html_body=html)
    return {"status": "sent", "user_id": user_id, "email": email}
