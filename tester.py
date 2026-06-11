###########################################
# AI Lookup Tests
###########################################
import asyncio
from nutritrack.ai.client import parse_natural_language_meal, get_food_suggestions
from nutritrack.core.logger import setup_logging

setup_logging()

### Food lookup
# result = asyncio.run(lookup_food_macros("chicken adobo"))
# print(result)
# try:
#     asyncio.run(lookup_food_macros("xyzabc123"))
# except FoodNotFoundError as e:
#     print(f"FoodNotFoundError caught: {e}")

### User input lookup (conversational input)
results = asyncio.run(
    parse_natural_language_meal("I ate a fried egg today and a banana for breakfast")
)
for item in results:
    print(item)

### Food suggestions
results = asyncio.run(
    get_food_suggestions(
        {"calories": 300, "protein_g": 30, "carbs_g": 100, "fat_g": 20},
        {"calories": 1800, "protein_g": 150, "carbs_g": 200, "fat_g": 60},
    )
)
for item in results:
    print(item)
