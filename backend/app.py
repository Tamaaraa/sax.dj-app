from flask import Flask, request, redirect, url_for, render_template, jsonify
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

@app.route("/")
def hello_world():
    # TODO: Login page
    return redirect(url_for("browse"))

@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@app.route("/browse")
def browse():
    rooms = supabase.table("room").select("*").execute()
    return jsonify(rooms.data)

@app.route("/rooms", methods=["POST"])
def create_room():
    data = request.json
    room_name = data.get("name")
    room_desc = data.get("description", "")

    if not room_name:
        return jsonify({"error": "Room name is required"}), 400

    res = supabase.table("room").insert({"name": room_name, "description": room_desc}).execute()
    return jsonify(res.data), 201

@app.route("/rooms/<room_id>", methods=["GET"])
def get_room_info(room_id):
    res = supabase.table("room").select("*").eq("id", room_id).execute()
    print(res)
    if not res:
        return jsonify({"error": "Room doesn't exist"}), 404
    return jsonify(res.data[0])

if __name__ == "__main__":
    app.run(debug=True)