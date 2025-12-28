import { defineStore } from "pinia";
import { ElMessage } from "element-plus";
import { authApi, userApi } from "@/services/api";
import type { User } from "@/types";

const formatValidationError = (detail: any) => {
  if (!Array.isArray(detail)) {
    return "";
  }
  const messages = detail.map((item) => {
    const loc = Array.isArray(item?.loc) ? item.loc : [];
    const field = loc.slice(1).join(".") || "field";
    const msg = item?.msg || "invalid value";
    return `${field}: ${msg}`;
  });
  return messages.join("；");
};

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as User | null,
    token: localStorage.getItem("access_token") || "",
    initialized: false,
    loading: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    roleId: (state) => state.user?.role_id || null,
    roleLabel: (state) => {
      switch (state.user?.role_id) {
        case 1:
          return "学生";
        case 2:
          return "教师";
        case 3:
          return "管理员";
        default:
          return "访客";
      }
    },
  },
  actions: {
    async initialize() {
      if (this.initialized) return;
      if (!this.token) {
        this.initialized = true;
        return;
      }
      try {
        this.user = await userApi.me();
      } catch (error) {
        this.clearSession();
      } finally {
        this.initialized = true;
      }
    },
    setToken(token: string) {
      this.token = token;
      localStorage.setItem("access_token", token);
    },
    clearSession() {
      this.token = "";
      this.user = null;
      localStorage.removeItem("access_token");
    },
    async login(username: string, password: string) {
      this.loading = true;
      try {
        const data = await authApi.login(username, password);
        this.setToken(data.access_token);
        this.user = await userApi.me();
        ElMessage.success("登录成功，欢迎回来");
        return true;
      } catch (error: any) {
        ElMessage.error(error?.response?.data?.detail || "登录失败，请检查账号或密码");
        return false;
      } finally {
        this.loading = false;
      }
    },
    async register(payload: {
      username: string;
      password: string;
      email?: string;
      full_name?: string;
      role_id: number;
    }) {
      this.loading = true;
      try {
        await authApi.register(payload);
        ElMessage.success("注册成功，请登录");
        return true;
      } catch (error: any) {
        const detail = error?.response?.data?.detail;
        const formatted = formatValidationError(detail);
        ElMessage.error(formatted || detail || "注册失败，请检查输入");
        return false;
      } finally {
        this.loading = false;
      }
    },
    async refreshProfile() {
      try {
        this.user = await userApi.me();
      } catch (error: any) {
        ElMessage.error("获取用户信息失败");
      }
    },
    async updateProfile(payload: {
      old_password: string;
      full_name?: string;
      email?: string;
      password?: string;
    }) {
      this.loading = true;
      try {
        this.user = await userApi.updateMe(payload);
        ElMessage.success("个人信息已更新");
        return true;
      } catch (error: any) {
        ElMessage.error(error?.response?.data?.detail || "更新失败");
        return false;
      } finally {
        this.loading = false;
      }
    },
    logout() {
      this.clearSession();
      ElMessage.success("已退出登录");
    },
  },
});
