<template>
  <iframe
    width="100%"
    height="100%"
    :src="currentVideoUrl"
    frameborder="0"
    allow="autoplay"
  ></iframe>
  <div class="queue-container">
    <div class="queue-controls">
      <input v-model="newVideoUrl" placeholder="Add YouTube URL..." />
      <button @click="addVideoToQueue">Add to Queue</button>
    </div>
    <div class="video-queue">
      <h3>Video Queue</h3>
      <ul>
        <li v-for="(video, index) in videoQueue" :key="index">
          <div class="queue-details">
            <strong>{{ video.video_name }}</strong>
            <span>By {{ video.requested_by }}</span>
          </div>
          <button @click="removeVideoFromQueue(video.id)">Remove</button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  props: {
    socket: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      videoQueue: [],
      currentVideoUrl: "",
      newVideoUrl: "",
    };
  },

  mounted() {
    this.fetchVideoQueue();

    this.socket.on("play_next_video", (data) => {
      this.currentVideoUrl = data.video_url;
    });
  },
  methods: {
    async fetchVideoQueue() {
      try {
        const room_id = this.$route.params.room_id;
        const token = localStorage.getItem("token");

        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/rooms/${room_id}/queue`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        this.videoQueue = response.data.map((video) => ({
          id: video.id,
          video_url: video.video_url,
          video_name: video.title,
          requested_by: video.requester,
        }));

        if (this.videoQueue.length >= 1 && !this.currentVideoUrl) {
          this.currentVideoUrl = this.videoQueue[0].video_url;
          this.socket.emit("play_next_video", {
            room_id,
          });
        }
      } catch (error) {
        console.error("Error fetching video queue:", error);
      }
    },
    async addVideoToQueue() {
      if (!this.newVideoUrl) return;

      try {
        const room_id = this.$route.params.room_id;
        const token = localStorage.getItem("token");

        await axios.post(
          `${import.meta.env.VITE_API_URL}/api/rooms/${room_id}/queue`,
          {
            video_url: this.newVideoUrl,
            requester: localStorage.getItem("username"),
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        this.newVideoUrl = "";
        this.fetchVideoQueue();
      } catch (error) {
        console.error("Error adding video to queue:", error);
      }
    },
    async removeVideoFromQueue(videoId) {
      try {
        const room_id = this.$route.params.room_id;
        const token = localStorage.getItem("token");

        await axios.delete(
          `${import.meta.env.VITE_API_URL}/api/rooms/${room_id}/queue`,
          {
            headers: { Authorization: `Bearer ${token}` },
            data: { video_id: videoId },
          }
        );
        this.fetchVideoQueue();
      } catch (error) {
        console.error("Error removing video from queue:", error);
      }
    },
  },
};
</script>

<style>
.queue-container {
  margin: 20px;
  min-width: 50%;
}

.queue-controls {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

.video-queue {
  margin-top: 20px;
  overflow-y: auto;
  padding: 10px;
}

.video-queue ul {
  list-style: none;
  padding: 0;
}

.video-queue li {
  display: flex;
  border-bottom: 1px solid #ccc;
  justify-content: space-between;
  margin-bottom: 5px;
  margin-top: 5px;
  vertical-align: middle;

  .queue-details {
    display: flex;
    flex: 4;
    flex-direction: column;
    gap: 5px;
  }

  button {
    flex: 1;
  }
}
</style>
