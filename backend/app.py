from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPA_URL")
key: str = os.environ.get("SUPA_KEY")
supabase: Client = create_client(url, key)

app = Flask(__name__)

@app.route("/api/register", methods=["POST", "OPTIONS"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")

    if not email or not password or not username:
        return jsonify({"error": "Missing fields"}), 400

    response = supabase.auth.sign_up({"email": email, "password": password})
    if "error" in response:
        return jsonify(response["error"]), 400

    user_id = response.user.id
    supabase.table("users").insert({"id": user_id, "username": username}).execute()

    return jsonify({"message": "User registered"}), 201

@app.route("/api/login", methods=["POST", "OPTIONS"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    response = supabase.auth.sign_in_with_password({"email": email, "password": password})

    if "error" in response:
        return jsonify(response["error"]), 400

    return jsonify({"message": "Login successful"}), 200

@app.route("/api/browse", methods=["GET"])
def browse():
    rooms = supabase.table("room").select("*").execute()
    return jsonify(rooms.data)

@app.route("/api/rooms/create", methods=["POST"])
def create_room():
    data = request.json
    room_name = data.get("name")
    room_desc = data.get("description", "")

    if not room_name:
        return jsonify({"error": "Room name is required"}), 400

    res = supabase.table("room").insert({"name": room_name, "description": room_desc}).execute()
    return jsonify(res.data), 201

@app.route("/api/rooms/<room_id>", methods=["GET"])
def get_room_info(room_id):
    res = supabase.table("room").select("*").eq("id", room_id).execute()
    if not res:
        return jsonify({"error": "Room doesn't exist"}), 404
    return jsonify(res.data[0])

if __name__ == "__main__":
    app.run(debug=True)