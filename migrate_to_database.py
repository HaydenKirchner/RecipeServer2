import os
import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Recipe, Ingredient, NutritionInfo, MealPlan, get_env_db_url

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def migrate_json_to_db(json_file_path, db_url=None):
    """
    Migrate recipe data from a JSON file to the database.
    
    Args:
        json_file_path (str): Path to the JSON file containing recipe data.
        db_url (str, optional): Database URL. If None, will use the environment-specific URL.
    
    Returns:
        bool: True if migration was successful, False otherwise.
    """
    try:
        # Check if the JSON file exists
        if not os.path.exists(json_file_path):
            logger.error(f"JSON file not found: {json_file_path}")
            return False
        
        # Load the JSON data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            recipe_data = json.load(f)
        
        # Get the database URL
        if db_url is None:
            db_url = get_env_db_url()
        
        # Create the database engine and session
        engine = create_engine(db_url)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Process each recipe
        recipes_added = 0
        for recipe_json in recipe_data:
            try:
                # Check if recipe already exists by title
                existing_recipe = session.query(Recipe).filter(Recipe.title == recipe_json['title']).first()
                if existing_recipe:
                    logger.info(f"Recipe already exists: {recipe_json['title']}")
                    continue
                
                # Create the recipe
                recipe = Recipe(
                    title=recipe_json['title'],
                    description=recipe_json.get('description', ''),
                    instructions=recipe_json.get('instructions', ''),
                    prep_time=recipe_json.get('prep_time'),
                    cook_time=recipe_json.get('cook_time'),
                    servings=recipe_json.get('servings'),
                    image_url=recipe_json.get('image_url'),
                    source_url=recipe_json.get('source_url')
                )
                
                # Add ingredients
                if 'ingredients' in recipe_json:
                    for ingredient_json in recipe_json['ingredients']:
                        # Check if ingredient already exists
                        ingredient_name = ingredient_json.get('name', '')
                        if not ingredient_name:
                            continue
                        
                        ingredient = session.query(Ingredient).filter(Ingredient.name == ingredient_name).first()
                        if not ingredient:
                            ingredient = Ingredient(
                                name=ingredient_name,
                                amount=ingredient_json.get('amount'),
                                unit=ingredient_json.get('unit')
                            )
                            session.add(ingredient)
                        
                        recipe.ingredients.append(ingredient)
                
                # Add nutrition info
                if 'nutrition' in recipe_json:
                    nutrition = NutritionInfo(
                        calories=recipe_json['nutrition'].get('calories'),
                        protein=recipe_json['nutrition'].get('protein'),
                        carbs=recipe_json['nutrition'].get('carbs'),
                        fat=recipe_json['nutrition'].get('fat'),
                        sugar=recipe_json['nutrition'].get('sugar'),
                        sodium=recipe_json['nutrition'].get('sodium'),
                        fiber=recipe_json['nutrition'].get('fiber')
                    )
                    recipe.nutrition = nutrition
                
                session.add(recipe)
                recipes_added += 1
                
                # Commit in batches to avoid memory issues
                if recipes_added % 10 == 0:
                    session.commit()
                    logger.info(f"Committed {recipes_added} recipes so far")
            
            except Exception as e:
                logger.error(f"Error processing recipe {recipe_json.get('title', 'Unknown')}: {str(e)}")
                continue
        
        # Final commit
        session.commit()
        logger.info(f"Successfully migrated {recipes_added} recipes to the database")
        
        return True
    
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        return False

if __name__ == "__main__":
    # Default JSON file path
    default_json_path = os.path.join('data', 'recipes.json')
    
    # Allow custom JSON file path from command line arguments
    import sys
    json_path = sys.argv[1] if len(sys.argv) > 1 else default_json_path
    
    logger.info(f"Starting migration from {json_path} to database")
    success = migrate_json_to_db(json_path)
    
    if success:
        logger.info("Migration completed successfully")
    else:
        logger.error("Migration failed")
