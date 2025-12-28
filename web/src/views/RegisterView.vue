<template>
  <div class="auth-form">
    <h2>创建账户</h2>
    <p>选择角色开始你的教学或学习旅程。</p>
    <el-form :model="form" label-position="top" @submit.prevent="onSubmit">
      <el-form-item label="用户名">
        <el-input v-model="form.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" show-password placeholder="至少 6 位" />
      </el-form-item>
      <el-form-item label="姓名">
        <el-input v-model="form.full_name" placeholder="请输入姓名" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="form.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="角色">
        <el-select v-model="form.role_id" placeholder="请选择角色" style="width: 100%">
          <el-option label="学生" :value="1" />
          <el-option label="教师" :value="2" />
        </el-select>
      </el-form-item>
      <el-button type="primary" :loading="auth.loading" class="submit" @click="onSubmit">
        注册
      </el-button>
    </el-form>
    <div class="auth-footer">
      <span>已有账号？</span>
      <RouterLink to="/login">直接登录</RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();

const form = reactive({
  username: "",
  password: "",
  full_name: "",
  email: "",
  role_id: 1,
});

const onSubmit = async () => {
  if (form.role_id === 3) {
    ElMessage.error("注册仅支持学生或教师账号");
    form.role_id = 1;
    return;
  }
  const success = await auth.register({
    username: form.username,
    password: form.password,
    full_name: form.full_name || undefined,
    email: form.email || undefined,
    role_id: form.role_id,
  });
  if (success) {
    router.push({ name: "login" });
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
