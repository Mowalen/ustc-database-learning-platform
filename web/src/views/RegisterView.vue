<template>
  <div class="register-view">
    <div class="register-card">
      <div class="register-card__header">
        <div class="welcome-badge">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="8.5" cy="7" r="4"/>
            <line x1="20" y1="8" x2="20" y2="14"/>
            <line x1="23" y1="11" x2="17" y2="11"/>
          </svg>
          <span>创建账户</span>
        </div>
        <h2>开始你的学习之旅</h2>
        <p>选择角色开始你的教学或学习体验</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="register-form"
        @submit.prevent="onSubmit"
      >
        <div class="form-row">
          <el-form-item label="用户名" prop="username" class="form-item-half">
            <el-input 
              v-model="form.username" 
              placeholder="请输入用户名"
              size="large"
              prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item label="姓名" prop="full_name" class="form-item-half">
            <el-input 
              v-model="form.full_name" 
              placeholder="请输入真实姓名"
              size="large"
              prefix-icon="User"
            />
          </el-form-item>
        </div>

        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            show-password 
            placeholder="至少 6 位字符"
            size="large"
            prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="form.email" 
            type="email"
            placeholder="example@ustc.edu.cn"
            size="large"
            prefix-icon="Message"
          />
        </el-form-item>

        <el-form-item label="选择角色" prop="role_id">
          <div class="role-selector">
            <div 
              class="role-option" 
              :class="{ 'role-option--active': form.role_id === 1 }"
              @click="form.role_id = 1"
            >
              <div class="role-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                  <path d="M6 12v5c3 3 9 3 12 0v-5"/>
                </svg>
              </div>
              <div class="role-info">
                <strong>学生</strong>
                <span>选课学习、提交作业</span>
              </div>
              <div class="role-check">
                <svg v-if="form.role_id === 1" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </div>
            </div>

            <div 
              class="role-option" 
              :class="{ 'role-option--active': form.role_id === 2 }"
              @click="form.role_id = 2"
            >
              <div class="role-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M2 3h20"/>
                  <path d="M21 3v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V3"/>
                  <path d="M7 21v-5"/>
                  <path d="M17 21v-5"/>
                  <path d="M12 11h.01"/>
                </svg>
              </div>
              <div class="role-info">
                <strong>教师</strong>
                <span>创建课程、发布任务</span>
              </div>
              <div class="role-check">
                <svg v-if="form.role_id === 2" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </div>
            </div>
          </div>
        </el-form-item>

        <el-button 
          type="primary" 
          :loading="auth.loading" 
          class="submit-btn"
          size="large"
          @click="onSubmit"
        >
          <span v-if="!auth.loading">立即注册</span>
          <span v-else>注册中...</span>
        </el-button>
      </el-form>

      <div class="register-footer">
        <div class="divider">
          <span>或</span>
        </div>
        <div class="login-prompt">
          <span>已有账号？</span>
          <RouterLink to="/login" class="login-link">
            直接登录
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- 装饰性元素 -->
    <div class="decoration decoration-1"></div>
    <div class="decoration decoration-2"></div>
    <div class="decoration decoration-3"></div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
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

const formRef = ref<FormInstance>();

const requireTrim = (message: string) => ({
  validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
    if (!value || !value.trim()) {
      callback(new Error(message));
      return;
    }
    callback();
  },
  trigger: "blur",
});

const rules: FormRules = {
  username: [requireTrim("请输入用户名")],
  full_name: [requireTrim("请输入姓名")],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码至少 6 位字符", trigger: "blur" },
  ],
  email: [
    requireTrim("请输入邮箱"),
    { type: "email", message: "邮箱格式不正确", trigger: "blur" },
  ],
  role_id: [{ required: true, message: "请选择角色", trigger: "change" }],
};

const onSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;
  if (form.role_id === 3) {
    ElMessage.error("注册仅支持学生或教师账号");
    form.role_id = 1;
    return;
  }
  const success = await auth.register({
    username: form.username.trim(),
    password: form.password,
    full_name: form.full_name.trim(),
    email: form.email.trim(),
    role_id: form.role_id,
  });
  if (success) {
    router.push({ name: "login" });
  }
};
</script>

<style scoped>
.register-view {
  position: relative;
  width: 100%;
  padding: 20px 0;
}

.register-card {
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

.register-card__header {
  text-align: center;
  margin-bottom: 36px;
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
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.welcome-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(31, 111, 109, 0.2);
}

.register-card__header h2 {
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

.register-card__header p {
  color: var(--color-ink-muted);
  font-size: 15px;
  line-height: 1.6;
}

.register-form {
  margin-bottom: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-item-half {
  margin-bottom: 0;
}

.register-form :deep(.el-form-item__label) {
  font-weight: 600;
  color: var(--color-ink);
  margin-bottom: 8px;
}

.register-form :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px rgba(31, 111, 109, 0.15) inset;
  transition: all 0.3s ease;
}

.register-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(31, 111, 109, 0.3) inset;
}

.register-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--color-teal) inset !important;
}

/* 角色选择器 */
.role-selector {
  display: flex;
  width: 100%;
}

.role-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px 12px;
  background: rgba(255, 253, 247, 0.5);
  border: 2px solid var(--color-border);
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 100px;
  position: relative;
}

.role-option:first-child {
  border-radius: 12px 0 0 12px;
  z-index: 0;
}

.role-option:last-child {
  border-radius: 0 12px 12px 0;
  margin-left: -2px; /* Overlap borders */
  z-index: 0;
}

.role-option:hover {
  border-color: rgba(31, 111, 109, 0.3);
  background: rgba(31, 111, 109, 0.05);
  z-index: 1;
}

.role-option--active {
  border-color: var(--color-teal);
  background: linear-gradient(135deg, rgba(31, 111, 109, 0.08), rgba(209, 143, 59, 0.08));
  box-shadow: 0 4px 12px rgba(31, 111, 109, 0.15);
  z-index: 2; /* Keep active above hover/siblings */
}

/* ... existing styles ... */
.role-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(31, 111, 109, 0.1), rgba(209, 143, 59, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-teal);
  transition: all 0.3s ease;
}

.role-option--active .role-icon {
  background: linear-gradient(135deg, var(--color-teal), #1e8a87);
  color: white;
}

.role-info {
  text-align: center;
}

.role-info strong {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-ink);
  margin-bottom: 4px;
}

.role-info span {
  display: block;
  font-size: 12px;
  color: var(--color-ink-muted);
}

.role-check {
  position: absolute;
  top: 8px;
  right: 8px;
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.role-option--active .role-check {
  border-color: var(--color-teal);
  background: var(--color-teal);
  color: white;
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
  margin-top: 8px;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(31, 111, 109, 0.4);
}

.submit-btn:active {
  transform: translateY(0);
}

.register-footer {
  margin-top: 28px;
}

.divider {
  text-align: center;
  margin-bottom: 20px;
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

.login-prompt {
  text-align: center;
  color: var(--color-ink-muted);
  font-size: 15px;
}

.login-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--color-teal);
  font-weight: 600;
  margin-left: 8px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.login-link:hover {
  gap: 8px;
  color: var(--color-accent);
}

.login-link svg {
  transition: transform 0.2s ease;
}

.login-link:hover svg {
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
  .register-card {
    padding: 32px 24px;
    border-radius: 20px;
  }

  .register-card__header h2 {
    font-size: 28px;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }

  .form-item-half {
    margin-bottom: 18px;
  }

  .role-selector {
    flex-direction: column;
  }

  .role-option:first-child {
    border-radius: 12px 12px 0 0;
  }

  .role-option:last-child {
    border-radius: 0 0 12px 12px;
    margin-left: 0;
    margin-top: -2px;
  }
}
</style>
