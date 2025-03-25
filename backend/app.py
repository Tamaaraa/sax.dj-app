from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime 
import requests

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    socketio = SocketIO(app, cors_allowed_origins="http://localhost:5173")

    url: str = os.environ.get("SUPA_URL")
    key: str = os.environ.get("SUPA_KEY")
    supabase: Client = create_client(url, key)

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
            if not response or not response.session:
                return jsonify({"error": "Invalid email or password"}), 400
            
            supabase.table("users").insert([{ "id": response.user.id, "username": username }]).execute()
            return jsonify({"message": "Sign up successful", "token": response.session.access_token, "username": response.user.user_metadata["display_name"]}), 201
        
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

            if not response or not response.session:
                return jsonify({"error": "Invalid email or password"}), 400

            return jsonify({"message": "Login successful", "token": response.session.access_token, "username": response.user.user_metadata["display_name"]}), 200

        except Exception as e:
            print(f"Login error: {e}")
            return jsonify({"error": f"Login error: {(str(e))}"}), 400

    @app.route("/api/browse", methods=["GET"])
    def browse():
        error = verify_token()
        if error:
            return error
        rooms = supabase.table("room").select("*").order("created_at", desc=False).execute()
        return jsonify(rooms.data)

    @app.route("/api/rooms/create", methods=["POST"])
    def create_room():
        error = verify_token()
        if error:
            return error
        
        data = request.json
        room_name = data.get("name")
        room_desc = data.get("description", "")

        if not room_name:
            return jsonify({"error": "Room name is required"}), 400

        res = supabase.table("room").insert({"name": room_name, "description": room_desc}).execute()
        return jsonify(res.data), 201

    @app.route("/api/rooms/<room_id>", methods=["GET"])
    def get_room_info(room_id):
        error = verify_token()
        if error:
            return error
        
        res = supabase.table("room").select("*").eq("id", room_id).execute()
        if not res:
            return jsonify({"error": "Room doesn't exist"}), 404
        return jsonify(res.data[0])

    @app.route("/api/rooms/<room_id>/messages", methods=["GET"])
    def get_room_messages(room_id):
        messages = (
            supabase.table("messages")
            .select("id, sender_id, content, created_at")
            .eq("room_id", room_id)
            .order("created_at", desc=False)
            .execute()
        )

        sender_ids = {msg["sender_id"] for msg in messages.data}
        users = (
            supabase.table("users")
            .select("id, username")
            .in_("id", list(sender_ids))
            .execute()
        )

        user_dic = {user["id"]: user["username"] for user in users.data}

        for message in messages.data:
            message["username"] = user_dic.get(message["sender_id"], "Unknown User")

        return jsonify(messages.data)

    @app.route("/api/rooms/<room_id>/queue", methods=["GET"])
    def get_video_queue(room_id):
        queue = (
            supabase.table("video_queue")
            .select("*")
            .eq("room_id", room_id)
            .order("position", desc=False)
            .execute()
        )
        return jsonify(queue.data)

    @app.route("/api/rooms/<room_id>/queue", methods=["POST"])
    def add_video_to_queue(room_id):
        error = verify_token()
        if error:
            return error

        data = request.json
        video_url = data.get("video_url")
        if not video_url:
            return jsonify({"error": "Video URL is required"}), 400

        if video_url.startswith("https://www.youtube.com/watch?v="):
            video_id = video_url.split('=')[1]
            video_url = f"https://www.youtube.com/embed/{video_id}"
        elif video_url.startswith("https://youtu.be/"):
            video_id = video_url.split('/')[3]
            video_url = f"https://www.youtube.com/embed/{video_id}"
        elif video_url.startswith("https://www.youtube.com/embed/"):
            video_id = video_url.split('/')[-1]
        else:
            return jsonify({"error": "Invalid video URL"}), 400

        video_url += "?autoplay=1&showinfo=0&controls=0"

        try:
            response = requests.get(f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json")
            response.raise_for_status()
            video_title = response.json().get("title", "Unknown Title")
            video_thumbnail= response.json().get("thumbnail_url", "https://cdn-icons-png.freepik.com/512/683/683935.png")
        except Exception as e:
            print(f"Error fetching video title: {e}")
            video_title = "Unknown Title"

        max_position = (
            supabase.table("video_queue")
            .select("position")
            .eq("room_id", room_id)
            .order("position", desc=True)
            .limit(1)
            .execute()
        )
        next_position = (max_position.data[0]["position"] + 1) if max_position.data else 1

        supabase.table("video_queue").insert({
            "room_id": room_id,
            "video_url": video_url,
            "video_title": video_title,
            "position": next_position,
            "requester": data.get("requester"),
            "video_thumbnail": video_thumbnail,
        }).execute()

        return jsonify({"message": "Video added to queue"}), 201

    @app.route("/api/rooms/<room_id>/queue", methods=["DELETE"])
    def remove_video_from_queue(room_id):
        error = verify_token()
        if error:
            return error

        data = request.json
        video_id = data.get("video_id")
        if not video_id:
            return jsonify({"error": "Video ID required"}), 400

        supabase.table("video_queue").delete().eq("id", video_id).execute()
        return jsonify({"message": "Video removed from queue"}), 200

    @app.route("/api/verify-token", methods=["GET", "OPTIONS"])
    def verify():
        if request.method == "OPTIONS":
            return cors_preflight()

        error = verify_token()
        if error:
            return error

        return jsonify({"message": "Token is valid"}), 200

    def cors_preflight():
        response = jsonify({"message": "CORS preflight success"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        return response

    def verify_token(token=None, return_user=False):
        if not token:
            token = request.headers.get("Authorization")
            
            if not token:
                return jsonify({"error": "Unauthorized"}), 401

            token = token.split(" ")[1]

        try:
            user = supabase.auth.get_user(token)
            if not user:
                return jsonify({"error": "Invalid token"}), 401

            if return_user:
                return user.user

        except Exception as e:
            if "expired" in str(e).lower():
                return jsonify({"error": "Token expired", "logout": True}), 401
            return jsonify({"error": "Invalid token"}), 401

        return None

    @socketio.on("join")
    def handle_join(data):
        room_id = data["room_id"]
        join_room(room_id)

    @socketio.on("message")
    def handle_message(data): 
        token = data["token"]
        user = verify_token(token, return_user=True)

        if not user:
            return

        sender_id = user.id
        room_id = data["room_id"]
        content = data["content"]
        username = data["username"]

        supabase.table("messages").insert({
            "room_id": room_id,
            "sender_id": sender_id,
            "content": content,
            "created_at": datetime.now().isoformat()
        }).execute()

        emit("message", {
            "sender_id": sender_id,
            "username": username,
            "content": content,
            "created_at": datetime.now().isoformat()
        }, room=room_id)

    @socketio.on("leave")
    def handle_leave(data):
        room_id = data["room_id"]
        leave_room(room_id)

    @socketio.on("play_next_video")
    def handle_play_next_video(data):
        room_id = data["room_id"]

        next_video = (
            supabase.table("video_queue")
            .select("*")
            .eq("room_id", room_id)
            .order("position", desc=False)
            .limit(1)
            .execute()
        )

        if next_video.data:
            video = next_video.data[0]
            supabase.table("room").update({"room_thumbnail": video["video_thumbnail"]}).eq("id", room_id).execute()
            emit("play_video", {"video_url": video["video_url"]}, room=room_id)

            supabase.table("video_queue").delete().eq("id", video["id"]).execute()

    return app, socketio

if __name__ == "__main__":
    app, socketio = create_app()
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)