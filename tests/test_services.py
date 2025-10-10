import pytest
import os
from app.services.recipe_service import RecipeService
from app.services.meal_plan_service import MealPlanService
from app.services.scraper_service import ScraperService
from app.services.nutrition_service import NutritionService
from app.services.pdf_service import PDFService
from database import Recipe, Ingredient, NutritionInfo, MealPlan
from sqlalchemy import and_, text
from unittest.mock import patch, MagicMock


def test_recipe_service_get_recipes(db_session, sample_recipe):
    """Test getting recipes with RecipeService."""
    service = RecipeService(db_session)
    
    # Get all recipes
    recipes = service.get_recipes()
    assert len(recipes) == 1
    assert recipes[0].title == "Test Recipe"
    
    # Test with search filter
    recipes = service.get_recipes({'search': 'test'})
    assert len(recipes) == 1
    
    recipes = service.get_recipes({'search': 'nonexistent'})
    assert len(recipes) == 0
    
    # Test with ingredient filter
    recipes = service.get_recipes({'ingredient': 'flour'})
    assert len(recipes) == 1
    
    recipes = service.get_recipes({'ingredient': 'nonexistent'})
    assert len(recipes) == 0
    
    # Test with calorie filter
    recipes = service.get_recipes({'min_calories': 300, 'max_calories': 400})
    assert len(recipes) == 1
    
    recipes = service.get_recipes({'min_calories': 500})
    assert len(recipes) == 0
    
    # Test with sort
    recipes = service.get_recipes({'sort_by': 'title', 'sort_direction': 'asc'})
    assert len(recipes) == 1
    assert recipes[0].title == "Test Recipe"


def test_recipe_service_get_recipe_by_id(db_session, sample_recipe):
    """Test getting a recipe by ID with RecipeService."""
    service = RecipeService(db_session)
    
    recipe = service.get_recipe_by_id(sample_recipe.id)
    assert recipe is not None
    assert recipe.title == "Test Recipe"
    
    recipe = service.get_recipe_by_id(9999)  # Non-existent ID
    assert recipe is None


def test_recipe_service_create_recipe(db_session):
    """Test creating a recipe with RecipeService."""
    service = RecipeService(db_session)
    
    recipe_data = {
        "title": "New Recipe",
        "description": "A new recipe",
        "instructions": "1. Step one\n2. Step two",
        "prep_time": 10,
        "cook_time": 20,
        "servings": 4,
        "ingredients": [
            {"name": "Ingredient 1", "amount": 1.0, "unit": "cup"},
            {"name": "Ingredient 2", "amount": 2.0, "unit": "tbsp"}
        ],
        "nutrition": {
            "calories": 250.0,
            "protein": 5.0,
            "carbs": 30.0,
            "fat": 10.0
        }
    }
    
    recipe = service.create_recipe(recipe_data)
    assert recipe is not None
    assert recipe.title == "New Recipe"
    assert len(recipe.ingredients) == 2
    assert recipe.nutrition is not None
    assert recipe.nutrition.calories == 250.0


def test_recipe_service_update_recipe(db_session, sample_recipe):
    """Test updating a recipe with RecipeService."""
    service = RecipeService(db_session)
    
    update_data = {
        "title": "Updated Recipe",
        "prep_time": 25,
        "ingredients": [
            {"name": "New Ingredient", "amount": 3.0, "unit": "oz"}
        ],
        "nutrition": {
            "calories": 400.0
        }
    }
    
    updated_recipe = service.update_recipe(sample_recipe.id, update_data)
    assert updated_recipe is not None
    assert updated_recipe.title == "Updated Recipe"
    assert updated_recipe.prep_time == 25
    assert updated_recipe.cook_time == 30  # Unchanged
    assert len(updated_recipe.ingredients) == 1
    assert updated_recipe.ingredients[0].name == "New Ingredient"
    assert updated_recipe.nutrition.calories == 400.0


def test_recipe_service_delete_recipe(db_session, sample_recipe):
    """Test deleting a recipe with RecipeService."""
    service = RecipeService(db_session)
    
    result = service.delete_recipe(sample_recipe.id)
    assert result is True
    
    # Verify the recipe is deleted
    recipe = db_session.query(Recipe).filter(Recipe.id == sample_recipe.id).first()
    assert recipe is None
    
    # Try deleting a non-existent recipe
    result = service.delete_recipe(9999)
    assert result is False


@patch('app.services.recipe_service.PDFService')
def test_recipe_service_generate_pdf(mock_pdf_service, db_session, sample_recipe):
    """Test generating a PDF for a recipe with RecipeService."""
    # Mock the PDF service's generate_recipe_pdf method to return True
    mock_pdf_instance = MagicMock()
    mock_pdf_instance.generate_recipe_pdf.return_value = True
    mock_pdf_service.return_value = mock_pdf_instance
    
    service = RecipeService(db_session)
    
    # Create a temp directory for PDFs
    os.makedirs('static/pdfs', exist_ok=True)
    
    pdf_path = service.generate_pdf(sample_recipe.id)
    assert pdf_path is not None
    assert 'static/pdfs' in pdf_path
    assert 'recipe_' in pdf_path
    assert '.pdf' in pdf_path
    
    # Verify that the recipe's pdf_path field was updated
    updated_recipe = db_session.query(Recipe).filter(Recipe.id == sample_recipe.id).first()
    assert updated_recipe.pdf_path == pdf_path
    
    # Clean up
    try:
        os.remove(pdf_path)
    except:
        pass


def test_meal_plan_service_get_meal_plans(db_session, sample_meal_plan):
    """Test getting meal plans with MealPlanService."""
    service = MealPlanService(db_session)
    
    meal_plans = service.get_meal_plans()
    assert len(meal_plans) == 1
    assert meal_plans[0].name == "Test Meal Plan"
    
    # Test with limit
    meal_plans = service.get_meal_plans({'limit': 1})
    assert len(meal_plans) == 1


def test_meal_plan_service_get_meal_plan_by_id(db_session, sample_meal_plan):
    """Test getting a meal plan by ID with MealPlanService."""
    service = MealPlanService(db_session)
    
    meal_plan = service.get_meal_plan_by_id(sample_meal_plan.id)
    assert meal_plan is not None
    assert meal_plan.name == "Test Meal Plan"
    
    meal_plan = service.get_meal_plan_by_id(9999)  # Non-existent ID
    assert meal_plan is None


def test_meal_plan_service_create_meal_plan(db_session):
    """Test creating a meal plan with MealPlanService."""
    service = MealPlanService(db_session)
    
    meal_plan_data = {
        "name": "New Meal Plan",
        "start_date": "2023-02-01",
        "end_date": "2023-02-07"
    }
    
    meal_plan = service.create_meal_plan(meal_plan_data)
    assert meal_plan is not None
    assert meal_plan.name == "New Meal Plan"
    assert meal_plan.start_date.strftime("%Y-%m-%d") == "2023-02-01"
    assert meal_plan.end_date.strftime("%Y-%m-%d") == "2023-02-07"


def test_meal_plan_service_update_meal_plan(db_session, sample_meal_plan):
    """Test updating a meal plan with MealPlanService."""
    service = MealPlanService(db_session)
    
    update_data = {
        "name": "Updated Meal Plan",
        "end_date": "2023-01-14"
    }
    
    updated_meal_plan = service.update_meal_plan(sample_meal_plan.id, update_data)
    assert updated_meal_plan is not None
    assert updated_meal_plan.name == "Updated Meal Plan"
    assert updated_meal_plan.end_date.strftime("%Y-%m-%d") == "2023-01-14"
    assert updated_meal_plan.start_date.strftime("%Y-%m-%d") == "2023-01-01"  # Unchanged


def test_meal_plan_service_delete_meal_plan(db_session, sample_meal_plan):
    """Test deleting a meal plan with MealPlanService."""
    service = MealPlanService(db_session)
    
    result = service.delete_meal_plan(sample_meal_plan.id)
    assert result is True
    
    # Verify the meal plan is deleted
    meal_plan = db_session.query(MealPlan).filter(MealPlan.id == sample_meal_plan.id).first()
    assert meal_plan is None
    
    # Try deleting a non-existent meal plan
    result = service.delete_meal_plan(9999)
    assert result is False


def test_meal_plan_service_add_recipe_to_meal_plan(db_session, sample_meal_plan, sample_recipe):
    """Test adding a recipe to a meal plan with MealPlanService."""
    service = MealPlanService(db_session)
    
    # Add a recipe to a different day/meal type
    meal_plan = service.add_recipe_to_meal_plan(
        sample_meal_plan.id, 
        sample_recipe.id,
        "Wednesday",
        "Breakfast"
    )
    
    assert meal_plan is not None
    
    # Verify the recipe was added to the meal plan
    result = db_session.execute(
        text("""
            SELECT * FROM meal_plan_recipe 
            WHERE meal_plan_id = :meal_plan_id 
              AND recipe_id = :recipe_id
              AND day = :day
              AND meal_type = :meal_type
        """),
        {
            "meal_plan_id": sample_meal_plan.id,
            "recipe_id": sample_recipe.id,
            "day": "Wednesday",
            "meal_type": "Breakfast"
        }
    ).fetchone()
    
    assert result is not None


def test_meal_plan_service_remove_recipe_from_meal_plan(db_session, sample_meal_plan, sample_recipe):
    """Test removing a recipe from a meal plan with MealPlanService."""
    service = MealPlanService(db_session)
    
    # First, verify the test recipe is in the meal plan for Monday Dinner
    result = db_session.execute(
        text("""
            SELECT * FROM meal_plan_recipe 
            WHERE meal_plan_id = :meal_plan_id 
              AND recipe_id = :recipe_id
              AND day = :day
              AND meal_type = :meal_type
        """),
        {
            "meal_plan_id": sample_meal_plan.id,
            "recipe_id": sample_recipe.id,
            "day": "Monday",
            "meal_type": "Dinner"
        }
    ).fetchone()
    
    assert result is not None
    
    # Remove the recipe from the meal plan
    meal_plan = service.remove_recipe_from_meal_plan(
        sample_meal_plan.id,
        sample_recipe.id,
        "Monday",
        "Dinner"
    )
    
    assert meal_plan is not None
    
    # Verify the recipe was removed
    result = db_session.execute(
        text("""
            SELECT * FROM meal_plan_recipe 
            WHERE meal_plan_id = :meal_plan_id 
              AND recipe_id = :recipe_id
              AND day = :day
              AND meal_type = :meal_type
        """),
        {
            "meal_plan_id": sample_meal_plan.id,
            "recipe_id": sample_recipe.id,
            "day": "Monday",
            "meal_type": "Dinner"
        }
    ).fetchone()
    
    assert result is None


def test_meal_plan_service_get_meal_plan_with_recipes(db_session, sample_meal_plan, sample_recipe):
    """Test retrieving a meal plan with organized recipes."""
    service = MealPlanService(db_session)
    
    meal_plan_data = service.get_meal_plan_with_recipes(sample_meal_plan)
    assert meal_plan_data is not None
    assert meal_plan_data['name'] == "Test Meal Plan"
    assert 'days' in meal_plan_data
    assert 'Monday' in meal_plan_data['days']
    assert 'Dinner' in meal_plan_data['days']['Monday']
    assert len(meal_plan_data['days']['Monday']['Dinner']) == 1
    assert meal_plan_data['days']['Monday']['Dinner'][0]['title'] == "Test Recipe"


@patch('app.services.nutrition_service.NutritionService.calculate_nutrition')
@patch('trafilatura.fetch_url')
@patch('trafilatura.extract')
def test_scraper_service_scrape_recipe(mock_extract, mock_fetch_url, mock_calculate_nutrition, db_session):
    """Test scraping a recipe with ScraperService."""
    # Mock the trafilatura functions
    mock_fetch_url.return_value = b'<html><body>Recipe content</body></html>'
    mock_extract.return_value = """
    Recipe Title
    
    Description of the recipe.
    
    Ingredients:
    - 1 cup flour
    - 2 tbsp sugar
    
    Instructions:
    1. Mix ingredients
    2. Bake at 350°F
    
    Prep time: 10 minutes
    Cook time: 30 minutes
    Servings: 4
    """
    
    # Mock the nutrition calculation
    mock_calculate_nutrition.return_value = {
        "calories": 200.0,
        "protein": 5.0,
        "carbs": 30.0,
        "fat": 2.0,
        "sugar": 15.0,
        "sodium": 50.0,
        "fiber": 1.0
    }
    
    service = ScraperService()
    
    recipe_data = service.scrape_recipe("https://example.com/recipe")
    assert recipe_data is not None
    assert 'title' in recipe_data
    assert 'ingredients' in recipe_data
    assert 'instructions' in recipe_data
    assert 'source_url' in recipe_data
    assert recipe_data['source_url'] == "https://example.com/recipe"


def test_nutrition_service_calculate_nutrition(db_session):
    """Test calculating nutrition information with NutritionService."""
    service = NutritionService()
    
    ingredients = [
        {"name": "flour", "amount": 100, "unit": "g"},
        {"name": "sugar", "amount": 50, "unit": "g"},
        {"name": "egg", "amount": 1, "unit": "whole"}
    ]
    
    nutrition = service.calculate_nutrition(ingredients)
    assert nutrition is not None
    assert 'calories' in nutrition
    assert 'protein' in nutrition
    assert 'carbs' in nutrition
    assert 'fat' in nutrition
    assert 'sugar' in nutrition
    assert 'sodium' in nutrition
    assert 'fiber' in nutrition
    
    # Test with string ingredients
    ingredients_str = ["flour", "sugar", "egg"]
    nutrition = service.calculate_nutrition(ingredients_str)
    assert nutrition is not None
    assert all(key in nutrition for key in ["calories", "protein", "carbs", "fat", "sugar", "sodium", "fiber"])


def test_pdf_service(sample_recipe):
    """Test generating a PDF with PDFService."""
    service = PDFService()
    
    # Create a temp directory for PDFs
    os.makedirs('static/pdfs', exist_ok=True)
    
    # Generate a test PDF
    pdf_path = 'static/pdfs/test_recipe.pdf'
    result = service.generate_recipe_pdf(sample_recipe, pdf_path)
    assert result is True
    
    # Verify the PDF was created
    assert os.path.exists(pdf_path)
    
    # Clean up
    try:
        os.remove(pdf_path)
    except:
        pass

