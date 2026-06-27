import json
import anthropic
from anthropic.types import TextBlock
from nutritrack.api.settings import get_settings
from nutritrack.core.exceptions import AIServiceError, FoodNotFoundError
from nutritrack.ai.prompts import (
    food_macro_lookup_prompt,
    natural_language_meal_prompt,
    daily_suggestions_prompt,
)
from nutritrack.core.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return text


async def lookup_food_macros(food_name: str) -> dict:
    """
    Calls Anthropic API to get macros per 100g for a given food name.
    Returns a dict with protein_per_100g, carbs_per_100g, fat_per_100g, fiber_per_100g.
    Raises FoodNotFoundError if the food is unrecognizable.
    Raises AIServiceError if the API call fails.
    """
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    try:
        response = await client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=256,
            messages=[{"role": "user", "content": food_macro_lookup_prompt(food_name)}],
        )
        block = response.content[0]
        if not isinstance(block, TextBlock):
            raise AIServiceError(f"Unexpected response block type: {type(block)}")
        text = _strip_markdown_fences(block.text)
        result = json.loads(text)

        err_msg = result.get("error")
        if err_msg:
            if "unknown_food" in err_msg:
                raise FoodNotFoundError(food_name)
            raise Exception(err_msg)

        logger.info(
            f"Done lookup for macros of {food_name}. "
            f"protein_per_100g: {result['protein_per_100g']} "
            f"carbs_per_100g: {result['carbs_per_100g']} "
            f"fat_per_100g: {result['fat_per_100g']} "
            f"fiber_per_100g: {result['fiber_per_100g']} "
        )
        return result
    except FoodNotFoundError:
        raise
    except Exception as exc:
        raise AIServiceError(str(exc))


async def parse_natural_language_meal(user_input: str) -> list[dict]:
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    try:
        response = await client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=256,
            messages=[
                {"role": "user", "content": natural_language_meal_prompt(user_input)}
            ],
        )
        block = response.content[0]
        if not isinstance(block, TextBlock):
            raise AIServiceError(f"Unexpected response block type: {type(block)}")
        text = _strip_markdown_fences(block.text)
        result = json.loads(text)

        if not result:
            raise FoodNotFoundError(user_input)

        logger.info(f"Done lookup for macros of user input: {user_input}")
        for food in result:
            logger.info(
                f"food_name: {food['food_name']} "
                f"protein_per_100g: {food['protein_per_100g']} "
                f"carbs_per_100g: {food['carbs_per_100g']} "
                f"fat_per_100g: {food['fat_per_100g']} "
                f"fiber_per_100g: {food['fiber_per_100g']} "
            )
        return result
    except FoodNotFoundError:
        raise
    except Exception as exc:
        raise AIServiceError(str(exc))


async def get_food_suggestions(
    remaining: dict, goal: dict, available_foods_macros: list[dict]
) -> list[dict]:
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    try:
        response = await client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": daily_suggestions_prompt(
                        remaining, goal, available_foods_macros
                    ),
                }
            ],
        )
        block = response.content[0]
        if not isinstance(block, TextBlock):
            raise AIServiceError(f"Unexpected response block type: {type(block)}")
        text = _strip_markdown_fences(block.text)
        result = json.loads(text)

        if not result:
            raise AIServiceError("No food suggestions/results returned")

        logger.info("Done fetching food suggestions")
        for food in result:
            logger.info(
                f"food_name: {food['food_name']} "
                f"weight_g: {food['weight_g']} "
                f"calories: {food['calories']} "
                f"protein_g: {food['protein_g']} "
                f"carbs_g: {food['carbs_g']} "
                f"fat_g: {food['fat_g']} "
            )

        return result
    except AIServiceError:
        raise
    except Exception as exc:
        raise AIServiceError(str(exc))
