import os
from config.base import Config


class ProductionConfig(Config):
    """Configuration for production environment."""
    
    # Database path (use environment variable)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///data/production.db')
    
    # Production settings
    FLASK_ENV = 'production'
    
    # Set a secure secret key for production
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24))
    
    # Additional production settings
    PREFERRED_URL_SCHEME = 'https'
    
    # Initialize production-specific configuration
    @classmethod
    def initialize(cls):
        """Initialize production-specific configuration."""
        super().initialize()
        
        # Log configuration
        import logging
        logging.basicConfig(level=logging.WARNING)
        
        # Ensure all required directories exist
        os.makedirs(os.path.join(os.getcwd(), 'data'), exist_ok=True)
