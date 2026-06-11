import time
import threading

from functools import wraps
from typing import Optional, Callable, Any
from nutritrack.core.exceptions import (
    InvalidMacroError,
)
from nutritrack.core.logger import get_logger

logger = get_logger(__name__)


def timed_log(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        logger.info(f"[OK]   {func.__name__} completed in {duration:.3f}s")
        return result

    return wrapper


def validate_macros(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        for macro_type, value in kwargs.items():
            if (
                macro_type.endswith("_g") or macro_type.endswith("_per_100g")
            ) and value < 0:
                raise InvalidMacroError(macro_type, value)
        result = func(*args, **kwargs)
        return result

    return wrapper


def retry(
    times: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempts = 0
            last_exception = Exception
            current_delay = delay
            while attempts < times:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as err:
                    if not isinstance(err, exceptions):
                        raise err
                    logger.warning(
                        f"Attempt {attempts + 1}/{times} failed with error: {err}"
                    )
                    last_exception = err
                    time.sleep(current_delay)
                    current_delay *= backoff
                    attempts += 1
            raise last_exception

        return wrapper

    return decorator


def rate_limit(calls_per_second: float = 1.0) -> Callable:
    last_called = [0.0]
    interval_s = 1 / calls_per_second
    lock = threading.Lock()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with lock:
                elapsed_time = time.perf_counter() - last_called[0]
                if elapsed_time < interval_s:
                    time.sleep(interval_s - elapsed_time)

                # alternative logic
                # wait = interval_s - elapsed
                # if wait > 0:
                #     time.sleep(wait)

                last_called[0] = time.perf_counter()

            return func(*args, **kwargs)

        return wrapper

    return decorator


@timed_log
@validate_macros
def calculate_calories(
    protein_g: float,
    carbs_g: float,
    fat_g: float,
    fiber_g: Optional[float] = None,
) -> float:
    """
    Calculate total calories from macronutrients.
    Protein: 4 kcal/g, Carbs: 4 kcal/g, Fat: 9 kcal/g.
    Fiber is subtracted from carbs if provided (net carbs).
    """
    net_carbs = carbs_g - (fiber_g or 0.0)
    return (protein_g * 4) + (net_carbs * 4) + (fat_g * 9)


def calculate_macro_ratio(
    grams: float,
    total_calories: float,
    kcal_per_gram: float,
) -> float:
    """Return what percentage of total calories this macro contributes."""
    if total_calories == 0:
        return 0.0
    return round((grams * kcal_per_gram / total_calories) * 100, 1)
