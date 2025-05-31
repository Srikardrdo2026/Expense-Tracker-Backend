# backend/database.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_CLUSTER = os.getenv("MONGO_CLUSTER")
MONGO_DB = os.getenv("MONGO_DB", "expense_tracker")

# Build Atlas connection string
MONGO_URI = (
    f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/{MONGO_DB}"
    "?retryWrites=true&w=majority&tls=true"
)

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI, tls=True)
db = client[MONGO_DB]

# Collections
users_collection    = db["users"]
expenses_collection = db["expenses"]
budgets_collection  = db["budgets"]
