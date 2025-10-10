from config.base import Config
from config.development import DevelopmentConfig
from config.testing import TestingConfig
from config.production import ProductionConfig

# Map of environment names to configuration classes
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
