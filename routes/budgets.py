from flask import Blueprint, request, jsonify, current_app
from database import budgets_collection, expenses_collection
from auth import decode_jwt, AuthError
from bson.objectid import ObjectId
from pymongo.errors import OperationFailure
from datetime import datetime, timezone

BEARER_PREFIX = "Bearer "

budgets_bp = Blueprint("budgets", __name__)

@budgets_bp.route("/budgets", methods=["POST"])
def create_or_update_budget():
    try:
        token = request.headers.get("Authorization").split(BEARER_PREFIX)[1]
        payload = decode_jwt(token)
        user_email = payload["email"]
    except (AuthError, IndexError, AttributeError) as e:
        return jsonify({"message": "Unauthorized", "status": "error"}), 401

    data = request.get_json()
    
    required_fields = ["amount"]
    if not data or any(field not in data for field in required_fields):
        return jsonify({"error": f"Missing required field: {', '.join(required_fields)}"}), 400

    try:
        amount = float(data["amount"])
        if amount <= 0:
            return jsonify({"error": "Amount must be greater than zero"}), 400
    except ValueError:
        return jsonify({"error": "Invalid amount format"}), 400

    try:
        existing_budget = budgets_collection.find_one({"email": user_email})

        current_timestamp = datetime.now(timezone.utc)
        budget_data = {
            "email": user_email,
            "amount": amount,
            "updated_at": current_timestamp
        }

        if existing_budget:
            result = budgets_collection.update_one(
                {"email": user_email},
                {"$set": budget_data},
                upsert=False
            )
            if result.modified_count > 0:
                return jsonify({"message": "Budget updated successfully", "amount": amount}), 200
            else:
                return jsonify({"error": "Failed to update budget"}), 500
        else:
            budget_data["created_at"] = current_timestamp
            budget_data["is_active"] = True
            inserted_budget = budgets_collection.insert_one(budget_data)
            return jsonify({
                "message": "Budget created successfully",
                "budget_id": str(inserted_budget.inserted_id),
                "amount": amount
            }), 201

    except OperationFailure as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@budgets_bp.route("/budgets/<email>", methods=["GET"])
def get_budget(email):
    try:
        token = request.headers.get("Authorization").split(BEARER_PREFIX)[1]
        payload = decode_jwt(token)
        if payload["email"] != email:
            return jsonify({"message": "Unauthorized", "status": "error"}), 401
    except (AuthError, IndexError, AttributeError) as e:
        return jsonify({"message": "Unauthorized", "status": "error"}), 401

    try:
        budget = budgets_collection.find_one({"email": email, "is_active": True})
        
        if not budget:
            return jsonify({"message": "No budget found", "budget": None}), 200

        total_expenses = expenses_collection.aggregate([
            {"$match": {"user_id": email}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ])
        total_expenses = next(total_expenses, {"total": 0})["total"]

        budget["_id"] = str(budget["_id"])
        budget["created_at"] = budget["created_at"].isoformat() if "created_at" in budget else None
        budget["updated_at"] = budget["updated_at"].isoformat()
        
        return jsonify({
            "message": "Budget retrieved successfully",
            "budget": {
                "_id": budget["_id"],
                "email": budget["email"],
                "amount": budget["amount"],
                "total_expenses": total_expenses,
                "remaining": budget["amount"] - total_expenses,
                "created_at": budget["created_at"],
                "updated_at": budget["updated_at"],
                "is_active": budget["is_active"]
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error retrieving budget: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@budgets_bp.route("/budgets/<budget_id>", methods=["DELETE"])
def delete_budget(budget_id):
    try:
        token = request.headers.get("Authorization").split("Bearer ")[1]
        payload = decode_jwt(token)
        user_email = payload["email"]
    except (AuthError, IndexError, AttributeError) as e:
        return jsonify({"message": "Unauthorized", "status": "error"}), 401

    try:
        result = budgets_collection.update_one(
            {"_id": ObjectId(budget_id), "email": user_email},
            {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}}
        )

        if result.modified_count > 0:
            return jsonify({"message": "Budget deleted successfully"}), 200
        return jsonify({"error": "Budget not found or unauthorized"}), 404

    except OperationFailure as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
