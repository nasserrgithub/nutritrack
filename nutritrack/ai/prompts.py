def food_macro_lookup_prompt(food_name: str) -> str:
    return f"""You are a nutrition database. Return ONLY raw JSON with no markdown, no code fences, no backticks, no explanation.

The response must start with {{ and end with }}.

Return the macros per 100g for: {food_name}

Required format:
{{"protein_per_100g": <float>, "carbs_per_100g": <float>, "fat_per_100g": <float>, "fiber_per_100g": <float or null>}}

If the food is unknown or unrecognizable, return:
{{"error": "unknown_food"}}""".strip()
