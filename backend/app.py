import os
from datetime import datetime
import requests
from dotenv import load_dotenv
from flask import Flask, json, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from supabase import Client, create_client
import redis
import yt_dlp
import time
import uuid


def create_app(app=None, env=None):
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {
        "origins": [os.environ.get("FRONT_END_URL"), "http://localhost:5173"]
        }})
    socketio = SocketIO(app,
                        cors_allowed_origins=[
                            os.environ.get("FRONT_END_URL"),
                            "http://localhost:5173"])

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
        r_queue = f"room:{room_id}:queue"
        queue = redis_client.lrange(r_queue, 0, -1)
        return [json.loads(item) for item in queue]

    @app.route("/api/rooms/<room_id>/queue", methods=["POST"])
    def add_video_to_queue(room_id):
        error = verify_token()
        if error:
            return error

        data = request.json
        video_url = data.get("video_url")
        if not video_url:
            return jsonify({"error": "Video URL is required"}), 400

        video_data = get_video_data(video_url)
        video_data["requester"] = data.get("requester")
        video_data["id"] = str(uuid.uuid4())

        r_queue = f"room:{room_id}:queue"
        r_current = f"room:{room_id}:current_video"

        redis_client.rpush(r_queue, json.dumps(video_data))
        if not redis_client.exists(r_current):
            play_next_video(room_id)

        return jsonify({"message": "Video added to queue"}), 201

    @app.route("/api/rooms/<room_id>/queue", methods=["DELETE"])
    def remove_video_from_queue(room_id):
        error = verify_token()
        if error:
            return error

        data = request.json

        r_queue = f"room:{room_id}:queue"
        queue = redis_client.lrange(r_queue, 0, -1)

        for item in queue:
            item_data = json.loads(item)
            video_id = data.get("video_id")
            if item_data.get("id") == video_id:
                redis_client.lrem(r_queue, 1, item)
                break

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
        pass

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


def get_video_data(video_url):
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

    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_duration = info.get('duration')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return {"video_url": video_url,
            "title": video_title,
            "thumbnail": video_thumbnail,
            "duration": video_duration}


def play_next_video(room_id):
    r_queue = f"room:{room_id}:queue"
    r_current = f"room:{room_id}:current_video"
    r_start_time = f"room:{room_id}:current_start_time"

    next = redis_client.lpop(r_queue)
    if next:
        video = json.loads(next)

        redis_client.hset(r_current, mapping=video)
        redis_client.set(r_start_time, int(time.time()))

        supabase.table("room").update({
            "room_thumbnail": video["thumbnail"]
            }).eq("id", room_id).execute()

    else:
        redis_client.delete(r_current, r_start_time)


def check_room_video(room_id):
    r_start = f"room:{room_id}:current_start_time"
    r_current = f"room:{room_id}:current_video"

    if not redis_client.exists(r_current):
        return

    start_time = int(redis_client.get(r_start))
    video = redis_client.hgetall(r_current)
    duration = int(video.get("duration", 0))

    if time.time() - start_time >= duration:
        play_next_video(room_id)


if __name__ == "__main__":
    load_dotenv()

    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=6379,
        decode_responses=True
    )

    url: str = os.environ.get("SUPA_URL")
    key: str = os.environ.get("SUPA_KEY")
    supabase: Client = create_client(url, key)

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
