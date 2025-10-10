"""Service layer encapsulating meal plan logic."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from database import MealPlan, Recipe, meal_plan_recipe


class MealPlanService:
    """Business logic for CRUD operations on meal plans."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def get_meal_plans(self, filters: Optional[Dict[str, Any]] = None) -> List[MealPlan]:
        filters = filters or {}
        query = self.session.query(MealPlan).order_by(MealPlan.created_at.desc())

        limit = filters.get("limit")
        if limit:
            try:
                query = query.limit(int(limit))
            except (TypeError, ValueError):  # pragma: no cover - defensive
                pass

        return query.all()

    def get_meal_plan_by_id(self, meal_plan_id: int) -> Optional[MealPlan]:
        return self.session.get(MealPlan, meal_plan_id)

    def get_meal_plan_with_recipes(
        self,
        meal_plan: MealPlan,
        ensure: Optional[Dict[str, Optional[str]]] = None,
    ) -> Dict[str, Any]:
        data = meal_plan.to_dict()
        data["days"] = {}

        results = self.session.execute(
            select(
                meal_plan_recipe.c.day,
                meal_plan_recipe.c.meal_type,
                Recipe,
            )
            .join(Recipe, Recipe.id == meal_plan_recipe.c.recipe_id)
            .where(meal_plan_recipe.c.meal_plan_id == meal_plan.id)
        )

        for day, meal_type, recipe in results:
            meals = data["days"].setdefault(day, {})
            recipe_list = meals.setdefault(meal_type, [])
            recipe_list.append(recipe.to_dict())

        if ensure:
            day = ensure.get("day") if ensure else None
            meal_type = ensure.get("meal_type") if ensure else None
            if day:
                ensured_meals = data["days"].setdefault(day, {})
                if meal_type and meal_type not in ensured_meals:
                    ensured_meals[meal_type] = []

        return data

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------
    def create_meal_plan(self, payload: Dict[str, Any]) -> MealPlan:
        name = (payload or {}).get("name")
        if not name:
            raise ValueError("'name' is a required field")

        meal_plan = MealPlan(
            name=name,
            start_date=self._parse_date(payload.get("start_date")),
            end_date=self._parse_date(payload.get("end_date")),
        )

        self.session.add(meal_plan)
        self.session.commit()
        self.session.refresh(meal_plan)
        return meal_plan

    def update_meal_plan(self, meal_plan_id: int, payload: Dict[str, Any]) -> Optional[MealPlan]:
        meal_plan = self.get_meal_plan_by_id(meal_plan_id)
        if meal_plan is None:
            return None

        if "name" in payload:
            meal_plan.name = payload["name"]
        if "start_date" in payload:
            meal_plan.start_date = self._parse_date(payload.get("start_date"))
        if "end_date" in payload:
            meal_plan.end_date = self._parse_date(payload.get("end_date"))

        self.session.add(meal_plan)
        self.session.commit()
        self.session.refresh(meal_plan)
        return meal_plan

    def delete_meal_plan(self, meal_plan_id: int) -> bool:
        meal_plan = self.get_meal_plan_by_id(meal_plan_id)
        if meal_plan is None:
            return False

        self.session.delete(meal_plan)
        self.session.commit()
        return True

    def add_recipe_to_meal_plan(
        self,
        meal_plan_id: int,
        recipe_id: Optional[int],
        day: Optional[str],
        meal_type: Optional[str],
    ) -> Optional[MealPlan]:
        if not recipe_id:
            raise ValueError("'recipe_id' is required")
        if not day:
            raise ValueError("'day' is required")
        if not meal_type:
            raise ValueError("'meal_type' is required")

        meal_plan = self.get_meal_plan_by_id(meal_plan_id)
        recipe = self.session.get(Recipe, recipe_id)
        if meal_plan is None or recipe is None:
            return None

        self.session.execute(
            insert(meal_plan_recipe).values(
                meal_plan_id=meal_plan.id,
                recipe_id=recipe.id,
                day=day,
                meal_type=meal_type,
            )
        )
        self.session.commit()
        self.session.refresh(meal_plan)
        return meal_plan

    def remove_recipe_from_meal_plan(
        self,
        meal_plan_id: int,
        recipe_id: int,
        day: Optional[str],
        meal_type: Optional[str],
    ) -> Optional[MealPlan]:
        meal_plan = self.get_meal_plan_by_id(meal_plan_id)
        if meal_plan is None:
            return None

        deletion = delete(meal_plan_recipe).where(meal_plan_recipe.c.meal_plan_id == meal_plan.id)
        deletion = deletion.where(meal_plan_recipe.c.recipe_id == recipe_id)
        if day:
            deletion = deletion.where(meal_plan_recipe.c.day == day)
        if meal_type:
            deletion = deletion.where(meal_plan_recipe.c.meal_type == meal_type)

        result = self.session.execute(deletion)
        if result.rowcount == 0:
            return None

        self.session.commit()
        self.session.refresh(meal_plan)
        return meal_plan

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_date(value: Optional[Any]) -> Optional[datetime]:
        if value in (None, ""):
            return None

        if isinstance(value, datetime):
            return value

        try:
            return datetime.fromisoformat(str(value))
        except ValueError:
            raise ValueError("Dates must be ISO formatted strings (YYYY-MM-DD)") from None


__all__ = ["MealPlanService"]
