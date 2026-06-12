class FoodNotFoundError(Exception):
    """Raised when a food item is not found in the database."""

    def __init__(self, food_name: str):
        super().__init__(f"Food '{food_name}' was not found in the database")


class UserNotFoundError(Exception):
    """Raised when a user is not found in the database."""

    def __init__(self, user_id: int):
        super().__init__(f"User with id of {user_id} was not found in the database")


class InvalidMacroError(Exception):
    """Raised when a macro value is negative"""

    def __init__(self, field_name: str, value: float):
        super().__init__(
            f"Invalid macro value {value} for {field_name}. Macros should always be positive."
        )


class GoalNotSetError(Exception):
    """Raised when a user tries to log food but has not set a MacroGoal yet"""

    def __init__(self):
        super().__init__(
            "No macro goal has been set for this date. You can't log a food entry yet."
        )


class AIServiceError(Exception):
    """Raised when the AI service fails"""

    def __init__(self, message: str):
        super().__init__(f"Failed to communicate with the AI service: {message}")
