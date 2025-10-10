import json
import pytest


def test_get_recipes(client):
    """Test retrieving recipes."""
    response = client.get('/api/recipes')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_get_recipe_by_id(client, sample_recipe, db_session):
    """Test retrieving a specific recipe by ID."""
    response = client.get(f'/api/recipes/{sample_recipe.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Test Recipe'
    assert data['description'] == 'A test recipe'
    assert data['prep_time'] == 15
    assert data['cook_time'] == 30
    assert data['servings'] == 4
    assert data['nutrition']['calories'] == 350.0
    assert len(data['ingredients']) == 3


def test_get_nonexistent_recipe(client):
    """Test retrieving a recipe that doesn't exist."""
    response = client.get('/api/recipes/9999')
    assert response.status_code == 404


def test_create_recipe(client):
    """Test creating a new recipe."""
    recipe_data = {
        "title": "New Test Recipe",
        "description": "A new test recipe",
        "instructions": "1. Do something\n2. Do something else",
        "prep_time": 10,
        "cook_time": 20,
        "servings": 2,
        "ingredients": [
            {"name": "Ingredient 1", "amount": 1.0, "unit": "cup"},
            {"name": "Ingredient 2", "amount": 2.0, "unit": "tbsp"}
        ],
        "nutrition": {
            "calories": 200.0,
            "protein": 5.0,
            "carbs": 30.0,
            "fat": 2.0
        }
    }
    
    response = client.post(
        '/api/recipes',
        data=json.dumps(recipe_data),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'New Test Recipe'
    assert len(data['ingredients']) == 2
    assert data['nutrition']['calories'] == 200.0


def test_create_recipe_missing_title(client):
    """Test creating a recipe without a title."""
    recipe_data = {
        "description": "A test recipe without a title",
        "instructions": "1. Do something"
    }
    
    response = client.post(
        '/api/recipes',
        data=json.dumps(recipe_data),
        content_type='application/json'
    )
    assert response.status_code == 400


def test_update_recipe(client, sample_recipe, db_session):
    """Test updating an existing recipe."""
    update_data = {
        "title": "Updated Recipe Title",
        "prep_time": 25
    }
    
    response = client.put(
        f'/api/recipes/{sample_recipe.id}',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Updated Recipe Title'
    assert data['prep_time'] == 25
    # Other fields should remain unchanged
    assert data['description'] == 'A test recipe'


def test_delete_recipe(client, sample_recipe, db_session):
    """Test deleting a recipe."""
    response = client.delete(f'/api/recipes/{sample_recipe.id}')
    assert response.status_code == 200
    
    # Verify the recipe is deleted
    response = client.get(f'/api/recipes/{sample_recipe.id}')
    assert response.status_code == 404


def test_get_meal_plans(client):
    """Test retrieving meal plans."""
    response = client.get('/api/meal-plans')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_get_meal_plan_by_id(client, sample_meal_plan, db_session):
    """Test retrieving a specific meal plan by ID."""
    response = client.get(f'/api/meal-plans/{sample_meal_plan.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Test Meal Plan'
    assert 'days' in data
    assert 'Monday' in data['days']
    assert 'Dinner' in data['days']['Monday']
    assert 'Tuesday' in data['days']
    assert 'Lunch' in data['days']['Tuesday']


def test_create_meal_plan(client):
    """Test creating a new meal plan."""
    meal_plan_data = {
        "name": "New Meal Plan",
        "start_date": "2023-02-01",
        "end_date": "2023-02-07"
    }
    
    response = client.post(
        '/api/meal-plans',
        data=json.dumps(meal_plan_data),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'New Meal Plan'


def test_add_recipe_to_meal_plan(client, sample_meal_plan, sample_recipe, db_session):
    """Test adding a recipe to a meal plan."""
    add_data = {
        "recipe_id": sample_recipe.id,
        "day": "Wednesday",
        "meal_type": "Breakfast"
    }
    
    response = client.post(
        f'/api/meal-plans/{sample_meal_plan.id}/recipes',
        data=json.dumps(add_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'Wednesday' in data['days']
    assert 'Breakfast' in data['days']['Wednesday']
    assert data['days']['Wednesday']['Breakfast'][0]['title'] == 'Test Recipe'


def test_remove_recipe_from_meal_plan(client, sample_meal_plan, sample_recipe, db_session):
    """Test removing a recipe from a meal plan."""
    remove_data = {
        "day": "Monday",
        "meal_type": "Dinner"
    }
    
    response = client.delete(
        f'/api/meal-plans/{sample_meal_plan.id}/recipes/{sample_recipe.id}',
        data=json.dumps(remove_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # The recipe should be removed from Monday Dinner
    assert 'Monday' in data['days']
    if 'Dinner' in data['days']['Monday']:
        assert len(data['days']['Monday']['Dinner']) == 0


def test_calculate_nutrition(client):
    """Test the nutrition calculation endpoint."""
    ingredients = [
        {"name": "flour", "amount": 100, "unit": "g"},
        {"name": "sugar", "amount": 50, "unit": "g"},
        {"name": "butter", "amount": 30, "unit": "g"}
    ]
    
    response = client.post(
        '/api/nutrition/calculate',
        data=json.dumps({"ingredients": ingredients}),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'calories' in data
    assert 'protein' in data
    assert 'carbs' in data
    assert 'fat' in data
    assert 'sugar' in data
    assert 'sodium' in data
    assert 'fiber' in data


def test_scrape_recipe(client, monkeypatch):
    """Test the recipe scraper endpoint."""
    # Mock the scraper service to return a fixed recipe
    def mock_scrape_recipe(url):
        return {
            "title": "Mocked Recipe",
            "description": "A mocked recipe for testing",
            "ingredients": [
                {"name": "Mocked Ingredient", "amount": 1.0, "unit": "cup"}
            ],
            "instructions": "1. This is a mocked instruction.",
            "prep_time": 10,
            "cook_time": 20,
            "servings": 4,
            "image_url": "https://example.com/image.jpg",
            "source_url": url
        }
    
    from app.services.scraper_service import ScraperService
    monkeypatch.setattr(ScraperService, 'scrape_recipe', mock_scrape_recipe)
    
    response = client.post(
        '/api/scrape',
        data=json.dumps({"url": "https://example.com/recipe"}),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Mocked Recipe'
    assert len(data['ingredients']) == 1
    assert data['ingredients'][0]['name'] == 'Mocked Ingredient'

