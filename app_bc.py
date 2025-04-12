from flask import Flask, jsonify, render_template
from flask_cors import CORS
from config import Config
from auth import auth_bp
from routes.users import users_bp
from routes.expenses import expenses_bp
from routes.budgets import budgets_bp
from websockets import sock  # Import WebSocket instance
import os

# 🔥 Set correct template folder path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Get backend directory
TEMPLATE_DIR = os.path.join(BASE_DIR, "../frontend/templates")  # Move to frontend/templates

app = Flask(__name__, template_folder=TEMPLATE_DIR)  
app.config.from_object(Config)
CORS(app)

# Register API routes
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(users_bp, url_prefix="/api")
app.register_blueprint(expenses_bp, url_prefix="/api")
app.register_blueprint(budgets_bp, url_prefix="/api")

# Register WebSocket separately
sock.init_app(app)

# ✅ **Fix: Add a home route**
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Expense Tracker Backend API"}), 200

# ✅ **Fix: Change Health Check Route to Avoid Conflict**
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
