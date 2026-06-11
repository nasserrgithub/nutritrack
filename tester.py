# AI
import asyncio
from nutritrack.ai.client import lookup_food_macros
from nutritrack.core.exceptions import FoodNotFoundError

from nutritrack.core.logger import setup_logging
setup_logging()

result = asyncio.run(lookup_food_macros("chicken adobo"))
print(result)

try:
    asyncio.run(lookup_food_macros("xyzabc123"))
except FoodNotFoundError as e:
    print(f"FoodNotFoundError caught: {e}")