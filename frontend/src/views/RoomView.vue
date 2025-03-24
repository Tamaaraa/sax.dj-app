<template>
  <div class="room-container">
    <div class="room-top-bar">
      <button @click="$router.push('/browse')" class="back-button">
        ← Back
      </button>
      <h1 class="room-name">{{ room_data.name }}</h1>
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
            <strong>{{ message.username }}:</strong> {{ message.content }}
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
      messages: [],
      newMessage: "",
      socket: null,
    };
  },
  mounted() {
    const token = localStorage.getItem("token");
    const room_id = this.$route.params.room_id;

    if (!token) {
      console.error("No token found, redirecting to login...");
      this.$router.push("/login");
      return;
    }

    // Fetch room details
    axios
      .get(`http://127.0.0.1:5000/api/rooms/${room_id}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((response) => {
        this.room_data = response.data;
        this.room_data.id = room_id;
      })
      .catch((error) => console.error("Error fetching room data:", error));

    this.fetchMessages();

    this.socket = io("http://127.0.0.1:5000");

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
        const room_id = this.$route.params.room_id;

        const response = await axios.get(
          `http://127.0.0.1:5000/api/rooms/${room_id}/messages`,
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
      const username = localStorage.getItem("username");

      this.socket.emit("message", {
        room_id: this.room_data.id,
        content: this.newMessage,
        token,
        username,
      });

      this.newMessage = "";
    },

    scrollToBottom() {
      const chatContainer = this.$el.querySelector(".chat-messages");
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
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
  padding: 10px 90px 10px 10px;
  background: #222;
  color: white;
  width: 100%;
}

.back-button {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  max-width: 90px;
}

.room-name {
  margin: 0 auto;
  font-size: 1.5rem;
  font-weight: 500;
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
