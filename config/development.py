import os
from config.base import Config


class DevelopmentConfig(Config):
    """Configuration for development environment."""
    
    # Enable debug mode
    DEBUG = True
    
    # Database path (development-specific)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///data/development.db')
    
    # Additional development settings
    FLASK_ENV = 'development'
    
    # Initialize development-specific configuration
    @classmethod
    def initialize(cls):
        """Initialize development-specific configuration."""
        super().initialize()
        
        # Log configuration
        import logging
        logging.basicConfig(level=logging.DEBUG)
        logging.info("Development configuration initialized")
