import { createRouter, createWebHistory } from "vue-router";
import BrowseRooms from "../views/BrowseRooms.vue";
import RoomView from "../views/RoomView.vue";
import Login from "../views/Login.vue";

const routes = [
  { path: "/browse", component: BrowseRooms, meta: { requiresAuth: true } },
  {
    path: "/rooms/:room_id",
    component: RoomView,
    props: true,
    meta: { requiresAuth: true },
  },
  { path: "/login", component: Login, props: true },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem("token");
  if (to.path === "/") {
    if (token) {
      next("/browse");
    } else {
      next("/login");
    }
  }

  if (to.meta.requiresAuth && token) {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/verify-token`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (response.status === 401) {
        const data = await response.json();
        if (data.logout) {
          localStorage.removeItem("token");
          localStorage.removeItem("username");
          next("/login");
        } else {
          next();
        }
      } else {
        next();
      }
    } catch (error) {
      console.error("Error verifying token:", error);
      next("/login");
    }
  } else if (to.meta.requiresAuth && !token) {
    next("/login");
  } else if (to.path === "/login" && token) {
    next("/browse");
  } else {
    next();
  }
});

export default router;
