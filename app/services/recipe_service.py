"""Business logic for working with recipes."""
from __future__ import annotations

import os
import time
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from database import Ingredient, NutritionInfo, Recipe
from .pdf_service import PDFService


class RecipeService:
    """Service layer for CRUD operations on :class:`Recipe` objects."""

    def __init__(
        self,
        session: Session,
        pdf_service: Optional[PDFService] = None,
        pdf_output_dir: Optional[str] = None,
    ) -> None:
        self.session = session
        self.pdf_service = pdf_service or PDFService()
        self.pdf_output_dir = pdf_output_dir or os.path.join(os.getcwd(), "static", "pdfs")

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def get_recipes(self, filters: Optional[Dict[str, Any]] = None) -> List[Recipe]:
        """Return recipes optionally filtered by the supplied parameters."""

        filters = filters or {}
        query = self.session.query(Recipe).distinct()

        search_term = filters.get("search")
        if search_term:
            ilike_pattern = f"%{search_term}%"
            query = query.filter(or_(Recipe.title.ilike(ilike_pattern), Recipe.description.ilike(ilike_pattern)))

        ingredient_name = filters.get("ingredient")
        if ingredient_name:
            ilike_pattern = f"%{ingredient_name}%"
            query = query.join(Recipe.ingredients).filter(Ingredient.name.ilike(ilike_pattern))

        min_calories = filters.get("min_calories")
        max_calories = filters.get("max_calories")
        if min_calories is not None or max_calories is not None:
            query = query.join(Recipe.nutrition, isouter=True)
            if min_calories is not None:
                query = query.filter(NutritionInfo.calories >= float(min_calories))
            if max_calories is not None:
                query = query.filter(NutritionInfo.calories <= float(max_calories))

        sort_by = filters.get("sort_by")
        sort_direction = filters.get("sort_direction", "asc").lower()
        if sort_by:
            sort_attr = getattr(Recipe, sort_by, None)
            if sort_attr is not None:
                ordering = asc(sort_attr) if sort_direction == "asc" else desc(sort_attr)
                query = query.order_by(ordering)

        limit = filters.get("limit")
        if limit:
            try:
                query = query.limit(int(limit))
            except (TypeError, ValueError):  # pragma: no cover - defensive
                pass

        return query.all()

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """Return a recipe by its primary key."""

        return self.session.get(Recipe, recipe_id)

    # ------------------------------------------------------------------
    # Mutating operations
    # ------------------------------------------------------------------
    def create_recipe(self, data: Dict[str, Any]) -> Recipe:
        """Create a new recipe from the supplied payload."""

        title = (data or {}).get("title")
        if not title:
            raise ValueError("'title' is a required field")

        recipe = Recipe(
            title=title,
            description=data.get("description"),
            instructions=data.get("instructions"),
            prep_time=data.get("prep_time"),
            cook_time=data.get("cook_time"),
            servings=data.get("servings"),
            image_url=data.get("image_url"),
            source_url=data.get("source_url"),
        )

        self._apply_ingredients(recipe, data.get("ingredients"))
        self._apply_nutrition(recipe, data.get("nutrition"))

        self.session.add(recipe)
        self.session.commit()
        self.session.refresh(recipe)
        return recipe

    def update_recipe(self, recipe_id: int, data: Dict[str, Any]) -> Optional[Recipe]:
        """Update an existing recipe returning ``None`` if not found."""

        recipe = self.get_recipe_by_id(recipe_id)
        if recipe is None:
            return None

        for field in [
            "title",
            "description",
            "instructions",
            "prep_time",
            "cook_time",
            "servings",
            "image_url",
            "source_url",
        ]:
            if field in data:
                setattr(recipe, field, data[field])

        if "ingredients" in data:
            recipe.ingredients.clear()
            self._apply_ingredients(recipe, data.get("ingredients"))

        if "nutrition" in data:
            self._apply_nutrition(recipe, data.get("nutrition"))

        self.session.add(recipe)
        self.session.commit()
        self.session.refresh(recipe)
        return recipe

    def delete_recipe(self, recipe_id: int) -> bool:
        """Delete a recipe returning ``True`` if the record existed."""

        recipe = self.get_recipe_by_id(recipe_id)
        if recipe is None:
            return False

        self.session.delete(recipe)
        self.session.commit()
        return True

    def generate_pdf(self, recipe_id: int) -> Optional[str]:
        """Generate a PDF for the given recipe and update its ``pdf_path``."""

        recipe = self.get_recipe_by_id(recipe_id)
        if recipe is None:
            return None

        os.makedirs(self.pdf_output_dir, exist_ok=True)
        filename = f"recipe_{recipe.id}_{int(time.time())}.pdf"
        output_path = os.path.join(self.pdf_output_dir, filename)

        if self.pdf_service.generate_recipe_pdf(recipe, output_path):
            recipe.pdf_path = output_path
            self.session.add(recipe)
            self.session.commit()
            return output_path

        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _apply_ingredients(self, recipe: Recipe, ingredients: Optional[Iterable[Dict[str, Any]]]) -> None:
        if not ingredients:
            return

        for payload in ingredients:
            if not payload:
                continue
            ingredient = Ingredient(
                name=payload.get("name"),
                amount=payload.get("amount"),
                unit=payload.get("unit"),
            )
            recipe.ingredients.append(ingredient)

    def _apply_nutrition(self, recipe: Recipe, nutrition: Optional[Dict[str, Any]]) -> None:
        if not nutrition:
            return

        if recipe.nutrition is None:
            recipe.nutrition = NutritionInfo()

        for key in ["calories", "protein", "carbs", "fat", "sugar", "sodium", "fiber"]:
            if key in nutrition:
                setattr(recipe.nutrition, key, nutrition[key])

        self.session.add(recipe.nutrition)


__all__ = ["RecipeService"]
