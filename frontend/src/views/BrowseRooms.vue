<template>
  <div class="browse-container">
    <button @click="showModal = true" class="create-room-btn">
      + Create Room
    </button>

    <div class="rooms-grid">
      <div v-for="room in rooms" :key="room.id" class="room-card">
        <router-link :to="`/rooms/${room.id}`">
          <img class="room-thumbnail" />
          <div class="room-info">
            <h3 class="room-title">{{ room.name }}</h3>
            <p class="room-description">{{ room.description }}</p>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Room Creation Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal">
        <h2>Create a New Room</h2>
        <input v-model="roomName" placeholder="Room Name" />
        <textarea v-model="roomDesc" placeholder="Room Description"></textarea>
        <div class="modal-buttons">
          <button @click="createRoom">Create</button>
          <button @click="showModal = false">Cancel</button>
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
      showModal: false,
      roomName: "",
      roomDesc: "",
      rooms: [],
    };
  },
  mounted() {
    this.fetchRooms();
  },
  methods: {
    async fetchRooms() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/api/browse");
        this.rooms = response.data;
      } catch (error) {
        console.error("Failed to fetch rooms from database: ", error);
      }
    },
    async createRoom() {
      if (!this.roomName.trim()) return alert("Room name is required!");

      try {
        await axios.post("http://127.0.0.1:5000/api/rooms/create", {
          name: this.roomName,
          description: this.roomDesc,
        });

        this.showModal = false;
        this.roomName = "";
        this.roomDesc = "";
        this.fetchRooms();
      } catch (error) {
        console.error("Failed to create room:", error);
      }
    },
  },
};
</script>

<style>
.browse-container {
  padding: 20px;
  background: #121212;
  color: white;
  min-height: 100vh;
}

.rooms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.room-card {
  background: #1e1e1e;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: 0.3s;
  position: relative;

  a {
    text-decoration: inherit;
    color: inherit;
  }

  &:hover {
    background: #292929;
  }
}

.room-thumbnail {
  width: 100%;
  height: 150px;
  object-fit: cover;
  background: url("https://cdn-icons-png.freepik.com/512/683/683935.png")
    center/cover no-repeat;
}

.room-info {
  padding: 10px;
  text-decoration: none;
  color: white;
}

.room-title {
  font-size: 16px;
  font-weight: bold;
}

.room-description {
  font-size: 12px;
  color: #aaa;
}

.create-room-btn {
  padding: 10px;
  background: #444;
  color: white;
  border: none;
  cursor: pointer;
  margin-bottom: 20px;
  max-width: 150px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  background: #222;
  padding: 20px;
  border-radius: 10px;
  width: 300px;
  text-align: center;

  input,
  textarea {
    width: 100%;
    margin: 10px 0;
    padding: 8px;
    background: #333;
    border: none;
    color: white;
  }
}

.modal-buttons {
  display: flex;
  justify-content: space-between;

  button {
    padding: 8px 15px;
    cursor: pointer;
  }
}
</style>
