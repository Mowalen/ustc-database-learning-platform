import { createRouter, createWebHistory } from "vue-router";
import pinia from "@/stores";
import { useAuthStore } from "@/stores/auth";

import AuthLayout from "@/layouts/AuthLayout.vue";
import MainLayout from "@/layouts/MainLayout.vue";

import LoginView from "@/views/LoginView.vue";
import RegisterView from "@/views/RegisterView.vue";
import DashboardView from "@/views/DashboardView.vue";
import CoursesView from "@/views/CoursesView.vue";
import CourseDetailView from "@/views/CourseDetailView.vue";
import EnrollmentsView from "@/views/EnrollmentsView.vue";
import TasksCenterView from "@/views/TasksCenterView.vue";
import ScoresView from "@/views/ScoresView.vue";
import AnnouncementsView from "@/views/AnnouncementsView.vue";
import AdminView from "@/views/AdminView.vue";
import AdminAnnouncementsView from "@/views/AdminAnnouncementsView.vue";
import ProfileView from "@/views/ProfileView.vue";
import NotFoundView from "@/views/NotFoundView.vue";
import TeacherCoursesView from "@/views/TeacherCoursesView.vue";

const routes = [
  {
    path: "/",
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: "", name: "dashboard", component: DashboardView },
      { path: "courses", name: "courses", component: CoursesView },
      {
        path: "courses/:id",
        name: "course-detail",
        component: CourseDetailView,
        props: true,
      },
      {
        path: "enrollments",
        name: "enrollments",
        component: EnrollmentsView,
        meta: { roles: [1] },
      },
      {
        path: "tasks",
        name: "tasks-center",
        component: TasksCenterView,
        meta: { roles: [1, 2] },
      },
      {
        path: "scores",
        name: "scores",
        component: ScoresView,
        meta: { roles: [1, 2] },
      },
      {
        path: "teaching",
        name: "teaching",
        component: TeacherCoursesView,
        meta: { roles: [2] },
      },
      {
        path: "announcements",
        name: "announcements",
        component: AnnouncementsView,
      },
      {
        path: "admin",
        name: "admin",
        component: AdminView,
        meta: { roles: [3] },
      },
      {
        path: "admin/announcements",
        name: "admin-announcements",
        component: AdminAnnouncementsView,
        meta: { roles: [3] },
      },
      {
        path: "profile",
        name: "profile",
        component: ProfileView,
      },
    ],
  },
  {
    path: "/",
    component: AuthLayout,
    children: [
      { path: "login", name: "login", component: LoginView },
      { path: "register", name: "register", component: RegisterView },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: NotFoundView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
});

router.beforeEach(async (to) => {
  const authStore = useAuthStore(pinia);
  await authStore.initialize();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: "login" };
  }

  if ((to.name === "login" || to.name === "register") && authStore.isAuthenticated) {
    return { name: "dashboard" };
  }

  const roles = (to.meta.roles as number[] | undefined) ?? null;
  if (roles && authStore.roleId && !roles.includes(authStore.roleId)) {
    return { name: "dashboard" };
  }

  return true;
});

export default router;
