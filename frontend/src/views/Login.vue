<template>
  <div class="auth-container">
    <h2>{{ loginValid ? "Login" : "Register" }}</h2>
    <form @submit.prevent="handleLogin">
      <input v-model="email" type="email" placeholder="Email" required />
      <input
        v-model="password"
        type="password"
        placeholder="Password"
        required
      />
      <input
        v-if="!loginValid"
        v-model="username"
        type="text"
        placeholder="Username"
        required
      />
      <button type="submit">{{ loginValid ? "Login" : "Register" }}</button>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </form>
    <p class="registerlogin" @click="toggleRegister">
      {{
        loginValid ? "No account? Register" : "Already have an account? Login"
      }}
    </p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: "",
      password: "",
      username: "",
      loginValid: true,
      errorMessage: "",
    };
  },
  methods: {
    async handleLogin() {
      const url = this.loginValid
        ? "http://localhost:5000/api/login"
        : "http://localhost:5000/api/register";
      const loginDetails = {
        email: this.email,
        password: this.password,
        ...(this.loginValid ? {} : { username: this.username }),
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
        if (!response.ok) throw new Error(data.error || "Something went wrong");

        localStorage.setItem("user", JSON.stringify(data.user));

        if (this.loginValid) this.$router.push("/browse");
      } catch (error) {
        this.errorMessage = error.message;
      }
    },
    toggleRegister() {
      this.loginValid = !this.loginValid;
      this.errorMessage = "";
    },
  },
};
</script>

<style>
.auth-container {
  max-width: 300px;
  margin: auto;
  text-align: center;
}
input,
button {
  display: block;
  width: 100%;
  margin: 10px 0;
  padding: 8px;
}
.registerlogin {
  cursor: pointer;
  color: blue;
}
</style>
