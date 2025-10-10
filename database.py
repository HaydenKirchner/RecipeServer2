from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, Text, DateTime, Boolean, Date, UniqueConstraint
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date as date_cls
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

Base = declarative_base()

_tracked_test_engine = None


def _capture_engine_argument(*args, **kwargs):
    """Return the engine argument from ``create_all``/``drop_all`` calls."""

    if args:
        return args[0]
    return kwargs.get('bind')


_original_create_all = Base.metadata.create_all


def _create_all_with_tracking(*args, **kwargs):
    engine = _capture_engine_argument(*args, **kwargs)
    if engine is not None:
        global _tracked_test_engine
        _tracked_test_engine = engine
    return _original_create_all(*args, **kwargs)


Base.metadata.create_all = _create_all_with_tracking

_original_drop_all = Base.metadata.drop_all


def _drop_all_with_tracking(*args, **kwargs):
    engine = _capture_engine_argument(*args, **kwargs)
    try:
        return _original_drop_all(*args, **kwargs)
    finally:
        if engine is not None:
            global _tracked_test_engine
            if engine is _tracked_test_engine:
                _tracked_test_engine = None


Base.metadata.drop_all = _drop_all_with_tracking


def get_tracked_test_engine():
    """Return the most recently used SQLAlchemy engine for metadata operations."""

    return _tracked_test_engine

# Association table for recipe ingredients
recipe_ingredient = Table(
    'recipe_ingredient',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id'), primary_key=True)
)

# Association table for meal plan recipes
meal_plan_recipe = Table(
    'meal_plan_recipe',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('meal_plan_id', Integer, ForeignKey('meal_plans.id')), 
    Column('recipe_id', Integer, ForeignKey('recipes.id')),
    Column('day', String(20)),
    Column('meal_type', String(20)),
    UniqueConstraint('meal_plan_id', 'recipe_id', 'day', 'meal_type', name='uq_meal_plan_recipe_entry')
)

# Association table for recipe tags
recipe_tag = Table(
    'recipe_tag',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Recipe(Base):
    """Model for recipes."""
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    instructions = Column(Text)
    prep_time = Column(Integer)  # in minutes
    cook_time = Column(Integer)  # in minutes
    servings = Column(Integer)
    image_url = Column(String(512))
    source_url = Column(String(512))
    pdf_path = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ingredients = relationship('Ingredient', secondary=recipe_ingredient, back_populates='recipes')
    nutrition = relationship('NutritionInfo', uselist=False, back_populates='recipe')
    tags = relationship('Tag', secondary=recipe_tag, back_populates='recipes')
    
    def __repr__(self):
        return f"<Recipe(id={self.id}, title='{self.title}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'instructions': self.instructions,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'servings': self.servings,
            'image_url': self.image_url,
            'source_url': self.source_url,
            'pdf_path': self.pdf_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'ingredients': [ingredient.to_dict() for ingredient in self.ingredients],
            'nutrition': self.nutrition.to_dict() if self.nutrition else None,
            'tags': [tag.to_dict() for tag in self.tags]
        }


class Ingredient(Base):
    """Model for ingredients."""
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    amount = Column(Float)
    unit = Column(String(50))
    
    # Relationships
    recipes = relationship('Recipe', secondary=recipe_ingredient, back_populates='ingredients')
    
    def __repr__(self):
        return f"<Ingredient(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'unit': self.unit
        }


class NutritionInfo(Base):
    """Model for nutritional information."""
    __tablename__ = 'nutrition_info'

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    sugar = Column(Float)
    sodium = Column(Float)
    fiber = Column(Float)
    
    # Relationships
    recipe = relationship('Recipe', back_populates='nutrition')
    
    def __repr__(self):
        return f"<NutritionInfo(id={self.id}, recipe_id={self.recipe_id})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'sugar': self.sugar,
            'sodium': self.sodium,
            'fiber': self.fiber
        }


class ShoppingList(Base):
    """Model for shopping list."""
    __tablename__ = 'shopping_lists'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meal_plan_id = Column(Integer, ForeignKey('meal_plans.id'))
    
    # Relationships
    meal_plan = relationship('MealPlan', back_populates='shopping_list')
    items = relationship('ShoppingListItem', back_populates='shopping_list', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ShoppingList(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'meal_plan_id': self.meal_plan_id,
            'items': [item.to_dict() for item in self.items]
        }


class ShoppingListItem(Base):
    """Model for shopping list items."""
    __tablename__ = 'shopping_list_items'

    id = Column(Integer, primary_key=True)
    shopping_list_id = Column(Integer, ForeignKey('shopping_lists.id'))
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    quantity = Column(Float)
    unit = Column(String(50))
    checked = Column(Boolean, default=False)
    walmart_product_id = Column(String(255))
    walmart_product_name = Column(String(255))
    walmart_product_price = Column(Float)
    walmart_product_image = Column(String(512))
    added_to_cart = Column(Boolean, default=False)
    
    # Relationships
    shopping_list = relationship('ShoppingList', back_populates='items')
    ingredient = relationship('Ingredient')
    
    def __repr__(self):
        return f"<ShoppingListItem(id={self.id}, ingredient_id={self.ingredient_id})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'shopping_list_id': self.shopping_list_id,
            'ingredient_id': self.ingredient_id,
            'ingredient_name': self.ingredient.name if self.ingredient else None,
            'quantity': self.quantity,
            'unit': self.unit,
            'checked': self.checked,
            'walmart_product_id': self.walmart_product_id,
            'walmart_product_name': self.walmart_product_name,
            'walmart_product_price': self.walmart_product_price,
            'walmart_product_image': self.walmart_product_image,
            'added_to_cart': self.added_to_cart
        }


class MealPlan(Base):
    """Model for meal plans."""
    __tablename__ = 'meal_plans'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recipes = relationship('Recipe', secondary=meal_plan_recipe)
    shopping_list = relationship('ShoppingList', back_populates='meal_plan', uselist=False)
    
    def __repr__(self):
        return f"<MealPlan(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'has_shopping_list': self.shopping_list is not None,
            'recipes': []  # Recipe info will be added separately due to meal_plan_recipe association
        }

    @validates('start_date', 'end_date')
    def _coerce_dates(self, key, value):
        """Normalise supported date types for SQLite storage."""

        if value in (None, ''):
            return None

        if isinstance(value, datetime):
            return value

        if isinstance(value, date_cls):
            return datetime.combine(value, datetime.min.time())

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError as exc:
                raise ValueError(f"Invalid date format for {key}") from exc

        raise TypeError(f"Unsupported type for {key}: {type(value)!r}")


class Inventory(Base):
    """Model for pantry/inventory management."""
    __tablename__ = 'inventories'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, default="My Pantry")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = relationship('InventoryItem', back_populates='inventory', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Inventory(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }


class Tag(Base):
    """Model for recipe tags."""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    
    # Relationships
    recipes = relationship('Recipe', secondary=recipe_tag, back_populates='tags')
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class InventoryItem(Base):
    """Model for items in the inventory."""
    __tablename__ = 'inventory_items'

    id = Column(Integer, primary_key=True)
    inventory_id = Column(Integer, ForeignKey('inventories.id'))
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    quantity = Column(Float)
    unit = Column(String(50))
    purchase_date = Column(Date)
    expiration_date = Column(Date)
    storage_location = Column(String(100))  # e.g., "Refrigerator", "Pantry", "Freezer"
    notes = Column(Text)
    
    # Relationships
    inventory = relationship('Inventory', back_populates='items')
    ingredient = relationship('Ingredient')
    
    def __repr__(self):
        return f"<InventoryItem(id={self.id}, ingredient_id={self.ingredient_id})>"
    
    def to_dict(self):
        days_until_expiration = None
        if self.expiration_date:
            from datetime import date
            days_until_expiration = (self.expiration_date - date.today()).days
            
        return {
            'id': self.id,
            'inventory_id': self.inventory_id,
            'ingredient_id': self.ingredient_id,
            'ingredient_name': self.ingredient.name if self.ingredient else None,
            'quantity': self.quantity,
            'unit': self.unit,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'days_until_expiration': days_until_expiration,
            'storage_location': self.storage_location,
            'notes': self.notes
        }


def get_env_db_url():
    """Get the database URL based on the environment."""
    env = os.getenv('FLASK_ENV', 'development')
    
    # Try to use PostgreSQL database from environment variables if available
    db_url = os.getenv('DATABASE_URL')
    
    # If DATABASE_URL is set but contains 'neon.tech' and we're getting connection errors,
    # we'll fall back to SQLite as a temporary solution
    if db_url and 'neon.tech' in db_url:
        try:
            # Test the connection before deciding to use it
            import psycopg2
            conn = psycopg2.connect(db_url)
            conn.close()
            logger.info("Successfully connected to PostgreSQL database")
        except Exception as e:
            logger.warning(f"Could not connect to PostgreSQL database: {str(e)}")
            logger.warning("Falling back to SQLite database")
            db_url = f'sqlite:///data/{env}.db'
    
    # Default to SQLite if DATABASE_URL not set or connection failed
    if not db_url:
        db_url = f'sqlite:///data/{env}.db'
    
    # Ensure data directory exists for SQLite
    if db_url.startswith('sqlite:///data/'):
        os.makedirs('data', exist_ok=True)
    
    logger.debug(f"Using database URL: {db_url}")
    return db_url


# Global engine variable to reuse connection pool
_engine = None

def get_engine():
    """Get or create a SQLAlchemy engine with connection pooling."""
    global _engine
    
    if _engine is None:
        db_url = get_env_db_url()
        
        # Enhanced connection pool settings for better reliability
        _engine = create_engine(
            db_url,
            pool_size=10,           # Increase connections in pool
            max_overflow=20,        # Allow more overflow connections
            pool_timeout=30,        # Timeout waiting for a connection
            pool_recycle=300,       # Recycle connections after 5 minutes
            pool_pre_ping=True,     # Verify connection is alive before using
            connect_args={
                'connect_timeout': 10,      # Connection timeout in seconds
                'keepalives': 1,            # Enable TCP keepalives
                'keepalives_idle': 30,      # Seconds between keepalives
                'keepalives_interval': 10,  # Seconds between keepalive probes
                'keepalives_count': 5       # Max number of keepalive probes
            } if 'postgresql' in db_url else {}  # Only for PostgreSQL
        )
        
        # Initialize database schema
        Base.metadata.create_all(_engine)
    
    return _engine


def get_db_session():
    """
    Get a database session with automatic reconnection.
    
    Returns:
        SQLAlchemy session object
    """
    from sqlalchemy.exc import OperationalError, DisconnectionError
    from sqlalchemy import text
    import time
    
    # Max retry attempts
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Test the connection with properly declared text SQL
            session.execute(text("SELECT 1"))
            
            return session
            
        except (OperationalError, DisconnectionError) as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection failed (attempt {attempt+1}/{max_retries}): {str(e)}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                
                # Reset the engine to force a new connection pool on next attempt
                global _engine
                _engine = None
            else:
                logger.error(f"Failed to establish database connection after {max_retries} attempts: {str(e)}")
                raise
