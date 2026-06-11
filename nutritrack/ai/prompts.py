def food_macro_lookup_prompt(food_name: str) -> str:
    return f"""You are a nutrition database. Return ONLY raw JSON with no markdown, no code fences, no backticks, no explanation.

The response must start with {{ and end with }}.

Return the macros per 100g for: {food_name}

Required format:
{{"protein_per_100g": <float>, "carbs_per_100g": <float>, "fat_per_100g": <float>, "fiber_per_100g": <float or null>}}

If the food is unknown or unrecognizable, return:
{{"error": "unknown_food"}}""".strip()


def natural_language_meal_prompt(user_input: str) -> str:
    return f"""You are a nutrition database. Return ONLY raw JSON with no markdown, no code fences, no backticks, no explanation. 

First, identify the foods from the this user input: {user_input}. Then for each food, identify the macros per 100g.

Each set of macros for a food should be contained inside this format: {{"food_name": <food_name>, "weight_g": <weight>, "protein_per_100g": <float>, "carbs_per_100g": <float>, "fat_per_100g": <float>, "fiber_per_100g": <float or null>}}

After getting macros for the list of foods, compile them in a single list like this format:
[
    {{"food_name": <food_name 1>, "weight_g": <weight>, "protein_per_100g": <float>, "carbs_per_100g": <float>, "fat_per_100g": <float>, "fiber_per_100g": <float or null>}},
    {{"food_name": <food_name 2>, "weight_g": <weight>, "protein_per_100g": <float>, "carbs_per_100g": <float>, "fat_per_100g": <float>, "fiber_per_100g": <float or null>}},
    {{"food_name": <food_name 3>, "weight_g": <weight>, "protein_per_100g": <float>, "carbs_per_100g": <float>, "fat_per_100g": <float>, "fiber_per_100g": <float or null>}}
]

Return this list of macros and response must start with [ and end with ].

If no foods are mentioned from the user_input, return an empty list, [].
"""
