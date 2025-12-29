<template>
  <div class="profile">
    <el-card class="profile-card">
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

    <el-card class="profile-card">
      <h3>更新信息</h3>
      
      <div v-if="!isVerified">
        <el-alert
          title="为了您的账号安全，请先验证密码以修改信息"
          type="info"
          show-icon
          :closable="false"
          style="margin-bottom: 16px"
        />
        <el-form @submit.prevent="handleVerify">
            <el-form-item label="当前密码">
            <el-input 
                v-model="form.old_password" 
                type="password" 
                show-password 
                placeholder="请输入当前密码" 
                @keyup.enter="handleVerify"
            />
            </el-form-item>
            <el-button type="primary" :loading="auth.loading" @click="handleVerify">验证身份</el-button>
        </el-form>
      </div>

      <div v-else>
        <el-alert
            title="身份验证通过，您可以修改信息了"
            type="success"
            show-icon
            :closable="false"
            style="margin-bottom: 16px"
        />
        <el-form :model="form" label-position="top">
            <el-form-item label="姓名">
            <el-input v-model="form.full_name" />
            </el-form-item>
            <el-form-item label="邮箱">
            <el-input v-model="form.email" disabled />
            <span class="text-muted">邮箱不可修改</span>
            </el-form-item>
            <el-form-item label="新密码">
            <el-input v-model="form.password" type="password" show-password placeholder="如果不修改密码，请留空" />
            </el-form-item>
        </el-form>
        <div style="margin-top: 16px">
            <el-button type="primary" :loading="auth.loading" @click="save">保存修改</el-button>
            <el-button @click="isVerified = false">取消</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch, ref } from "vue";
import { ElMessage } from "element-plus";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const isVerified = ref(false);

const form = reactive({
  old_password: "",
  full_name: "",
  email: "",
  password: "",
});

watch(
  () => auth.user,
  (user) => {
    if (user) {
      form.old_password = "";
      form.full_name = user.full_name || "";
      form.email = user.email || "";
      form.password = "";
    }
  },
  { immediate: true }
);

const handleVerify = async () => {
    if (!form.old_password) {
        ElMessage.warning("请先输入密码");
        return;
    }
    const success = await auth.verifyPassword(form.old_password);
    if (success) {
        isVerified.value = true;
        form.old_password = "";
    }
};

const save = async () => {
  await auth.updateProfile({
    full_name: form.full_name || undefined,
    password: form.password || undefined,
  });
  form.password = "";
  // Reset verification after save? Or keep it?
  // Usually keep it until page refresh or manual cancel.
  ElMessage.success("保存成功");
  isVerified.value = false; // Reset to safe state
};
</script>

<style scoped>
.profile {
  display: grid;
  grid-template-columns: repeat(2, minmax(320px, 1fr));
  gap: 20px;
  align-items: start;
}

.profile-card {
  height: 100%;
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

.text-muted {
    font-size: 12px;
    color: var(--color-ink-muted);
}

@media (max-width: 1024px) {
  .profile {
    grid-template-columns: 1fr;
  }
}
</style>
