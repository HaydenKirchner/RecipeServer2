"""User-facing HTML routes for the Recipe Planner application."""
from __future__ import annotations

import os
from types import SimpleNamespace
from typing import Any, Dict, List, Mapping, Optional, Sequence

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from werkzeug.datastructures import ImmutableMultiDict

from sqlalchemy.orm import selectinload

from database import Inventory, MealPlan, Recipe, ShoppingList, ShoppingListItem
from .services.meal_plan_service import MealPlanService
from .services.recipe_service import RecipeService

views_bp = Blueprint("views", __name__)


_INGREDIENT_ICON_MAP = {
    # Vegetables
    "onion": "/static/images/ingredients/onion.svg",
    "shallot": "/static/images/ingredients/onion.svg",
    "garlic": "/static/images/ingredients/garlic.svg",
    "tomato": "/static/images/ingredients/tomato.svg",
    "potato": "/static/images/ingredients/potato.svg",
    "potatoes": "/static/images/ingredients/potato.svg",
    "kale": "/static/images/ingredients/kale.svg",
    "cabbage": "/static/images/ingredients/cabbage.svg",
    "pickle": "/static/images/ingredients/pickle.svg",
    "cucumber": "/static/images/ingredients/pickle.svg",
    # Proteins
    "chicken": "/static/images/ingredients/chicken.svg",
    "beef": "/static/images/ingredients/beef.svg",
    "steak": "/static/images/ingredients/beef.svg",
    "sirloin": "/static/images/ingredients/beef.svg",
    "bacon": "/static/images/ingredients/bacon.svg",
    # Dairy
    "cream": "/static/images/ingredients/dairy.svg",
    "sour cream": "/static/images/ingredients/dairy.svg",
    "milk": "/static/images/ingredients/dairy.svg",
    "butter": "/static/images/ingredients/dairy.svg",
    "yogurt": "/static/images/ingredients/dairy.svg",
    "cheese": "/static/images/ingredients/dairy.svg",
    # Condiments & Other
    "vinegar": "/static/images/ingredients/vinegar.svg",
    "salt": "/static/images/ingredients/spices.svg",
    "pepper": "/static/images/ingredients/spices.svg",
    "spice": "/static/images/ingredients/spices.svg",
    "seasoning": "/static/images/ingredients/spices.svg",
    "peppercorn": "/static/images/ingredients/spices.svg",
    # Grains
    "rice": "/static/images/ingredients/rice.svg",
    "pasta": "/static/images/ingredients/pasta.svg",
    "noodle": "/static/images/ingredients/pasta.svg",
    "spaghetti": "/static/images/ingredients/pasta.svg",
    "macaroni": "/static/images/ingredients/pasta.svg",
    "fettuccine": "/static/images/ingredients/pasta.svg",
    "linguine": "/static/images/ingredients/pasta.svg",
    "penne": "/static/images/ingredients/pasta.svg",
    # Nuts
    "nut": "/static/images/ingredients/nuts.svg",
    "almond": "/static/images/ingredients/nuts.svg",
    "walnut": "/static/images/ingredients/nuts.svg",
    "pistachio": "/static/images/ingredients/nuts.svg",
    "peanut": "/static/images/ingredients/nuts.svg",
    "cashew": "/static/images/ingredients/nuts.svg",
    "pecan": "/static/images/ingredients/nuts.svg",
    # Fruits
    "apple": "/static/images/ingredients/fruit.svg",
    "orange": "/static/images/ingredients/fruit.svg",
    "banana": "/static/images/ingredients/fruit.svg",
    "cherry": "/static/images/ingredients/fruit.svg",
    "lemon": "/static/images/ingredients/fruit.svg",
    "lime": "/static/images/ingredients/fruit.svg",
    "berry": "/static/images/ingredients/fruit.svg",
    "strawberry": "/static/images/ingredients/fruit.svg",
    "blueberry": "/static/images/ingredients/fruit.svg",
    "raspberry": "/static/images/ingredients/fruit.svg",
    # Herbs
    "herb": "/static/images/ingredients/herbs.svg",
    "basil": "/static/images/ingredients/herbs.svg",
    "mint": "/static/images/ingredients/herbs.svg",
    "thyme": "/static/images/ingredients/herbs.svg",
    "rosemary": "/static/images/ingredients/herbs.svg",
    "oregano": "/static/images/ingredients/herbs.svg",
    "parsley": "/static/images/ingredients/herbs.svg",
    "cilantro": "/static/images/ingredients/herbs.svg",
    "dill": "/static/images/ingredients/herbs.svg",
}


@views_bp.app_template_filter("ingredient_icon")
def ingredient_icon_filter(value: Optional[str]) -> str:
    """Return the icon path for the supplied ingredient name."""

    if not value:
        return "/static/images/ingredients/default.svg"

    lower_value = value.lower().strip()
    if lower_value in _INGREDIENT_ICON_MAP:
        return _INGREDIENT_ICON_MAP[lower_value]

    for key, path in _INGREDIENT_ICON_MAP.items():
        if key in lower_value:
            return path

    return "/static/images/ingredients/default.svg"


def _get_session():
    """Return the scoped session factory bound to the current app."""

    session_factory = current_app.extensions["get_session_factory"]()
    return session_factory


def _get_services():
    """Instantiate commonly used services for the current request."""

    session_factory = _get_session()
    session = session_factory()
    recipe_service = RecipeService(session)
    meal_plan_service = MealPlanService(session)
    return session, recipe_service, meal_plan_service


def _summarise_meal_plans(session) -> List[SimpleNamespace]:
    """Return lightweight representations of the available meal plans."""

    meal_plans: Sequence[MealPlan] = (
        session.query(MealPlan)
        .options(selectinload(MealPlan.shopping_list))
        .order_by(MealPlan.created_at.desc())
        .all()
    )

    summaries: List[SimpleNamespace] = []
    for meal_plan in meal_plans:
        summaries.append(
            SimpleNamespace(
                id=meal_plan.id,
                name=meal_plan.name,
                start_date=meal_plan.start_date,
                end_date=meal_plan.end_date,
                shopping_list_name=meal_plan.shopping_list.name if meal_plan.shopping_list else None,
            )
        )

    return summaries


def _summarise_shopping_lists(session) -> List[SimpleNamespace]:
    """Return lightweight data for all shopping lists."""

    shopping_lists: Sequence[ShoppingList] = (
        session.query(ShoppingList)
        .options(selectinload(ShoppingList.items), selectinload(ShoppingList.meal_plan))
        .order_by(ShoppingList.created_at.desc())
        .all()
    )

    summaries: List[SimpleNamespace] = []
    for shopping_list in shopping_lists:
        summaries.append(
            SimpleNamespace(
                id=shopping_list.id,
                name=shopping_list.name,
                created_at=shopping_list.created_at,
                updated_at=shopping_list.updated_at,
                item_count=len(shopping_list.items),
                meal_plan_name=shopping_list.meal_plan.name if shopping_list.meal_plan else None,
            )
        )

    return summaries


def _summarise_inventories(session) -> List[SimpleNamespace]:
    """Return lightweight data for available pantry inventories."""

    inventories: Sequence[Inventory] = (
        session.query(Inventory)
        .options(selectinload(Inventory.items))
        .order_by(Inventory.created_at.desc())
        .all()
    )

    summaries: List[SimpleNamespace] = []
    for inventory in inventories:
        summaries.append(
            SimpleNamespace(
                id=inventory.id,
                name=inventory.name,
                created_at=inventory.created_at,
                updated_at=inventory.updated_at,
                item_count=len(inventory.items),
            )
        )

    return summaries


def _coerce_int(value: Optional[str]) -> Optional[int]:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _coerce_float(value: Optional[str]) -> Optional[float]:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _collect_recipe_payload(form: ImmutableMultiDict[str, str]) -> Dict[str, Any]:
    """Convert the submitted recipe form data into a service payload."""

    payload: Dict[str, Any] = {
        "title": form.get("title", "").strip(),
        "description": form.get("description", "").strip() or None,
        "instructions": form.get("instructions", "").strip() or None,
        "prep_time": _coerce_int(form.get("prep_time")),
        "cook_time": _coerce_int(form.get("cook_time")),
        "servings": _coerce_int(form.get("servings")),
        "image_url": form.get("image_url", "").strip() or None,
        "source_url": form.get("source_url", "").strip() or None,
    }

    ingredient_names = form.getlist("ingredient_name")
    ingredient_amounts = form.getlist("ingredient_amount")
    ingredient_units = form.getlist("ingredient_unit")

    ingredients: List[Dict[str, Any]] = []
    for name, amount, unit in zip(ingredient_names, ingredient_amounts, ingredient_units):
        name = (name or "").strip()
        if not name:
            continue
        ingredient: Dict[str, Any] = {"name": name}
        coerced_amount = _coerce_float(amount)
        if coerced_amount is not None:
            ingredient["amount"] = coerced_amount
        unit = (unit or "").strip()
        if unit:
            ingredient["unit"] = unit
        ingredients.append(ingredient)

    if ingredients:
        payload["ingredients"] = ingredients

    nutrition_fields = ["calories", "protein", "carbs", "fat", "sugar", "sodium", "fiber"]
    nutrition: Dict[str, Any] = {}
    for field in nutrition_fields:
        value = _coerce_float(form.get(field))
        if value is not None:
            nutrition[field] = value

    if nutrition:
        payload["nutrition"] = nutrition

    return payload


def _payload_to_preview(payload: Mapping[str, Any]) -> SimpleNamespace:
    """Convert a payload dict into an object usable by the templates."""

    ingredients_payload = payload.get("ingredients", []) or []
    ingredients = [
        SimpleNamespace(name=item.get("name"), amount=item.get("amount"), unit=item.get("unit"))
        for item in ingredients_payload
    ]

    nutrition_payload = payload.get("nutrition") or {}
    nutrition = None
    if nutrition_payload:
        nutrition = SimpleNamespace(**nutrition_payload)

    return SimpleNamespace(
        id=payload.get("id"),
        title=payload.get("title"),
        description=payload.get("description"),
        instructions=payload.get("instructions"),
        prep_time=payload.get("prep_time"),
        cook_time=payload.get("cook_time"),
        servings=payload.get("servings"),
        image_url=payload.get("image_url"),
        source_url=payload.get("source_url"),
        ingredients=ingredients,
        nutrition=nutrition,
    )


def _validate_recipe_payload(payload: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if not payload.get("title"):
        errors.append("Recipe title is required.")
    return errors


def _ensure_shopping_list(meal_plan, recipe: Recipe, session) -> None:
    """Create or update the shopping list for the meal plan with the recipe's ingredients."""

    shopping_list = meal_plan.shopping_list
    if shopping_list is None:
        shopping_list = ShoppingList(name=f"{meal_plan.name} Shopping List", meal_plan=meal_plan)
        session.add(shopping_list)
        session.flush()

    existing_items = {item.ingredient_id: item for item in shopping_list.items}
    for ingredient in recipe.ingredients:
        if ingredient is None or ingredient.id is None:
            continue
        item = existing_items.get(ingredient.id)
        if item is None:
            item = ShoppingListItem(
                shopping_list=shopping_list,
                ingredient=ingredient,
                quantity=ingredient.amount,
                unit=ingredient.unit,
            )
            session.add(item)
            existing_items[ingredient.id] = item
        else:
            if ingredient.amount is not None:
                item.quantity = (item.quantity or 0) + ingredient.amount
            if ingredient.unit:
                item.unit = ingredient.unit

    session.commit()


def _parse_boolean(value: Optional[str]) -> bool:
    return str(value).lower() in {"1", "true", "yes", "on"}


@views_bp.route("/", endpoint="index")
def homepage():
    """Render the homepage with recent recipes, meal plans, and shopping lists."""

    session_factory = _get_session()
    session = session_factory()
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


@views_bp.route("/meal-plans", methods=["GET"])
def meal_plans_overview():
    """Display a simple overview of saved meal plans."""

    session_factory = _get_session()
    session = session_factory()
    try:
        meal_plans = _summarise_meal_plans(session)
    finally:
        session.close()

    return render_template("meal_plans_overview.html", meal_plans=meal_plans)


@views_bp.route("/shopping-lists", methods=["GET"])
def shopping_lists_overview():
    """Display the available shopping lists with basic metadata."""

    session_factory = _get_session()
    session = session_factory()
    try:
        shopping_lists = _summarise_shopping_lists(session)
    finally:
        session.close()

    return render_template("shopping_lists_overview.html", shopping_lists=shopping_lists)


@views_bp.route("/inventory", methods=["GET"])
def inventory_overview():
    """Display the inventories/pantries created by the user."""

    session_factory = _get_session()
    session = session_factory()
    try:
        inventories = _summarise_inventories(session)
    finally:
        session.close()

    return render_template("inventory_overview.html", inventories=inventories)


@views_bp.route("/recipes", methods=["GET"])
def recipes():
    """Render the recipe catalogue with optional filters."""

    session, recipe_service, meal_plan_service = _get_services()

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

    recipes_list = recipe_service.get_recipes(filters or None)
    meal_plans = meal_plan_service.get_meal_plans()

    return render_template(
        "recipes.html",
        recipes=recipes_list,
        filters=requested_filters,
        meal_plans=meal_plans,
    )


@views_bp.route("/recipes/add", methods=["GET", "POST"])
def add_recipe():
    """Display and process the add recipe form."""

    if request.method == "GET":
        return render_template("add_recipe.html", edit_mode=False, recipe=None)

    payload = _collect_recipe_payload(request.form)
    errors = _validate_recipe_payload(payload)
    if errors:
        for error in errors:
            flash(error, "danger")
        return render_template("add_recipe.html", edit_mode=False, recipe=_payload_to_preview(payload))

    _session, recipe_service, _ = _get_services()
    recipe = recipe_service.create_recipe(payload)
    flash("Recipe created successfully!", "success")
    return redirect(url_for("views.recipe_detail", recipe_id=recipe.id))


@views_bp.route("/recipes/<int:recipe_id>", methods=["GET"])
def recipe_detail(recipe_id: int):
    """Render the details page for a specific recipe."""

    session, recipe_service, meal_plan_service = _get_services()
    recipe = recipe_service.get_recipe_by_id(recipe_id)
    if recipe is None:
        abort(404)

    existing_meal_plans = meal_plan_service.get_meal_plans()
    return render_template(
        "recipe_detail.html",
        recipe=recipe,
        existing_meal_plans=existing_meal_plans,
    )


@views_bp.route("/recipes/<int:recipe_id>/edit", methods=["GET", "POST"])
def edit_recipe(recipe_id: int):
    """Edit an existing recipe."""

    _session, recipe_service, _ = _get_services()
    recipe = recipe_service.get_recipe_by_id(recipe_id)
    if recipe is None:
        abort(404)

    if request.method == "GET":
        return render_template("add_recipe.html", edit_mode=True, recipe=recipe)

    payload = _collect_recipe_payload(request.form)
    errors = _validate_recipe_payload(payload)
    if errors:
        for error in errors:
            flash(error, "danger")
        payload_with_id = dict(payload)
        payload_with_id["id"] = recipe_id
        return render_template(
            "add_recipe.html",
            edit_mode=True,
            recipe=_payload_to_preview(payload_with_id),
        )

    updated = recipe_service.update_recipe(recipe_id, payload)
    if updated is None:
        abort(404)
    flash("Recipe updated successfully!", "success")
    return redirect(url_for("views.recipe_detail", recipe_id=recipe_id))


@views_bp.route("/recipes/<int:recipe_id>/delete", methods=["POST"])
def delete_recipe(recipe_id: int):
    """Delete a recipe and return to the catalogue."""

    _session, recipe_service, _ = _get_services()
    deleted = recipe_service.delete_recipe(recipe_id)
    if not deleted:
        abort(404)
    flash("Recipe deleted.", "success")
    return redirect(url_for("views.recipes"))


@views_bp.route("/recipes/<int:recipe_id>/pdf", methods=["GET"])
def recipe_pdf(recipe_id: int):
    """Generate (if required) and send the recipe PDF to the client."""

    _session, recipe_service, _ = _get_services()
    recipe = recipe_service.get_recipe_by_id(recipe_id)
    if recipe is None:
        abort(404)

    pdf_path = recipe.pdf_path
    if not pdf_path or not os.path.exists(pdf_path):
        pdf_path = recipe_service.generate_pdf(recipe_id)

    if not pdf_path or not os.path.exists(pdf_path):
        flash("Unable to generate recipe PDF.", "danger")
        return redirect(url_for("views.recipe_detail", recipe_id=recipe_id))

    return send_file(pdf_path, as_attachment=True)


@views_bp.route("/recipes/<int:recipe_id>/add-to-meal-plan", methods=["POST"])
def add_to_meal_plan_from_recipe(recipe_id: int):
    """Attach the recipe to an existing meal plan."""

    session, recipe_service, meal_plan_service = _get_services()
    recipe = recipe_service.get_recipe_by_id(recipe_id)
    if recipe is None:
        abort(404)

    meal_plan_id = request.form.get("meal_plan_id")
    day = request.form.get("day")
    meal_type = request.form.get("meal_type")
    create_shopping_list = _parse_boolean(request.form.get("create_shopping_list"))

    try:
        meal_plan = meal_plan_service.add_recipe_to_meal_plan(
            int(meal_plan_id) if meal_plan_id else None,
            recipe.id,
            day,
            meal_type,
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("views.recipe_detail", recipe_id=recipe_id))

    if meal_plan is None:
        flash("Meal plan not found.", "danger")
        return redirect(url_for("views.recipe_detail", recipe_id=recipe_id))

    if create_shopping_list:
        _ensure_shopping_list(meal_plan, recipe, session)

    flash("Recipe added to meal plan.", "success")
    return redirect(url_for("views.recipe_detail", recipe_id=recipe_id))


@views_bp.route("/recipes/<int:recipe_id>/add-to-new-meal-plan", methods=["POST"])
def add_to_new_meal_plan(recipe_id: int):
    """Create a new meal plan and attach the recipe to it."""

    session, recipe_service, meal_plan_service = _get_services()
    recipe = recipe_service.get_recipe_by_id(recipe_id)
    if recipe is None:
        abort(404)

    payload = {
        "name": request.form.get("name"),
        "start_date": request.form.get("start_date"),
        "end_date": request.form.get("end_date"),
    }
    day = request.form.get("day")
    meal_type = request.form.get("meal_type")
    create_shopping_list = _parse_boolean(request.form.get("create_shopping_list"))

    try:
        meal_plan = meal_plan_service.create_meal_plan(payload)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("views.recipe_detail", recipe_id=recipe_id))

    try:
        meal_plan = meal_plan_service.add_recipe_to_meal_plan(meal_plan.id, recipe.id, day, meal_type)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("views.recipe_detail", recipe_id=recipe_id))

    if meal_plan is None:
        flash("Unable to associate recipe with the new meal plan.", "danger")
        return redirect(url_for("views.recipe_detail", recipe_id=recipe_id))

    if create_shopping_list:
        _ensure_shopping_list(meal_plan, recipe, session)

    flash("Meal plan created and recipe added.", "success")
    return redirect(url_for("views.recipe_detail", recipe_id=recipe_id))


__all__ = ["views_bp"]
