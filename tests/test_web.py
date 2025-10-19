"""Tests for the user-facing web blueprint."""
from __future__ import annotations

from database import Recipe


def _get_session(app):
    session_factory = app.extensions["get_session_factory"]()
    return session_factory()


def test_homepage_renders_successfully(client):
    """The homepage should render without server errors."""

    response = client.get("/")

    assert response.status_code == 200
    assert b"Welcome to Recipe Planner" in response.data


def test_recipes_page_renders_successfully(client):
    """The recipes catalogue should render without server errors."""

    response = client.get("/recipes")

    assert response.status_code == 200
    assert b"Recipes" in response.data


def test_meal_plans_overview_renders(client):
    """The meal plans overview page should return successfully."""

    response = client.get("/meal-plans")

    assert response.status_code == 200
    assert b"Meal Plans" in response.data


def test_shopping_lists_overview_renders(client):
    """The shopping lists overview page should return successfully."""

    response = client.get("/shopping-lists")

    assert response.status_code == 200
    assert b"Shopping Lists" in response.data


def test_inventory_overview_renders(client):
    """The inventory overview page should return successfully."""

    response = client.get("/inventory")

    assert response.status_code == 200
    assert b"Pantry Inventory" in response.data


def test_add_recipe_form_renders(client):
    """The add recipe page should be accessible."""

    response = client.get("/recipes/add")

    assert response.status_code == 200
    assert b"Add Recipe" in response.data


def test_create_recipe_via_form(app, client):
    """Submitting the add recipe form should create a recipe and redirect."""

    form_data = {
        "title": "Form Created Recipe",
        "description": "Created from the form",
        "instructions": "Step 1\nStep 2",
        "prep_time": "10",
        "cook_time": "20",
        "servings": "4",
        "ingredient_name": ["Flour", "Sugar"],
        "ingredient_amount": ["2", "1.5"],
        "ingredient_unit": ["cups", "cups"],
    }

    response = client.post("/recipes/add", data=form_data, follow_redirects=False)

    assert response.status_code == 302

    with app.app_context():
        session = _get_session(app)
        recipe = session.query(Recipe).filter_by(title="Form Created Recipe").one()
        session.close()

    assert f"/recipes/{recipe.id}" in response.headers["Location"]


def test_edit_recipe_via_form(app, client):
    """Editing an existing recipe via the form should persist changes."""

    with app.app_context():
        session = _get_session(app)
        recipe = Recipe(title="Editable Recipe")
        session.add(recipe)
        session.commit()
        recipe_id = recipe.id
        session.close()

    response = client.post(
        f"/recipes/{recipe_id}/edit",
        data={"title": "Updated Recipe", "ingredient_name": ["Sugar"], "ingredient_amount": ["1"], "ingredient_unit": ["cup"]},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert f"/recipes/{recipe_id}" in response.headers["Location"]

    with app.app_context():
        session = _get_session(app)
        updated = session.get(Recipe, recipe_id)
        session.close()

    assert updated.title == "Updated Recipe"


def test_delete_recipe_flow(app, client):
    """Deleting a recipe via the form should remove it from the database."""

    with app.app_context():
        session = _get_session(app)
        recipe = Recipe(title="Disposable Recipe")
        session.add(recipe)
        session.commit()
        recipe_id = recipe.id
        session.close()

    response = client.post(f"/recipes/{recipe_id}/delete", follow_redirects=False)

    assert response.status_code == 302
    assert "/recipes" in response.headers["Location"]

    with app.app_context():
        session = _get_session(app)
        deleted = session.get(Recipe, recipe_id)
        session.close()

    assert deleted is None


def test_scraper_page_renders(client):
    """The scraper page should render successfully."""

    response = client.get("/scraper")

    assert response.status_code == 200
    assert b"Recipe Scraper" in response.data


def test_scraper_submission_shows_preview(client, monkeypatch):
    """Submitting a URL to the scraper should render a preview."""

    sample_payload = {
        "title": "Mocked Scraped Recipe",
        "description": "Mocked description",
        "ingredients": [
            {"name": "Mocked Ingredient", "amount": 1.0, "unit": "cup"},
        ],
        "instructions": "1. Test instruction",
        "prep_time": 5,
        "cook_time": 10,
        "servings": 2,
        "image_url": "https://example.com/image.jpg",
        "source_url": "https://example.com/recipe",
        "nutrition": {"calories": 100},
    }

    from app.services.scraper_service import ScraperService

    monkeypatch.setattr(ScraperService, "scrape_recipe", lambda url: sample_payload)

    response = client.post("/scraper", data={"url": "https://example.com/recipe"})

    assert response.status_code == 200
    assert b"Mocked Scraped Recipe" in response.data
    assert b"Mocked description" in response.data


def test_scraper_save_creates_recipe(app, client):
    """Saving a scraped recipe should persist the record and redirect."""

    form_data = {
        "title": "Saved Scraper Recipe",
        "description": "Scraped via form",
        "instructions": "Step 1\nStep 2",
        "prep_time": "5",
        "cook_time": "10",
        "servings": "4",
        "image_url": "https://example.com/recipe.jpg",
        "source_url": "https://example.com/recipe",
        "ingredient_name": "Sugar",
        "ingredient_amount": "1",
        "ingredient_unit": "cup",
    }

    response = client.post("/scraper/save", data=form_data, follow_redirects=False)

    assert response.status_code == 302

    with app.app_context():
        session = _get_session(app)
        recipe = session.query(Recipe).filter_by(title="Saved Scraper Recipe").one()
        session.close()

    assert f"/recipes/{recipe.id}" in response.headers["Location"]
