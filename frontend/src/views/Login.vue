<template>
  <div class="centered-div">
    <div class="auth-container">
      <h2>{{ isLogin ? "Login" : "Register" }}</h2>
      <form @submit.prevent="handleLogin">
        <input v-model="email" type="email" placeholder="Email" required />
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          required
        />
        <input
          v-if="!isLogin"
          v-model="username"
          type="text"
          placeholder="Username"
          required
        />
        <button type="submit">{{ isLogin ? "Login" : "Register" }}</button>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </form>
      <p class="registerlogin" @click="toggleRegister">
        {{
          isLogin ? "No account? Register" : "Already have an account? Login"
        }}
      </p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: "",
      password: "",
      username: "",
      isLogin: true,
      errorMessage: "",
    };
  },
  methods: {
    async handleLogin() {
      const url = this.isLogin
        ? `${import.meta.env.VITE_API_URL}/api/login`
        : `${import.meta.env.VITE_API_URL}/api/register`;

      const loginDetails = {
        email: this.email,
        password: this.password,
        ...(this.isLogin ? {} : { username: this.username }),
      };

      try {
        const response = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(loginDetails),
        });

        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || "Something went wrong");
        }
        localStorage.setItem("token", data.token);
        localStorage.setItem("username", data.username);

        this.$router.push("/browse");
      } catch (error) {
        this.errorMessage = error.message;
      }
    },
    toggleRegister() {
      this.isLogin = !this.isLogin;
      this.errorMessage = "";
    },
  },
};
</script>

<style>
.centered-div {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #121212;
  color: whitesmoke;
  min-height: 100vh;
  width: 100vw;
}

.auth-container {
  text-align: center;
  height: 200px;
  width: 300px;
}

input,
button {
  background: #444;
  color: white;
  display: block;
  border: none;
  width: 100%;
  margin: 10px 0;
  padding: 8px;
}
.registerlogin {
  cursor: pointer;
  color: rgb(0, 161, 161);
}
</style>
