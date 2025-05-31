from flask import Flask, jsonify, render_template, session
from flask_session import Session
from flask_cors import CORS
from flask_sock import Sock

from .config import Config
from .auth import auth_bp
from .routes.users import users_bp
from .routes.expenses import expenses_bp
from .routes.budgets import budgets_bp
from .websockets import sock

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "../frontend")

app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.config.from_object(Config)
# Allow CORS for Vercel and Azure domains
CORS(app, resources={
    r"/api/*": {"origins": ["https://*.vercel.app", "https://*.azurestaticapps.net", "http://localhost:5173"]},
    r"/ws": {"origins": ["https://*.vercel.app", "https://*.azurestaticapps.net", "http://localhost:5173"]}
}, supports_credentials=True)

app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True
Session(app)

app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(users_bp, url_prefix="/api")
app.register_blueprint(expenses_bp, url_prefix="/api")
app.register_blueprint(budgets_bp, url_prefix="/api")

sock.init_app(app)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Expense Tracker Backend API"}), 200

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)