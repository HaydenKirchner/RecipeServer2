import logging
from app import create_app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the application instance
app = create_app()

if __name__ == "__main__":
    logger.info("Starting the Recipe Planner application")
    app.run(host="0.0.0.0", port=5001, debug=True)
