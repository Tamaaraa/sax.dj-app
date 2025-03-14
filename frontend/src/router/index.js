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

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  if (to.path === "/") {
    if (token) {
      next("/browse");
    } else {
      next("/login");
    }
  }

  if (to.meta.requiresAuth && !token) {
    next("/login");
  } else if (to.path === "/login" && token) {
    next("/browse");
  } else {
    next();
  }
});

export default router;
