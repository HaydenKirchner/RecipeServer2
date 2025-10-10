import os
import shutil
import sqlite3
import logging
from database import get_env_db_url

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def migrate_to_env_db():
    """
    Migrate data from the old recipes.db to environment-specific databases.
    
    This script is used when transitioning from a single database file to
    environment-specific database files (development.db, testing.db, production.db).
    """
    # Path to the old database
    old_db_path = os.path.join('data', 'recipes.db')
    
    # Check if the old database exists
    if not os.path.exists(old_db_path):
        logger.warning("Original recipes.db not found. Nothing to migrate.")
        return False
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Get environment-specific database paths
    env_db_paths = {
        'development': get_db_path_from_url(get_env_db_url()),
        'testing': get_db_path_from_url(get_env_db_url('testing')),
        'production': get_db_path_from_url(get_env_db_url('production'))
    }
    
    # Copy the old database to the new environment-specific databases
    for env, db_path in env_db_paths.items():
        try:
            if os.path.exists(db_path):
                logger.warning(f"{env} database already exists. Backing up...")
                backup_path = f"{db_path}.bak"
                shutil.copy2(db_path, backup_path)
            
            logger.info(f"Copying recipes.db to {env} database at {db_path}")
            shutil.copy2(old_db_path, db_path)
            
            # Verify the new database
            verify_db(db_path)
            
            logger.info(f"Successfully migrated data to {env} database")
        except Exception as e:
            logger.error(f"Error migrating to {env} database: {str(e)}")
            continue
    
    # Rename the old database as a backup
    try:
        backup_path = f"{old_db_path}.bak"
        logger.info(f"Renaming original database to {backup_path}")
        os.rename(old_db_path, backup_path)
    except Exception as e:
        logger.error(f"Error backing up original database: {str(e)}")
    
    return True

def get_db_path_from_url(db_url):
    """Extract the file path from a SQLite database URL."""
    if db_url.startswith('sqlite:///'):
        return db_url[10:]  # Remove 'sqlite:///' prefix
    return None

def get_env_db_url(env=None):
    """Get the database URL for a specific environment."""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    # Use the database.py function if it exists, otherwise build the URL manually
    try:
        from database import get_env_db_url as db_get_env_db_url
        return db_get_env_db_url(env)
    except (ImportError, AttributeError):
        return f'sqlite:///data/{env}.db'

def verify_db(db_path):
    """Verify that a database file exists and is a valid SQLite database."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        logger.info(f"Verified database {db_path} with {len(tables)} tables")
        return True
    except sqlite3.Error as e:
        raise ValueError(f"Invalid SQLite database: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting database migration to environment-specific databases")
    success = migrate_to_env_db()
    
    if success:
        logger.info("Database migration completed successfully")
    else:
        logger.warning("Database migration did not complete")
