<template>
  <div class="room-container">
    <div class="top-bar">
      <button @click="$router.push('/browse')" class="back-button">
        ← Back
      </button>
      <h1 class="room-name">{{ room_data.name }}</h1>
    </div>

    <div class="content">
      <div class="video-container">
        <h2>Now Playing</h2>
        <p>Embed YouTube player here</p>
      </div>

      <div class="chat-container">
        <div class="chat-messages">
          <div
            v-for="(message, index) in chatMessages"
            :key="index"
            class="chat-message"
          >
            <strong>{{ message.username }}:</strong> {{ message.text }}
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

export default {
  data() {
    return {
      room_data: {},
      chatMessages: [],
      newMessage: "",
    };
  },
  mounted() {
    const room_id = this.$route.params.room_id;

    // Fetch room details
    axios
      .get(`http://127.0.0.1:5000/rooms/${room_id}`)
      .then((response) => {
        this.room_data = response.data;
      })
      .catch((error) => {
        console.error("Error fetching room data:", error);
      });
  },
  methods: {
    sendMessage() {
      if (this.newMessage.trim() !== "") {
        this.chatMessages.push({ username: "You", text: this.newMessage });
        this.newMessage = "";
      }
    },
  },
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.room-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.top-bar {
  display: flex;
  align-items: center;
  padding: 10px;
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

.video-container {
  flex: 4;
  background: #333;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* Chat Section */
.chat-container {
  flex: 1;
  background: #111;
  display: flex;
  flex-direction: column;
  color: white;
  height: 100%;
}

/* Chat Messages */
.chat-messages {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
}

/* Chat Input */
.chat-input {
  display: flex;
  padding: 10px;
  background: #222;
}

.chat-input input {
  flex: 1;
  padding: 5px;
  border: none;
  background: #333;
  color: white;
}

.chat-input button {
  margin-left: 10px;
  background: #444;
  border: none;
  color: white;
  cursor: pointer;
}
</style>
