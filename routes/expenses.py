from flask import Blueprint, request, jsonify, session
from database import expenses_collection, budgets_collection
from bson.objectid import ObjectId
from pymongo.errors import OperationFailure
from datetime import datetime

expenses_bp = Blueprint("expenses", __name__)

@expenses_bp.route("/expenses", methods=["POST"])
def add_expense():
    if 'user' not in session:
        return jsonify({"message": "Unauthorized", "status": "error"}), 401

    data = request.get_json()
    
    required_fields = ["amount"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": f"Missing required field: {', '.join(required_fields)}"}), 400

    try:
        amount = float(data["amount"])
        if amount <= 0:
            return jsonify({"error": "Amount must be greater than zero"}), 400
    except ValueError:
        return jsonify({"error": "Invalid amount format"}), 400

    user_email = session["user"]
    description = data.get("description", "")

    # Check if budget exists and has sufficient funds
    budget = budgets_collection.find_one({"email": user_email, "is_active": True})
    if not budget:
        return jsonify({"error": "No active budget found"}), 400

    total_expenses = expenses_collection.aggregate([
        {"$match": {"user_id": user_email}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ])
    total_expenses = next(total_expenses, {"total": 0})["total"]

    if (total_expenses + amount) > budget["amount"]:
        return jsonify({"error": "Expense exceeds remaining budget"}), 400

    try:
        expense_data = {
            "user_id": user_email,
            "amount": amount,
            "description": description,
            "created_at": datetime.timezone.utc()
        }
        inserted_expense = expenses_collection.insert_one(expense_data)
        
        return jsonify({
            "message": "Expense added successfully",
            "expense_id": str(inserted_expense.inserted_id),
            "amount": amount,
            "description": description
        }), 201

    except OperationFailure as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@expenses_bp.route("/expenses/<email>", methods=["GET"])
def get_expenses(email):
    if 'user' not in session or session["user"] != email:
        return jsonify({"message": "Unauthorized", "status": "error"}), 401

    try:
        expenses = expenses_collection.find({"user_id": email}).sort("created_at", -1)
        expense_list = []

        for expense in expenses:
            expense["_id"] = str(expense["_id"])
            expense["created_at"] = expense["created_at"].isoformat()
            expense_list.append(expense)

        return jsonify({
            "message": "Expenses retrieved successfully",
            "expenses": expense_list,
            "count": len(expense_list)
        }), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@expenses_bp.route("/expenses/<expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    if 'user' not in session:
        return jsonify({"message": "Unauthorized", "status": "error"}), 401

    try:
        result = expenses_collection.delete_one({
            "_id": ObjectId(expense_id),
            "user_id": session["user"]
        })

        if result.deleted_count > 0:
            return jsonify({"message": "Expense deleted successfully"}), 200
        return jsonify({"error": "Expense not found or unauthorized"}), 404

    except OperationFailure as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500