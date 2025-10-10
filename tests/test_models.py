import pytest
from database import Recipe, Ingredient, NutritionInfo, MealPlan
from datetime import datetime


def test_recipe_model(db_session):
    """Test Recipe model creation and relationships."""
    # Create ingredients
    flour = Ingredient(name="Flour", amount=2.0, unit="cups")
    sugar = Ingredient(name="Sugar", amount=1.0, unit="cup")
    
    db_session.add_all([flour, sugar])
    
    # Create nutrition info
    nutrition = NutritionInfo(
        calories=300.0,
        protein=4.0,
        carbs=45.0,
        fat=12.0,
        sugar=20.0,
        sodium=50.0,
        fiber=1.5
    )
    
    # Create recipe
    recipe = Recipe(
        title="Test Cake",
        description="A simple test cake",
        instructions="1. Mix ingredients\n2. Bake",
        prep_time=10,
        cook_time=30,
        servings=8,
        image_url="https://example.com/cake.jpg",
        source_url="https://example.com/cake-recipe"
    )
    
    # Link ingredients and nutrition to recipe
    recipe.ingredients = [flour, sugar]
    recipe.nutrition = nutrition
    
    db_session.add(recipe)
    db_session.commit()
    
    # Retrieve the recipe from the database
    retrieved_recipe = db_session.query(Recipe).filter(Recipe.title == "Test Cake").first()
    
    # Verify the recipe
    assert retrieved_recipe is not None
    assert retrieved_recipe.title == "Test Cake"
    assert retrieved_recipe.description == "A simple test cake"
    assert retrieved_recipe.prep_time == 10
    assert retrieved_recipe.cook_time == 30
    assert retrieved_recipe.servings == 8
    assert retrieved_recipe.image_url == "https://example.com/cake.jpg"
    assert retrieved_recipe.source_url == "https://example.com/cake-recipe"
    
    # Verify created_at and updated_at timestamps
    assert retrieved_recipe.created_at is not None
    assert retrieved_recipe.updated_at is not None
    
    # Verify ingredients
    assert len(retrieved_recipe.ingredients) == 2
    ingredient_names = [i.name for i in retrieved_recipe.ingredients]
    assert "Flour" in ingredient_names
    assert "Sugar" in ingredient_names
    
    # Verify nutrition
    assert retrieved_recipe.nutrition is not None
    assert retrieved_recipe.nutrition.calories == 300.0
    assert retrieved_recipe.nutrition.protein == 4.0
    assert retrieved_recipe.nutrition.carbs == 45.0
    assert retrieved_recipe.nutrition.fat == 12.0
    assert retrieved_recipe.nutrition.sugar == 20.0
    assert retrieved_recipe.nutrition.sodium == 50.0
    assert retrieved_recipe.nutrition.fiber == 1.5


def test_recipe_to_dict(sample_recipe):
    """Test the to_dict method of Recipe model."""
    recipe_dict = sample_recipe.to_dict()
    
    # Check basic fields
    assert recipe_dict['id'] == sample_recipe.id
    assert recipe_dict['title'] == "Test Recipe"
    assert recipe_dict['description'] == "A test recipe"
    assert recipe_dict['instructions'] == "1. Mix ingredients\n2. Bake for 30 minutes"
    assert recipe_dict['prep_time'] == 15
    assert recipe_dict['cook_time'] == 30
    assert recipe_dict['servings'] == 4
    assert recipe_dict['image_url'] == "https://example.com/image.jpg"
    assert recipe_dict['source_url'] == "https://example.com/recipe"
    
    # Check ingredients
    assert len(recipe_dict['ingredients']) == 3
    assert recipe_dict['ingredients'][0]['name'] == "Flour"
    assert recipe_dict['ingredients'][0]['amount'] == 2.0
    assert recipe_dict['ingredients'][0]['unit'] == "cups"
    
    # Check nutrition
    assert recipe_dict['nutrition']['calories'] == 350.0
    assert recipe_dict['nutrition']['protein'] == 5.0
    assert recipe_dict['nutrition']['carbs'] == 50.0
    assert recipe_dict['nutrition']['fat'] == 10.0
    assert recipe_dict['nutrition']['sugar'] == 25.0
    assert recipe_dict['nutrition']['sodium'] == 100.0
    assert recipe_dict['nutrition']['fiber'] == 2.0


def test_ingredient_model(db_session):
    """Test Ingredient model."""
    ingredient = Ingredient(name="Salt", amount=1.0, unit="tsp")
    
    db_session.add(ingredient)
    db_session.commit()
    
    retrieved_ingredient = db_session.query(Ingredient).filter(Ingredient.name == "Salt").first()
    
    assert retrieved_ingredient is not None
    assert retrieved_ingredient.name == "Salt"
    assert retrieved_ingredient.amount == 1.0
    assert retrieved_ingredient.unit == "tsp"
    
    # Test to_dict method
    ingredient_dict = retrieved_ingredient.to_dict()
    assert ingredient_dict['id'] == retrieved_ingredient.id
    assert ingredient_dict['name'] == "Salt"
    assert ingredient_dict['amount'] == 1.0
    assert ingredient_dict['unit'] == "tsp"


def test_nutrition_info_model(db_session):
    """Test NutritionInfo model."""
    nutrition = NutritionInfo(
        calories=150.0,
        protein=3.0,
        carbs=20.0,
        fat=7.0,
        sugar=10.0,
        sodium=30.0,
        fiber=0.5
    )
    
    db_session.add(nutrition)
    db_session.commit()
    
    retrieved_nutrition = db_session.query(NutritionInfo).filter(NutritionInfo.calories == 150.0).first()
    
    assert retrieved_nutrition is not None
    assert retrieved_nutrition.calories == 150.0
    assert retrieved_nutrition.protein == 3.0
    assert retrieved_nutrition.carbs == 20.0
    assert retrieved_nutrition.fat == 7.0
    assert retrieved_nutrition.sugar == 10.0
    assert retrieved_nutrition.sodium == 30.0
    assert retrieved_nutrition.fiber == 0.5
    
    # Test to_dict method
    nutrition_dict = retrieved_nutrition.to_dict()
    assert nutrition_dict['id'] == retrieved_nutrition.id
    assert nutrition_dict['calories'] == 150.0
    assert nutrition_dict['protein'] == 3.0
    assert nutrition_dict['carbs'] == 20.0
    assert nutrition_dict['fat'] == 7.0
    assert nutrition_dict['sugar'] == 10.0
    assert nutrition_dict['sodium'] == 30.0
    assert nutrition_dict['fiber'] == 0.5


def test_meal_plan_model(db_session, sample_recipe):
    """Test MealPlan model."""
    # Create another recipe
    recipe2 = Recipe(
        title="Another Recipe",
        description="Another test recipe",
        instructions="1. Do something",
        prep_time=5,
        cook_time=15,
        servings=2
    )
    
    db_session.add(recipe2)
    db_session.commit()
    
    # Create meal plan
    meal_plan = MealPlan(
        name="Weekly Plan",
        start_date=datetime.strptime("2023-01-01", "%Y-%m-%d"),
        end_date=datetime.strptime("2023-01-07", "%Y-%m-%d"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
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
    
    # Retrieve the meal plan from the database
    retrieved_meal_plan = db_session.query(MealPlan).filter(MealPlan.name == "Weekly Plan").first()
    
    assert retrieved_meal_plan is not None
    assert retrieved_meal_plan.name == "Weekly Plan"
    assert retrieved_meal_plan.start_date.strftime("%Y-%m-%d") == "2023-01-01"
    assert retrieved_meal_plan.end_date.strftime("%Y-%m-%d") == "2023-01-07"
    assert retrieved_meal_plan.created_at is not None
    assert retrieved_meal_plan.updated_at is not None
    
    # Verify recipes are linked
    assert len(retrieved_meal_plan.recipes) == 2
    recipe_titles = [r.title for r in retrieved_meal_plan.recipes]
    assert "Test Recipe" in recipe_titles
    assert "Another Recipe" in recipe_titles
    
    # Test to_dict method
    meal_plan_dict = retrieved_meal_plan.to_dict()
    assert meal_plan_dict['id'] == retrieved_meal_plan.id
    assert meal_plan_dict['name'] == "Weekly Plan"
    assert meal_plan_dict['start_date'].startswith("2023-01-01")
    assert meal_plan_dict['end_date'].startswith("2023-01-07")

