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
CORS(app)

@app.route("/api/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return cors_preflight()
    
    data = request.json
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")

    if not email or not password or not username:
        return jsonify({"error": "Missing fields"}), 400

    try:
        response = supabase.auth.sign_up({"email": email, "password": password, "options": { "data": {"display_name": username}}})

        if not response or not hasattr(response, "session") or not response.session:
            return jsonify({"error": "Invalid email or password"}), 400

        return jsonify({"message": "Sign up successful", "token": response.session.access_token}), 201
    
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": f"Sign up error: {(str(e))}"}), 400


@app.route("/api/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return cors_preflight()
    
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})

        if not response or not hasattr(response, "session") or not response.session:
            return jsonify({"error": "Invalid email or password"}), 400

        return jsonify({"message": "Login successful", "token": response.session.access_token}), 200

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": f"Login error: {(str(e))}"}), 400


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

def cors_preflight():
    response = jsonify({"message": "CORS preflight success"})
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    return response

if __name__ == "__main__":
    app.run(debug=True)