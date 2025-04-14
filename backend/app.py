import os
from datetime import datetime
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from supabase import Client, create_client


def create_app(app=None, env=None):
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {
        "origins": [os.environ.get("FRONT_END_URL"), "http://localhost:5173"]
        }})
    socketio = SocketIO(app,
                        cors_allowed_origins=[
                            os.environ.get("FRONT_END_URL"),
                            "http://localhost:5173"])

    url: str = os.environ.get("SUPA_URL")
    key: str = os.environ.get("SUPA_KEY")
    supabase: Client = create_client(url, key)

    initialize_users(supabase)

    @app.route("/api/register", methods=["POST"])
    def register():
        data = request.json
        email = data.get("email")
        password = data.get("password")
        username = data.get("username")

        if not email or not password or not username:
            return jsonify({"error": "Missing fields"}), 400

        try:
            response = supabase.auth.sign_up({"email": email,
                                              "password": password,
                                              "options": {"data": {
                                                  "display_name": username
                                                  }}})
            if not response or not response.session:
                return jsonify({"error": "Invalid email or password"}), 400

            supabase.table("users").insert([{"user_id": response.user.id,
                                             "display_name": username}]
                                           ).execute()
            return jsonify({
                "message": "Sign up successful",
                "token": response.session.access_token,
                "username": response.user.user_metadata["display_name"],
                "user_id": response.user.id
                }), 201

        except Exception as e:
            print(f"Login error: {e}")
            return jsonify({"error": f"Sign up error: {(str(e))}"}), 400

    @app.route("/api/login", methods=["POST"])
    def login():
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Missing fields"}), 400

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not response or not response.session:
                return jsonify({"error": "Invalid email or password"}), 400

            return jsonify({
                "message": "Login successful",
                "token": response.session.access_token,
                "username": response.user.user_metadata["display_name"]
            }), 200

        except Exception as e:
            return jsonify({"error": f"Login error: {(str(e))}"}), 400

    @app.route("/api/browse", methods=["GET"])
    def browse():
        error = verify_token()
        if error:
            return error
        rooms = supabase.table("room").select("*").order("created_at",
                                                         desc=False).execute()
        return jsonify(rooms.data)

    @app.route("/api/rooms/create", methods=["POST"])
    def create_room():
        user = verify_token(return_user=True)
        if not user:
            return jsonify({"error": "Invalid token"}), 401

        data = request.json
        creator_id = user.id
        room_name = data.get("name")
        room_desc = data.get("description", "")

        if not room_name:
            return jsonify({"error": "Room name is required"}), 400

        res = supabase.table("room").insert({
            "name": room_name,
            "description": room_desc,
            "room_creator": creator_id
            }).execute()
        return jsonify(res.data), 201

    @app.route("/api/rooms/<room_id>", methods=["GET"])
    def get_room_info(room_id):
        user = verify_token(return_user=True)
        if not user:
            return jsonify({"error": "Invalid token"}), 401

        res = supabase.table("room").select("*").eq("id", room_id).execute()
        if not res:
            return jsonify({"error": "Room doesn't exist"}), 404

        res.data[0]["user_id"] = user.id

        return jsonify(res.data[0]), 200

    @app.route("/api/rooms/<room_id>/messages", methods=["GET"])
    def get_room_messages(room_id):
        messages = (
            supabase.table("messages")
            .select("id, sender_id, content, created_at")
            .eq("room_id", room_id)
            .order("created_at", desc=False)
            .execute()
        )

        sender_ids = {
            msg["sender_id"] for msg in messages.data
        }
        users = (
            supabase.table("users")
            .select("user_id, display_name")
            .in_("user_id", list(sender_ids))
            .execute()
        )

        user_dic = {
            user["user_id"]: user["display_name"] for user in users.data
        }

        for message in messages.data:
            message["display_name"] = user_dic.get(message["sender_id"],
                                                   "Unknown User")

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

        video_json = f"https://www.youtube.com/watch?v={video_id}"

        try:
            response = requests.get(
                f"https://www.youtube.com/oembed?url={video_json}&format=json")
            response.raise_for_status()
            video_title = response.json().get("title", "Unknown Title")
            video_thumbnail = response.json().get(
                "thumbnail_url",
                "https://cdn-icons-png.freepik.com/512/683/683935.png"
            )
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
        next_position = (
            max_position.data[0]["position"] + 1
            ) if max_position.data else 1

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

    @app.route("/api/rooms/<room_id>/delete", methods=["DELETE"])
    def delete_room(room_id):
        error = verify_token()
        if error:
            return error

        supabase.table("room").delete().eq("id", room_id).execute()
        return jsonify({"message": "Room deleted"}), 200

    @app.route("/api/verify-token", methods=["GET"])
    def verify():
        error = verify_token()
        if error:
            return error

        return jsonify({"message": "Token is valid"}), 200

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
        display_name = user.user_metadata["display_name"]

        supabase.table("messages").insert({
            "room_id": room_id,
            "sender_id": sender_id,
            "content": content,
            "created_at": datetime.now().isoformat()
        }).execute()

        emit("message", {
            "sender_id": sender_id,
            "display_name": display_name,
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
            supabase.table("room").update({
                "room_thumbnail": video["video_thumbnail"]
                }).eq("id", room_id).execute()
            emit("play_video", {"video_url": video["video_url"]}, room=room_id)

            supabase.table("video_queue").delete().eq(
                "id", video["id"]
            ).execute()

    return app, socketio


def initialize_users(supabase):
    """Creates 2 testing accounts if they don't exist."""
    users = [
        {"email": "testing1@gmail.com",
         "password": os.environ.get("TEST_ACC_1_PASS"),
         "username": "Testing1"},
        {"email": "testing2@gmail.com",
         "password": os.environ.get("TEST_ACC_2_PASS"),
         "username": "Testing2"}
    ]

    for user in users:
        try:
            existing_user = supabase.table("users").select("*").eq(
                "display_name",
                user["username"]
                ).execute()
            if not existing_user.data:
                response = supabase.auth.sign_up({
                    "email": user["email"],
                    "password": user["password"],
                    "options": {"data": {"display_name": user["username"]}}
                })
                if response and response.user:
                    supabase.table("users").insert([{
                        "user_id": response.user.id,
                        "display_name": user["username"]
                    }]).execute()
        except Exception as e:
            print(f"Error initializing user {user['email']}: {e}")


if __name__ == "__main__":
    load_dotenv()
    app, socketio = create_app()
    debug = os.environ.get("DEBUG_MODE")
    if debug == "True":
        socketio.run(app,
                     host="0.0.0.0",
                     port=5000,
                     debug=True)
    else:
        socketio.run(app,
                     host="0.0.0.0",
                     port=5000,
                     debug=False,
                     allow_unsafe_werkzeug=True)
