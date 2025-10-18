"""User-facing HTML routes for the Recipe Planner application."""
from __future__ import annotations

from typing import Sequence

from flask import Blueprint, current_app, render_template, request

from database import ShoppingList
from .services.meal_plan_service import MealPlanService
from .services.recipe_service import RecipeService

web_bp = Blueprint("web", __name__)


def _get_session():
    """Return the scoped session factory bound to the current app."""

    session_factory = current_app.extensions["get_session_factory"]()
    return session_factory


@web_bp.route("/")
def homepage():
    """Render the homepage with recent recipes, meal plans, and shopping lists."""

    session = _get_session()
    recipe_service = RecipeService(session)
    meal_plan_service = MealPlanService(session)

    recent_recipes: Sequence = recipe_service.get_recipes(
        {"sort_by": "created_at", "sort_direction": "desc", "limit": 6}
    )
    recent_meal_plans: Sequence = meal_plan_service.get_meal_plans({"limit": 3})
    recent_lists: Sequence = (
        session.query(ShoppingList)
        .order_by(ShoppingList.created_at.desc())
        .limit(3)
        .all()
    )

    return render_template(
        "index.html",
        recipes=recent_recipes,
        meal_plans=recent_meal_plans,
        shopping_lists=recent_lists,
    )


@web_bp.route("/recipes")
def recipes():
    """Render the recipe catalogue with optional filters."""

    session = _get_session()
    recipe_service = RecipeService(session)
    meal_plan_service = MealPlanService(session)

    requested_filters = {
        key: request.args.get(key)
        for key in [
            "search",
            "ingredient",
            "sort_by",
            "sort_direction",
            "min_calories",
            "max_calories",
        ]
    }
    filters = {key: value for key, value in requested_filters.items() if value not in (None, "")}

    recipes = recipe_service.get_recipes(filters or None)
    meal_plans = meal_plan_service.get_meal_plans()

    return render_template(
        "recipes.html",
        recipes=recipes,
        filters=requested_filters,
        meal_plans=meal_plans,
    )


__all__ = ["web_bp"]
