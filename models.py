from bson import ObjectId
from datetime import datetime, timezone

class UserModel:
    def __init__(self, username, email, password, id=None):
        self.id = ObjectId(id) if id else ObjectId()
        self.username = username
        self.email = email
        self.password = password

    def to_dict(self):
        return {
            "_id": str(self.id),
            "username": self.username,
            "email": self.email,
            "password": self.password,
        }

class ExpenseModel:
    def __init__(self, user_id, category, amount, description=None, date=None, id=None):
        self.id = ObjectId(id) if id else ObjectId()
        self.user_id = user_id
        self.category = category
        self.amount = amount
        self.description = description
        self.date = date or datetime.now(timezone.utc)

    def to_dict(self):
        return {
            "_id": str(self.id),
            "user_id": self.user_id,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
            "date": self.date,
        }

class BudgetModel:
    def __init__(self, user_id, amount, id=None):
        self.id = ObjectId(id) if id else ObjectId()
        self.user_id = user_id
        self.amount = amount

    def to_dict(self):
        return {
            "_id": str(self.id),
            "user_id": self.user_id,
            "amount": self.amount
        }