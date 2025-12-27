<template>
  <div class="auth-form">
    <h2>欢迎回来</h2>
    <p>登录后进入课程与考核管理。</p>
    <el-form :model="form" label-position="top" @submit.prevent="onSubmit">
      <el-form-item label="用户名">
        <el-input v-model="form.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
      </el-form-item>
      <el-button type="primary" :loading="auth.loading" class="submit" @click="onSubmit">
        登录
      </el-button>
    </el-form>
    <div class="auth-footer">
      <span>还没有账号？</span>
      <RouterLink to="/register">立即注册</RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();

const form = reactive({
  username: "",
  password: "",
});

const onSubmit = async () => {
  const success = await auth.login(form.username, form.password);
  if (success) {
    router.push({ name: "dashboard" });
  }
};
</script>

<style scoped>
.auth-form h2 {
  font-family: var(--font-display);
  font-size: 28px;
  margin-bottom: 8px;
}

.auth-form p {
  color: var(--color-ink-muted);
  margin-bottom: 20px;
}

.submit {
  width: 100%;
  margin-top: 12px;
}

.auth-footer {
  margin-top: 20px;
  text-align: center;
  color: var(--color-ink-muted);
}

.auth-footer a {
  color: var(--color-teal);
  font-weight: 600;
  margin-left: 6px;
}
</style>
