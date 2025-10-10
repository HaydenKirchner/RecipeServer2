"""
Debug script to help diagnose the issue with recipe instructions not saving.
"""
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import our modules
sys.path.append('.')

# Import the database and recipe service
from database import get_db_session, Recipe
from app.services.recipe_service import RecipeService

def main():
    """Main function to debug recipe instructions."""
    try:
        # Get database session
        db_session = get_db_session()
        recipe_service = RecipeService(db_session)
        
        # Get the first recipe from the database
        recipe = db_session.query(Recipe).first()
        if not recipe:
            logger.error("No recipes found in the database.")
            return
        
        logger.info(f"Found recipe: id={recipe.id}, title='{recipe.title}'")
        logger.info(f"Current instructions: '{recipe.instructions}'")
        
        # Update the recipe instructions directly
        new_instructions = "These are test instructions.\nStep 1: Do something.\nStep 2: Do something else."
        logger.info(f"Setting new instructions: '{new_instructions}'")
        
        # Try updating via the service
        update_data = {
            'title': recipe.title,
            'instructions': new_instructions
        }
        
        updated_recipe = recipe_service.update_recipe(recipe.id, update_data)
        
        if updated_recipe:
            logger.info(f"Recipe updated. New instructions: '{updated_recipe.instructions}'")
            
            # Verify in the database directly
            refreshed_recipe = db_session.query(Recipe).filter(Recipe.id == recipe.id).first()
            logger.info(f"Refreshed from DB - instructions: '{refreshed_recipe.instructions}'")
        else:
            logger.error("Failed to update recipe")
        
    except Exception as e:
        logger.exception(f"Error in debug script: {str(e)}")

if __name__ == "__main__":
    main()