from pymongo import MongoClient
from config import Config
import os

# Establish MongoDB connection
client = MongoClient(Config.MONGO_URI)
db = client[MONGO_DB]

# Collections
users_collection = db["users"]
expenses_collection = db["expenses"]
budgets_collection = db["budgets"]
