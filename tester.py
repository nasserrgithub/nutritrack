###########################################
# AI Lookup Tests
###########################################
import asyncio
from nutritrack.ai.client import lookup_food_macros, parse_natural_language_meal
from nutritrack.core.exceptions import FoodNotFoundError
from nutritrack.core.logger import setup_logging

setup_logging()

# Food lookup
# result = asyncio.run(lookup_food_macros("chicken adobo"))
# print(result)
# try:
#     asyncio.run(lookup_food_macros("xyzabc123"))
# except FoodNotFoundError as e:
#     print(f"FoodNotFoundError caught: {e}")

# User input lookup (conversational input)
results = asyncio.run(
    parse_natural_language_meal("I ate a fried egg today and a banana for breakfast")
)
for item in results:
    print(item)