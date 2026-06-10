from typing import Optional
from sqlalchemy.orm import Session
from datetime import date
from nutritrack.db.models import FoodModel, UserModel, FoodEntryModel
from nutritrack.core.exceptions import FoodNotFoundError, UserNotFoundError
from nutritrack.core.logger import get_logger

logger = get_logger(__name__)


class FoodRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        name: str,
        protein_per_100g: float,
        carbs_per_100g: float,
        fat_per_100g: float,
        fiber_per_100g: Optional[float] = None,
        source: str = "manual",
    ) -> FoodModel:
        food = FoodModel(
            name=name,
            protein_per_100g=protein_per_100g,
            carbs_per_100g=carbs_per_100g,
            fat_per_100g=fat_per_100g,
            fiber_per_100g=fiber_per_100g,
            source=source,
        )
        self.session.add(food)
        self.session.flush()  # assigns id without committing
        logger.info(f"Created food: {food.name} (id={food.id})")
        return food

    def get_by_id(self, food_id: int) -> FoodModel:
        food = self.session.get(FoodModel, food_id)
        if not food:
            raise FoodNotFoundError(str(food_id))
        return food

    def get_by_name(self, name: str) -> Optional[FoodModel]:
        return (
            self.session.query(FoodModel)
            .filter(FoodModel.name.ilike(f"%{name}%"))
            .first()
        )

    def get_all(self) -> list[FoodModel]:
        return self.session.query(FoodModel).all()


class UserRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        email: str,
        hashed_password: str,
        weight_kg: float,
        height_cm: float,
        age: int,
        gender: str,
        activity_level: str = "sedentary",
        is_active: bool = True,
    ) -> UserModel:
        user = UserModel(
            email=email,
            hashed_password=hashed_password,
            weight_kg=weight_kg,
            height_cm=height_cm,
            age=age,
            gender=gender,
            activity_level=activity_level,
            is_active=is_active,
        )

        self.session.add(user)
        self.session.flush()  # assigns id without committing
        logger.info(f"Created user: {user.email} (id={user.id})")
        return user

    def get_by_id(self, user_id: int) -> UserModel:
        user = self.session.get(UserModel, user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user

    def get_by_email(self, email: str) -> Optional[UserModel]:
        user = self.session.query(UserModel).filter(UserModel.email == email).first()
        return user

    def get_all(self) -> list[UserModel]:
        return self.session.query(UserModel).all()

    def deactivate(self, user_id: int) -> UserModel:
        user = self.get_by_id(user_id)  # raises UserNotFoundError if not found
        user.is_active = False
        self.session.flush()
        logger.info(f"User {user.email} (id={user.id}) has been deactivated.")
        return user


class FoodEntryRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        user_id: int,
        food_id: int,
        weight_g: float,
        logged_date: date,
        meal_slot: str = "unspecified",
    ) -> FoodEntryModel:
        food_entry = FoodEntryModel(
            user_id=user_id,
            food_id=food_id,
            weight_g=weight_g,
            logged_date=logged_date,
            meal_slot=meal_slot,
        )

        self.session.add(food_entry)
        self.session.flush()
        logger.info(
            f"Created food entry: food_id={food_id}, user_id={user_id}, weight_g={weight_g}"
        )
        return food_entry

    def get_by_user(self, user_id: int) -> list[FoodEntryModel]:
        food_entry = (
            self.session.query(FoodEntryModel)
            .filter(FoodEntryModel.user_id == user_id)
            .all()
        )
        return food_entry

    def get_by_user_and_date(
        self, user_id: int, logged_date: date
    ) -> list[FoodEntryModel]:
        food_entry = (
            self.session.query(FoodEntryModel)
            .filter(FoodEntryModel.user_id == user_id)
            .filter(FoodEntryModel.logged_date == logged_date)
            .all()
        )
        return food_entry
