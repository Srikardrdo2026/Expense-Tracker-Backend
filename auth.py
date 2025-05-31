import jwt
import os
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta
from database import users_collection

auth_bp = Blueprint("auth", __name__)

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")

class AuthError(Exception):
    """Custom exception class for authentication errors."""
    def __init__(self, message, status_code=401):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

@auth_bp.route("/signup", methods=["POST"])
def register():
    data = request.get_json()
    
    if users_collection.find_one({"email": data["email"]}):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(data["password"])
    user = {
        "username": data["username"],
        "email": data["email"],
        "password": hashed_password,
    }
    users_collection.insert_one(user)
    
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = users_collection.find_one({"email": data["email"]})

    if not user or not check_password_hash(user["password"], data["password"]):
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    # Generate JWT
    token = jwt.encode(
        {"user_id": str(user["_id"]), "email": user["email"], "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        SECRET_KEY,
        algorithm="HS256",
    )
    return jsonify({
        "status": "success",
        "message": "Login successful!",
        "token": token,
        "email": user["email"],
        "redirect": "/dashboard"
    })

def decode_jwt(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired", 401)
    except jwt.InvalidTokenError:
        raise AuthError("Invalid token", 403)
