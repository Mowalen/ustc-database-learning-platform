<template>
  <div class="page-shell">
    <aside class="sidebar" :class="{ open: mobileMenuOpen }">
      <div class="brand">
        <div class="brand__logo">USTC</div>
        <div>
          <h2>数据库学习平台</h2>
          <span>教学 · 练习 · 考核</span>
        </div>
      </div>
      <div class="user-card">
        <div class="avatar">
          <img
            v-if="auth.user?.avatar_url"
            :src="auth.user.avatar_url"
            alt="avatar"
          />
          <span v-else>{{
            auth.user?.username?.slice(0, 2)?.toUpperCase()
          }}</span>
        </div>
        <div>
          <strong>{{ auth.user?.full_name || auth.user?.username }}</strong>
          <small>{{ auth.roleLabel }}</small>
        </div>
      </div>
      <el-menu
        class="nav-menu"
        :default-active="activePath"
        router
        @select="handleSelect"
      >
        <el-menu-item
          v-for="item in visibleMenuItems"
          :key="item.path"
          :index="item.path"
        >
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar__footer">
        <el-button type="primary" plain @click="goProfile">个人设置</el-button>
        <el-button type="danger" plain @click="logout">退出登录</el-button>
      </div>
    </aside>

    <main class="content">
      <header class="topbar">
        <div>
          <h1>{{ pageTitle }}</h1>
          <p>{{ pageDesc }}</p>
        </div>
        <div class="topbar__actions">
          <el-button class="mobile-toggle" @click="toggleMenu">菜单</el-button>
          <el-tag type="warning" effect="light">{{ auth.roleLabel }}</el-tag>
        </div>
      </header>
      <section class="content-body">
        <RouterView />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();
const mobileMenuOpen = ref(false);

const menuItems = [
  { path: "/", label: "我的主页", roles: [1, 2, 3] },
  { path: "/courses", label: "课程管理", roles: [1, 2, 3] },
  { path: "/teaching", label: "我的授课", roles: [2] },
  { path: "/enrollments", label: "我的选课", roles: [1] },
  { path: "/tasks", label: "作业与考试", roles: [] },
  { path: "/scores", label: "成绩反馈", roles: [] },
  { path: "/announcements", label: "公告看板", roles: [1, 2] },
  { path: "/admin", label: "用户管理", roles: [3] },
  { path: "/admin/announcements", label: "公告管理", roles: [3] },
];

const visibleMenuItems = computed(() =>
  menuItems.filter((item) => item.roles.includes(auth.roleId || 0))
);

const activePath = computed(() => {
  if (route.path.startsWith("/courses/")) return "/courses";
  return route.path === "/" ? "/" : route.path;
});

const pageTitle = computed(() => {
  const item = menuItems.find((m) => m.path === activePath.value);
  return item?.label || "学习平台";
});

const pageDesc = computed(() => {
  if (activePath.value === "/admin") {
    return "管理用户账号、课程状态与系统运行。";
  }
  return "专注数据库课程的教学流程与学习体验。";
});

const logout = () => {
  auth.logout();
  router.push({ name: "login" });
};

const goProfile = () => {
  router.push({ name: "profile" });
};

const handleSelect = () => {
  mobileMenuOpen.value = false;
};

const toggleMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value;
};
</script>

<style scoped>
.sidebar {
  background: var(--color-surface);
  padding: 32px 24px;
  border-right: 1px solid var(--color-border);
  position: relative;
  min-height: 100vh;
}

.brand {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-bottom: 28px;
}

.brand__logo {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: linear-gradient(
    140deg,
    var(--color-accent) 0%,
    var(--color-teal) 100%
  );
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 700;
  font-family: var(--font-display);
}

.brand h2 {
  font-size: 18px;
  font-family: var(--font-display);
}

.brand span {
  font-size: 12px;
  color: var(--color-ink-muted);
}

.user-card {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 14px;
  background: rgba(209, 143, 59, 0.08);
  border-radius: 16px;
  margin-bottom: 24px;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: rgba(31, 111, 109, 0.2);
  display: grid;
  place-items: center;
  font-weight: 700;
  color: var(--color-teal);
  overflow: hidden;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-card strong {
  display: block;
  font-size: 14px;
}

.user-card small {
  color: var(--color-ink-muted);
  font-size: 12px;
}

.nav-menu {
  border-right: none;
  background: transparent;
}

.sidebar__footer {
  position: absolute;
  bottom: 24px;
  left: 24px;
  right: 24px;
  display: grid;
  gap: 12px;
}

.sidebar__footer .el-button {
  width: 100%;
  justify-content: center;
  height: 40px;
  padding: 0 16px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  line-height: 1;
}

.sidebar__footer .el-button + .el-button {
  margin-left: 0;
}

.content {
  padding: 32px 40px 40px;
  min-width: 0;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

.topbar h1 {
  font-family: var(--font-display);
  font-size: 28px;
}

.topbar p {
  color: var(--color-ink-muted);
  margin-top: 6px;
}

.topbar__actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.mobile-toggle {
  display: none;
}

.content-body {
  background: rgba(255, 253, 247, 0.75);
  border-radius: 24px;
  padding: 24px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-soft);
  min-width: 0;
  min-height: calc(100vh - 200px);
}

@media (max-width: 960px) {
  .sidebar {
    position: fixed;
    z-index: 10;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    box-shadow: var(--shadow-card);
    width: 80%;
    max-width: 320px;
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .content {
    padding: 24px;
  }

  .mobile-toggle {
    display: inline-flex;
  }

  .sidebar__footer {
    position: static;
    margin-top: 24px;
  }
}
</style>
