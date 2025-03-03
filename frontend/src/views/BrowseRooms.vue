<template>
  <div class="browse-container">
    <button @click="showModal = true" class="create-room-btn">
      + Create Room
    </button>

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

    <ul>
      <li v-for="room in rooms" :key="room.id">
        <router-link :to="`/rooms/${room.id}`">{{ room.name }}</router-link>
      </li>
    </ul>
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
        const response = await axios.get("http://127.0.0.1:5000/browse");
        this.rooms = response.data;
      } catch (error) {
        console.error("Failed to fetch rooms from database: ", error);
      }
    },
    async createRoom() {
      if (!this.roomName.trim()) return alert("Room name is required!");

      try {
        await axios.post("http://127.0.0.1:5000/rooms/create", {
          name: this.roomName,
          description: this.roomDesc,
        });

        this.showModal = false;
        this.roomName = "";
        this.roomDesc = "";
        this.fetchRooms(); // Refresh list after creating a room
      } catch (error) {
        console.error("Failed to create room:", error);
      }
    },
  },
};
</script>

<style>
/* Modal Styling */
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
  color: white;

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

.modal-buttons .create-room-btn {
  padding: 10px;
  background: #444;
  color: white;
  border: none;
  cursor: pointer;
}
</style>
