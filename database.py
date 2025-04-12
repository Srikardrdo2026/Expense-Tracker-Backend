from pymongo import MongoClient
import os

# Load MongoDB credentials from environment variables
MONGO_USER = os.getenv("MONGO_USER", "Srikar")  # Default user
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "One_Piece")  # Default password
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB = os.getenv("MONGO_DB", "expense_tracker")

# Construct MongoDB URI with authentication
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"

# Establish MongoDB connection
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# Collections
users_collection = db["users"]
expenses_collection = db["expenses"]
budgets_collection = db["budgets"]
