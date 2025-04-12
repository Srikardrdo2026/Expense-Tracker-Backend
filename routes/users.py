from flask import Blueprint, request, jsonify
from database import users_collection
from bson.objectid import ObjectId

users_bp = Blueprint("users", __name__)

@users_bp.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    user["_id"] = str(user["_id"])  # Convert ObjectId to string
    return jsonify(user)

@users_bp.route("/users", methods=["GET"])
def get_all_users():
    users = list(users_collection.find({}))
    for user in users:
        user["_id"] = str(user["_id"])
    return jsonify(users)
