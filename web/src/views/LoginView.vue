<template>
  <div class="login-view">
    <div class="login-card">
      <div class="login-card__header">
        <div class="welcome-badge">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
          <span>学习平台</span>
        </div>
        <h2>欢迎回来</h2>
        <p>登录后进入课程与考核管理平台</p>
      </div>

      <el-form :model="form" label-position="top" class="login-form" @submit.prevent="onSubmit">
        <el-form-item label="用户名">
          <el-input 
            v-model="form.username" 
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item label="密码">
          <el-input 
            v-model="form.password" 
            type="password" 
            show-password 
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            @keyup.enter="onSubmit"
          />
        </el-form-item>

        <div class="login-options">
          <el-checkbox v-model="rememberMe">记住我</el-checkbox>
          <a href="#" class="forgot-link" @click.prevent="openResetDialog">忘记密码？</a>
        </div>

        <el-button 
          type="primary" 
          :loading="auth.loading" 
          class="submit-btn"
          size="large"
          @click="onSubmit"
        >
          <span v-if="!auth.loading">登录</span>
          <span v-else>登录中...</span>
        </el-button>
      </el-form>

      <div class="login-footer">
        <div class="divider">
          <span>或</span>
        </div>
        <div class="register-prompt">
          <span>还没有账号？</span>
          <RouterLink to="/register" class="register-link">
            立即注册
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </RouterLink>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="resetDialogVisible"
      title="找回密码"
      width="420px"
      append-to-body
    >
      <el-form :model="resetForm" label-position="top">
        <el-form-item label="邮箱">
          <el-input v-model="resetForm.email" type="email" placeholder="请输入注册邮箱" />
        </el-form-item>
        <el-form-item label="验证码">
          <el-input v-model="resetForm.code" placeholder="请输入验证码">
            <template #append>
              <el-button :loading="resetLoading" @click="requestResetCode">
                发送验证码
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="resetForm.new_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="resetLoading" @click="submitReset">
          重置密码
        </el-button>
      </template>
    </el-dialog>

    <!-- 装饰性元素 -->
    <div class="decoration decoration-1"></div>
    <div class="decoration decoration-2"></div>
    <div class="decoration decoration-3"></div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { authApi } from "@/services/api";
import { translateAuthDetail } from "@/utils/authMessages";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();

const form = reactive({
  username: "",
  password: "",
});

const rememberMe = ref(false);
const resetDialogVisible = ref(false);
const resetLoading = ref(false);

const resetForm = reactive({
  email: "",
  code: "",
  new_password: "",
});

const onSubmit = async () => {
  const success = await auth.login(form.username, form.password);
  if (success) {
    router.push({ name: "dashboard" });
  }
};

const openResetDialog = () => {
  resetDialogVisible.value = true;
  resetForm.code = "";
  resetForm.new_password = "";
};

const requestResetCode = async () => {
  if (!resetForm.email) {
    ElMessage.warning("请输入邮箱");
    return;
  }
  resetLoading.value = true;
  try {
    await authApi.requestPasswordReset(resetForm.email);
    ElMessage.success("验证码已发送");
  } catch (error: any) {
    const detail = error?.response?.data?.detail;
    const translated = translateAuthDetail(typeof detail === "string" ? detail : "");
    ElMessage.error(translated || "发送验证码失败");
  } finally {
    resetLoading.value = false;
  }
};

const submitReset = async () => {
  if (!resetForm.email || !resetForm.code || !resetForm.new_password) {
    ElMessage.warning("请完整填写邮箱、验证码和新密码");
    return;
  }
  resetLoading.value = true;
  try {
    await authApi.confirmPasswordReset({
      email: resetForm.email,
      code: resetForm.code,
      new_password: resetForm.new_password,
    });
    ElMessage.success("密码已重置，请使用新密码登录");
    resetDialogVisible.value = false;
  } catch (error: any) {
    const detail = error?.response?.data?.detail;
    const translated = translateAuthDetail(typeof detail === "string" ? detail : "");
    ElMessage.error(translated || "重置密码失败");
  } finally {
    resetLoading.value = false;
  }
};
</script>

<style scoped>
.login-view {
  position: relative;
  width: 100%;
  padding: 20px 0;
}

.login-card {
  position: relative;
  background: var(--color-surface);
  border-radius: 24px;
  padding: 48px;
  max-width: 480px;
  width: 100%;
  margin: 0 auto;
  box-shadow: 
    0 20px 60px rgba(31, 111, 109, 0.12),
    0 0 0 1px rgba(31, 111, 109, 0.1);
  animation: slideUp 0.6s ease-out;
  z-index: 1;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-card__header {
  text-align: center;
  margin-bottom: 40px;
}

.welcome-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, rgba(31, 111, 109, 0.1), rgba(209, 143, 59, 0.1));
  border: 1px solid rgba(31, 111, 109, 0.2);
  border-radius: 999px;
  color: var(--color-teal);
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.welcome-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(31, 111, 109, 0.2);
}

.welcome-badge svg {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-5px);
  }
}

.login-card__header h2 {
 font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  color: var(--color-ink);
  margin-bottom: 12px;
  background: linear-gradient(135deg, var(--color-teal), var(--color-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-card__header p {
  color: var(--color-ink-muted);
  font-size: 15px;
  line-height: 1.6;
}

.login-form {
  margin-bottom: 24px;
}

.login-form :deep(.el-form-item__label) {
  font-weight: 600;
  color: var(--color-ink);
  margin-bottom: 8px;
}

.login-form :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px rgba(31, 111, 109, 0.15) inset;
  transition: all 0.3s ease;
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(31, 111, 109, 0.3) inset;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--color-teal) inset !important;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.forgot-link {
  color: var(--color-teal);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
}

.forgot-link:hover {
  color: var(--color-teal);
  text-decoration: underline;
}

.submit-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--color-teal), #1e8a87);
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(31, 111, 109, 0.3);
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(31, 111, 109, 0.4);
}

.submit-btn:active {
  transform: translateY(0);
}

.login-footer {
  margin-top: 32px;
}

.divider {
  text-align: center;
  margin-bottom: 24px;
  position: relative;
}

.divider::before,
.divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 40%;
  height: 1px;
  background: var(--color-border);
}

.divider::before {
  left: 0;
}

.divider::after {
  right: 0;
}

.divider span {
  display: inline-block;
  padding: 0 16px;
  background: var(--color-surface);
  color: var(--color-ink-muted);
  font-size: 14px;
}

.register-prompt {
  text-align: center;
  color: var(--color-ink-muted);
  font-size: 15px;
}

.register-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--color-teal);
  font-weight: 600;
  margin-left: 8px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.register-link:hover {
  gap: 8px;
  color: var(--color-accent);
}

.register-link svg {
  transition: transform 0.2s ease;
}

.register-link:hover svg {
  transform: translateX(4px);
}

/* 装饰性元素 */
.decoration {
  position: absolute;
  border-radius: 50%;
  opacity: 0.6;
  z-index: 0;
  animation: pulse 4s ease-in-out infinite;
}

.decoration-1 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(31, 111, 109, 0.1), transparent);
  top: -150px;
  right: -150px;
  animation-delay: 0s;
}

.decoration-2 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(209, 143, 59, 0.1), transparent);
  bottom: -100px;
  left: -100px;
  animation-delay: 1s;
}

.decoration-3 {
  width: 150px;
  height: 150px;
  background: radial-gradient(circle, rgba(31, 111, 109, 0.08), transparent);
  top: 50%;
  left: -75px;
  animation-delay: 2s;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

@media (max-width: 600px) {
  .login-card {
    padding: 32px 24px;
    border-radius: 20px;
  }

  .login-card__header h2 {
    font-size: 28px;
  }
}
</style>
