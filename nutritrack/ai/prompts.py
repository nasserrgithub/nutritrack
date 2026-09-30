import json


def food_macro_lookup_prompt(food_name: str) -> str:
    return f"""You are a nutrition database. Return ONLY raw JSON with no markdown, no code fences, no backticks, no explanation.

The response must start with {{ and end with }}.

Return the macros per 100g for: {food_name}

Always consider maximum macros estimates.

Required format:
{{"protein_per_100g": <float>, "carbs_per_100g": <float>, "fat_per_100g": <float>, "fiber_per_100g": <float or null>}}

If the food is unknown or unrecognizable, return:
{{"error": "unknown_food"}}""".strip()


def natural_language_meal_prompt(user_input: str) -> str:
    return f"""You are a precise nutrition database assistant. Return ONLY raw JSON — no markdown, no code fences, no backticks, no explanation.

Analyze this meal input and identify every individual food item:

{user_input}

Rules:
- If the user provides a weight (e.g. "99g rice"), use that EXACT weight as weight_g
- If no weight is given, estimate a reasonable serving size in grams
- For compound or homemade dishes listed with their ingredients, break them down into individual ingredients and distribute the total weight proportionally among them
- Provide macros PER 100G for each food (standard nutrition database format)
- Use maximum/conservative macro estimates
- food_name should be descriptive but concise
- fiber_per_100g can be null if unknown

Return a JSON list where each item follows this exact format:
{{"food_name": <string>, "weight_g": <float>, "protein_per_100g": <float>, "carbs_per_100g": <float>, "fat_per_100g": <float>, "fiber_per_100g": <float or null>}}

Example for "99g rice and 50g grilled chicken":
[
    {{"food_name": "white rice", "weight_g": 99, "protein_per_100g": 2.7, "carbs_per_100g": 28.2, "fat_per_100g": 0.3, "fiber_per_100g": 0.4}},
    {{"food_name": "grilled chicken breast", "weight_g": 50, "protein_per_100g": 31.0, "carbs_per_100g": 0.0, "fat_per_100g": 3.6, "fiber_per_100g": 0.0}}
]

Response must start with [ and end with ].
If no foods are mentioned, return [].
""".strip()


def daily_suggestions_prompt(
    remaining: dict, goal: dict, available_foods_macros: list[dict]
) -> str:
    foods_json = json.dumps(available_foods_macros)
    return f"""You are a nutrition database. Return ONLY raw JSON with no markdown, no code fences, no backticks, no explanation.

The user has told you the foods they currently have available foods with their corresponding macros: "{available_foods_macros}"

The format of the each element in the input available_foods_macros list is: 
{{
    "name": food name,
    "protein_per_100g": food.protein_per_100g,
    "carbs_per_100g": food.carbs_per_100g,
    "fat_per_100g": food.fat_per_100g,
}}

If given, use these input macros as basis of your computations of foods & macros to be suggested.

Your job is to suggest which of these available foods (or reasonable combinations of them)
would help the user hit their remaining macros. Prioritize suggestions that use ONLY
foods from the list above. If none of the available foods would meaningfully help close
the remaining gaps, you may suggest one or two reasonable additions. If the available_foods is empty, go give your own suggestions. Always consider maximum macros estimates.

The remaining macros are {remaining} and the goal to hit is: {goal} which are in python dict format and all measurements are in grams (except for calories).

Give 3-5 specific food suggestions with portion sizes that would help hit the remaining macros. If the number of available foods is more than 5, pick the 5 most reasonable ones.

Each food will be described in this format: {{
    "food_name": <food_name>, 
    "weight_g": <weight>, 
    "calories": <food calories based on suggested weight>, 
    "protein_g": <food protein in grams based on suggested weight>, 
    "carbs_g": <food carbs in grams based on suggested weight>, 
    "fat_g": <food fat in grams based on suggested weight>
}}

Return the list of these food suggestions in a single list.""".strip()
