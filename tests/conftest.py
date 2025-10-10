import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Add the parent directory to the path so that imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database import Base, Recipe, Ingredient, NutritionInfo, MealPlan


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Use a temporary in-memory database for testing
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def db_engine():
    """Create a database engine for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    """Create a database session for testing."""
    session = Session(db_engine)
    yield session
    session.close()


@pytest.fixture
def sample_recipe(db_session):
    """Create a sample recipe for testing."""
    # Create ingredients
    ingredient1 = Ingredient(name="Flour", amount=2.0, unit="cups")
    ingredient2 = Ingredient(name="Sugar", amount=1.0, unit="cup")
    ingredient3 = Ingredient(name="Eggs", amount=2.0, unit="whole")
    
    db_session.add_all([ingredient1, ingredient2, ingredient3])
    
    # Create nutrition info
    nutrition = NutritionInfo(
        calories=350.0,
        protein=5.0,
        carbs=50.0,
        fat=10.0,
        sugar=25.0,
        sodium=100.0,
        fiber=2.0
    )
    
    # Create recipe
    recipe = Recipe(
        title="Test Recipe",
        description="A test recipe",
        instructions="1. Mix ingredients\n2. Bake for 30 minutes",
        prep_time=15,
        cook_time=30,
        servings=4,
        image_url="https://example.com/image.jpg",
        source_url="https://example.com/recipe"
    )
    
    # Link ingredients and nutrition to recipe
    recipe.ingredients = [ingredient1, ingredient2, ingredient3]
    recipe.nutrition = nutrition
    
    db_session.add(recipe)
    db_session.commit()
    
    return recipe


@pytest.fixture
def sample_meal_plan(db_session, sample_recipe):
    """Create a sample meal plan for testing."""
    # Create another recipe for the meal plan
    recipe2 = Recipe(
        title="Another Test Recipe",
        description="Another test recipe",
        instructions="1. Prepare ingredients\n2. Cook for 20 minutes",
        prep_time=10,
        cook_time=20,
        servings=2
    )
    
    db_session.add(recipe2)
    db_session.commit()
    
    # Create meal plan
    meal_plan = MealPlan(
        name="Test Meal Plan",
        start_date="2023-01-01",
        end_date="2023-01-07"
    )
    
    db_session.add(meal_plan)
    db_session.commit()
    
    # Add recipes to meal plan via association table
    from sqlalchemy import text
    db_session.execute(
        text("INSERT INTO meal_plan_recipe (meal_plan_id, recipe_id, day, meal_type) VALUES (:meal_plan_id, :recipe_id, :day, :meal_type)"),
        {"meal_plan_id": meal_plan.id, "recipe_id": sample_recipe.id, "day": "Monday", "meal_type": "Dinner"}
    )
    db_session.execute(
        text("INSERT INTO meal_plan_recipe (meal_plan_id, recipe_id, day, meal_type) VALUES (:meal_plan_id, :recipe_id, :day, :meal_type)"),
        {"meal_plan_id": meal_plan.id, "recipe_id": recipe2.id, "day": "Tuesday", "meal_type": "Lunch"}
    )
    
    db_session.commit()
    
    return meal_plan

