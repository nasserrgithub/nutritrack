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

If no foods are mentioned from the user_input, return an empty list, []""".strip()


def daily_suggestions_prompt(remaining: dict, goal: dict) -> str:
    return f"""You are a nutrition database. Return ONLY raw JSON with no markdown, no code fences, no backticks, no explanation. 

Your job is to give suggestions on what types of food or meals the user can eat to hit the remaining macros.

The remaining macros are {remaining} and the goal to hit is: {goal} which are in python dict format and all measurements are in grams (except for calories).

Give 3-5 specific food suggestions with portion sizes that would help hit the remaining macros. 

Each food will be described in this format: {{"food_name": <food_name>, "weight_g": <weight>, "reason": <add a reason how this food helps to hit reamining macros>}}

Then return the list of these food suggestions in a single list in this format:
[
    {{
        "food_name 1": "test 1",
        "weight_g": 150,
        "reason": "High protein, low carb — helps close the 45g protein gap"
    }},
    {{
        "food_name 2": "grilled chicken breast",
        "weight_g": 150,
        "reason": "High protein, low carb — helps close the 45g protein gap"
    }},
    {{
        "food_name 3": "grilled chicken breast",
        "weight_g": 150,
        "reason": "High protein, low carb — helps close the 45g protein gap"
    }}
]
""".strip()
