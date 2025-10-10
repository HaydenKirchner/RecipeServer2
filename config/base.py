import os


class Config:
    """Base configuration for the application."""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key_for_development')
    
    # Database settings (default to SQLite)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///data/recipes.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # PDF generation settings
    PDF_OUTPUT_DIR = os.path.join(os.getcwd(), 'static', 'pdfs')
    
    # Debug settings
    DEBUG = False
    TESTING = False
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
    
    # Ensure directories exist
    @classmethod
    def initialize(cls):
        """Initialize configuration by ensuring directories exist."""
        # Ensure PDF output directory exists
        os.makedirs(cls.PDF_OUTPUT_DIR, exist_ok=True)
        
        # Ensure other static directories exist
        for dir_name in ['css', 'js', 'images']:
            os.makedirs(os.path.join(cls.STATIC_DIR, dir_name), exist_ok=True)
