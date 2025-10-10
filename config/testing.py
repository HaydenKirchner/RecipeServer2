import os
from config.base import Config


class TestingConfig(Config):
    """Configuration for testing environment."""
    
    # Enable testing mode
    TESTING = True
    
    # Database path (in-memory SQLite for testing)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///data/testing.db')
    
    # Additional testing settings
    FLASK_ENV = 'testing'
    
    # Disable CSRF protection for testing
    WTF_CSRF_ENABLED = False
    
    # Initialize testing-specific configuration
    @classmethod
    def initialize(cls):
        """Initialize testing-specific configuration."""
        super().initialize()
        
        # Log configuration
        import logging
        logging.basicConfig(level=logging.INFO)
        logging.info("Testing configuration initialized")
