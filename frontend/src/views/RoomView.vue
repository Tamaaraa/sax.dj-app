<template>
  <div class="room-container">
    <div class="room-top-bar">
      <button @click="$router.push('/browse')" class="back-button">
        ← Back
      </button>
      <h1 class="room-name">{{ room_data.name }}</h1>
      <button
        v-if="room_data.room_creator == room_data.user_id"
        @click="removeRoom()"
        class="remove-button"
      >
        Remove room
      </button>
    </div>

    <div class="content">
      <div class="video-container">
        <VideoPlayer v-if="socket" :socket="socket" />
      </div>
      <div class="chat-container">
        <div class="chat-messages">
          <div
            v-for="(message, index) in messages"
            :key="index"
            class="chat-message"
          >
            <strong>{{ message.display_name }}:</strong> {{ message.content }}
          </div>
        </div>

        <!-- Chat Input -->
        <div class="chat-input">
          <input
            v-model="newMessage"
            placeholder="Type a message..."
            @keyup.enter="sendMessage"
          />
          <button @click="sendMessage">Send</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { io } from "socket.io-client";
import VideoPlayer from "@/components/VideoPlayer.vue";

export default {
  components: {
    VideoPlayer,
  },
  data() {
    return {
      room_data: {},
      room_id: null,
      messages: [],
      newMessage: "",
      socket: null,
    };
  },
  mounted() {
    const token = localStorage.getItem("token");
    const room_id = this.$route.params.room_id;
    this.room_id = room_id;

    if (!token) {
      console.error("No token found, redirecting to login...");
      this.$router.push("/login");
      return;
    }

    // Fetch room details
    axios
      .get(`${import.meta.env.VITE_API_URL}/api/rooms/${this.room_id}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((response) => {
        this.room_data = response.data;
      })
      .catch((error) => {
        console.error("Error fetching room data:", error);
        this.$router.push("/browse");
      });

    this.fetchMessages();

    this.socket = io(`${import.meta.env.VITE_API_URL}`);

    this.socket.emit("join", { room_id });

    this.socket.on("message", (message) => {
      this.messages.push(message);

      this.$nextTick(() => {
        this.scrollToBottom();
      });
    });
  },
  methods: {
    async fetchMessages() {
      try {
        const token = localStorage.getItem("token");

        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/rooms/${this.room_id}/messages`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        this.messages = response.data;

        this.$nextTick(() => {
          this.scrollToBottom();
        });
      } catch (error) {
        console.error("Error fetching messages:", error);
      }
    },
    sendMessage() {
      if (!this.newMessage) return;
      const token = localStorage.getItem("token");

      this.socket.emit("message", {
        room_id: this.room_id,
        content: this.newMessage,
        token,
      });

      this.newMessage = "";
    },

    scrollToBottom() {
      const chatContainer = this.$el.querySelector(".chat-messages");
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    },

    async removeRoom() {
      const token = localStorage.getItem("token");

      const response = await axios.delete(
        `${import.meta.env.VITE_API_URL}/api/rooms/${this.room_id}/delete`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (response.status == 200) {
        this.$router.push("/browse");
      } else {
        console.error("Error removing room:", response.data);
      }
    },
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.emit("leave", { room_id: this.room_data.id });
      this.socket.disconnect();
      this.socket = null;
    }
  },
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  overflow: hidden;
}

.room-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.room-top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background: #222;
  color: white;
  width: 100%;
}

.back-button {
  margin-right: auto;
  background: none;
  border: none;
  text-align: left;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  max-width: 150px;
}

.room-name {
  font-size: 1.5rem;
  font-weight: 500;
  text-align: center;
  flex-grow: 1;
}

.remove-button {
  margin-left: auto;
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  max-width: 170px;
  color: red;
  text-transform: uppercase;
}

.content {
  display: flex;
  flex: 1;
  width: 100%;
  height: 100%;
}

.chat-container {
  flex: 1;
  background: #111;
  display: flex;
  flex-direction: column;
  color: white;
  max-height: calc(100vh - 78px);
}

.chat-messages {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
}

.chat-input {
  display: flex;
  padding: 10px;
  background: #222;
}

.chat-input input {
  flex: 4;
  padding: 5px;
  border: none;
  background: #333;
  color: white;
}

.chat-input button {
  flex: 1;
  margin-left: 10px;
  background: #444;
  border: none;
  color: white;
  cursor: pointer;
}

.video-container {
  flex: 3;
  background: #333;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100%;
}
</style>
