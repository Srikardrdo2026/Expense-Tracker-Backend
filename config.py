import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/expense_tracker")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600))  # Default 1 hour

    # WebSockets Configuration
    WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", 5001))  # Default WebSocket port 5001

    # Flask-CORS (Optional: If you use CORS)
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")  # Allow all origins by default
