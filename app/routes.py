"""REST API routes for the Recipe Planner application."""
from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any, Dict, Optional

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from .services.meal_plan_service import MealPlanService
from .services.nutrition_service import NutritionService
from .services.pdf_service import PDFService
from .services.recipe_service import RecipeService
from .services.scraper_service import ScraperService

LOGGER = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _get_session():
    """Return a scoped SQLAlchemy session bound to the current app."""

    session_factory = current_app.extensions["get_session_factory"]()
    return session_factory


@api_bp.errorhandler(SQLAlchemyError)
def handle_database_error(error: SQLAlchemyError):  # pragma: no cover - defensive
    current_app.logger.exception("Database error: %%s", error)
    return jsonify({"message": "A database error occurred."}), HTTPStatus.INTERNAL_SERVER_ERROR


@api_bp.route("/recipes", methods=["GET"])
def list_recipes():
    """Return a list of recipes respecting optional filter parameters."""

    session = _get_session()
    service = RecipeService(session)
    recipes = service.get_recipes(request.args.to_dict())
    return jsonify([recipe.to_dict() for recipe in recipes])


@api_bp.route("/recipes/<int:recipe_id>", methods=["GET"])
def get_recipe(recipe_id: int):
    session = _get_session()
    service = RecipeService(session)
    recipe = service.get_recipe_by_id(recipe_id)
    if recipe is None:
        return jsonify({"message": "Recipe not found"}), HTTPStatus.NOT_FOUND

    return jsonify(recipe.to_dict())


@api_bp.route("/recipes", methods=["POST"])
def create_recipe():
    payload: Optional[Dict[str, Any]] = request.get_json(silent=True)
    if not payload:
        return jsonify({"message": "Request body must be JSON"}), HTTPStatus.BAD_REQUEST

    session = _get_session()
    service = RecipeService(session)
    try:
        recipe = service.create_recipe(payload)
    except ValueError as exc:
        return jsonify({"message": str(exc)}), HTTPStatus.BAD_REQUEST

    return jsonify(recipe.to_dict()), HTTPStatus.CREATED


@api_bp.route("/recipes/<int:recipe_id>", methods=["PUT"])
def update_recipe(recipe_id: int):
    payload: Optional[Dict[str, Any]] = request.get_json(silent=True)
    if payload is None:
        return jsonify({"message": "Request body must be JSON"}), HTTPStatus.BAD_REQUEST

    session = _get_session()
    service = RecipeService(session)
    recipe = service.update_recipe(recipe_id, payload)
    if recipe is None:
        return jsonify({"message": "Recipe not found"}), HTTPStatus.NOT_FOUND

    return jsonify(recipe.to_dict())


@api_bp.route("/recipes/<int:recipe_id>", methods=["DELETE"])
def delete_recipe(recipe_id: int):
    session = _get_session()
    service = RecipeService(session)
    deleted = service.delete_recipe(recipe_id)
    if not deleted:
        return jsonify({"message": "Recipe not found"}), HTTPStatus.NOT_FOUND

    return jsonify({"message": "Recipe deleted"})


@api_bp.route("/recipes/<int:recipe_id>/pdf", methods=["POST"])
def generate_recipe_pdf(recipe_id: int):
    session = _get_session()
    pdf_service = PDFService()
    service = RecipeService(session, pdf_service=pdf_service)

    pdf_path = service.generate_pdf(recipe_id)
    if pdf_path is None:
        return jsonify({"message": "Recipe not found"}), HTTPStatus.NOT_FOUND

    return jsonify({"pdf_path": pdf_path})


@api_bp.route("/meal-plans", methods=["GET"])
def list_meal_plans():
    session = _get_session()
    service = MealPlanService(session)
    meal_plans = service.get_meal_plans(request.args.to_dict())
    return jsonify([meal_plan.to_dict() for meal_plan in meal_plans])


@api_bp.route("/meal-plans/<int:meal_plan_id>", methods=["GET"])
def get_meal_plan(meal_plan_id: int):
    session = _get_session()
    service = MealPlanService(session)
    meal_plan = service.get_meal_plan_by_id(meal_plan_id)
    if meal_plan is None:
        return jsonify({"message": "Meal plan not found"}), HTTPStatus.NOT_FOUND

    data = service.get_meal_plan_with_recipes(meal_plan)
    return jsonify(data)


@api_bp.route("/meal-plans", methods=["POST"])
def create_meal_plan():
    payload: Optional[Dict[str, Any]] = request.get_json(silent=True)
    if not payload:
        return jsonify({"message": "Request body must be JSON"}), HTTPStatus.BAD_REQUEST

    session = _get_session()
    service = MealPlanService(session)
    try:
        meal_plan = service.create_meal_plan(payload)
    except ValueError as exc:
        return jsonify({"message": str(exc)}), HTTPStatus.BAD_REQUEST

    return jsonify(meal_plan.to_dict()), HTTPStatus.CREATED


@api_bp.route("/meal-plans/<int:meal_plan_id>", methods=["PUT"])
def update_meal_plan(meal_plan_id: int):
    payload: Optional[Dict[str, Any]] = request.get_json(silent=True)
    if payload is None:
        return jsonify({"message": "Request body must be JSON"}), HTTPStatus.BAD_REQUEST

    session = _get_session()
    service = MealPlanService(session)
    meal_plan = service.update_meal_plan(meal_plan_id, payload)
    if meal_plan is None:
        return jsonify({"message": "Meal plan not found"}), HTTPStatus.NOT_FOUND

    return jsonify(meal_plan.to_dict())


@api_bp.route("/meal-plans/<int:meal_plan_id>", methods=["DELETE"])
def delete_meal_plan(meal_plan_id: int):
    session = _get_session()
    service = MealPlanService(session)
    deleted = service.delete_meal_plan(meal_plan_id)
    if not deleted:
        return jsonify({"message": "Meal plan not found"}), HTTPStatus.NOT_FOUND

    return jsonify({"message": "Meal plan deleted"})


@api_bp.route("/meal-plans/<int:meal_plan_id>/recipes", methods=["POST"])
def add_recipe_to_meal_plan(meal_plan_id: int):
    payload: Optional[Dict[str, Any]] = request.get_json(silent=True)
    if not payload:
        return jsonify({"message": "Request body must be JSON"}), HTTPStatus.BAD_REQUEST

    session = _get_session()
    service = MealPlanService(session)
    try:
        meal_plan = service.add_recipe_to_meal_plan(
            meal_plan_id,
            payload.get("recipe_id"),
            payload.get("day"),
            payload.get("meal_type"),
        )
    except ValueError as exc:
        return jsonify({"message": str(exc)}), HTTPStatus.BAD_REQUEST

    if meal_plan is None:
        return jsonify({"message": "Meal plan or recipe not found"}), HTTPStatus.NOT_FOUND

    data = service.get_meal_plan_with_recipes(
        meal_plan,
        ensure={"day": payload.get("day"), "meal_type": payload.get("meal_type")},
    )

    day = payload.get("day")
    if day and day not in data["days"]:
        data["days"][day] = {}
    meal_type = payload.get("meal_type")
    if day and meal_type:
        data["days"][day].setdefault(meal_type, [])

    return jsonify(data)


@api_bp.route("/meal-plans/<int:meal_plan_id>/recipes/<int:recipe_id>", methods=["DELETE"])
def remove_recipe_from_meal_plan(meal_plan_id: int, recipe_id: int):
    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    LOGGER.debug("Remove recipe payload: %s", payload)
    session = _get_session()
    service = MealPlanService(session)

    meal_plan = service.remove_recipe_from_meal_plan(
        meal_plan_id,
        recipe_id,
        payload.get("day"),
        payload.get("meal_type"),
    )

    if meal_plan is None:
        return jsonify({"message": "Meal plan or recipe not found"}), HTTPStatus.NOT_FOUND

    data = service.get_meal_plan_with_recipes(
        meal_plan,
        ensure={"day": payload.get("day"), "meal_type": payload.get("meal_type")},
    )

    day = payload.get("day")
    if day and day not in data["days"]:
        data["days"][day] = {}
    meal_type = payload.get("meal_type")
    if day and meal_type:
        data["days"][day].setdefault(meal_type, [])

    LOGGER.debug("Meal plan days after removal: %s", data["days"])

    return jsonify(data)


@api_bp.route("/nutrition/calculate", methods=["POST"])
def calculate_nutrition():
    payload: Optional[Dict[str, Any]] = request.get_json(silent=True)
    if not payload or "ingredients" not in payload:
        return jsonify({"message": "Request must include an 'ingredients' field"}), HTTPStatus.BAD_REQUEST

    nutrition_service = NutritionService()
    nutrition = nutrition_service.calculate_nutrition(payload["ingredients"])
    return jsonify(nutrition)


@api_bp.route("/scrape", methods=["POST"])
def scrape_recipe():
    payload: Optional[Dict[str, Any]] = request.get_json(silent=True)
    if not payload or "url" not in payload:
        return jsonify({"message": "Request must include a 'url' field"}), HTTPStatus.BAD_REQUEST

    try:
        recipe_data = ScraperService.scrape_recipe(payload["url"])
    except ValueError as exc:
        LOGGER.warning("Scraping failed: %s", exc)
        return jsonify({"message": str(exc)}), HTTPStatus.BAD_REQUEST

    return jsonify(recipe_data)


__all__ = ["api_bp"]
