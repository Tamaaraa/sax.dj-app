import { createRouter, createWebHistory } from "vue-router";
import BrowseRooms from "../views/BrowseRooms.vue";
import RoomView from "../views/RoomView.vue";

const routes = [
  { path: "/browse", component: BrowseRooms },
  { path: "/rooms/:room_id", component: RoomView, props: true },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
