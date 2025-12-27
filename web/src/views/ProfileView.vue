<template>
  <div class="profile">
    <el-card>
      <div class="profile__header">
        <div>
          <h2>个人中心</h2>
          <p>更新你的联系方式与密码。</p>
        </div>
        <el-tag effect="light">{{ auth.roleLabel }}</el-tag>
      </div>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户 ID">{{ auth.user?.id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ auth.user?.username }}</el-descriptions-item>
        <el-descriptions-item label="姓名">{{ auth.user?.full_name || "-" }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ auth.user?.email || "-" }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card>
      <h3>更新信息</h3>
      <el-form :model="form" label-position="top">
        <el-form-item label="姓名">
          <el-input v-model="form.full_name" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
      </el-form>
      <el-button type="primary" :loading="auth.loading" @click="save">保存修改</el-button>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from "vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();

const form = reactive({
  full_name: "",
  email: "",
  password: "",
});

watch(
  () => auth.user,
  (user) => {
    if (user) {
      form.full_name = user.full_name || "";
      form.email = user.email || "";
      form.password = "";
    }
  },
  { immediate: true }
);

const save = async () => {
  await auth.updateProfile({
    full_name: form.full_name || undefined,
    email: form.email || undefined,
    password: form.password || undefined,
  });
};
</script>

<style scoped>
.profile {
  display: grid;
  gap: 16px;
}

.profile__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.profile__header h2 {
  font-family: var(--font-display);
  margin-bottom: 6px;
}

.profile__header p {
  color: var(--color-ink-muted);
}

h3 {
  margin-bottom: 12px;
}
</style>
