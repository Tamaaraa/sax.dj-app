<template>
  <button @click="logout" class="logout-button">Logout</button>
</template>

<script>
export default {
  methods: {
    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
.logout-button {
  background-color: #ff4d4d;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.logout-button:hover {
  background-color: #cc0000;
}
</style>
