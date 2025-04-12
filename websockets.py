from flask import Flask
from flask_sock import Sock  # Import Flask-Sock
import json
from database import expenses_collection  # MongoDB connection
from datetime import datetime

app = Flask(__name__)
sock = Sock()

def serialize_expense(expense):
    """Convert MongoDB expense document to JSON serializable format."""
    expense["date"] = expense["date"].isoformat() if isinstance(expense["date"], datetime) else expense["date"]
    return expense


@sock.route("/ws")  # WebSocket route
def websocket_handler(ws):
    print("Client connected to WebSocket")

    while True:
        data = ws.receive()
        if not data:
            break  # Stop when client disconnects

        message = json.loads(data)
        print(f"📩 Received message: {message}")
        if message.get("event") == "fetch_expenses":
            user_id = message.get("user_id")
            expenses = list(expenses_collection.find({"user_id": user_id}, {"_id": 0}))
            expenses_serialized = [serialize_expense(exp) for exp in expenses]
            response = {"event": "expense_update", "expenses": expenses_serialized}
            ws.send(json.dumps(response))
            print(f"📤 Sent expense update: {response}")  # Debugging output
        
        elif message.get("event") == "new_expense":
            print(f"New expense added: {message}")
            ws.send(json.dumps({"event": "expense_update", "message": "New expense added", "data": message}))

    print("Client disconnected")
