<template>
  <div class="profile-container">
    <div class="profile-sidebar">
      <div class="profile-avatar-container">
        <el-upload
          class="avatar-uploader-trigger"
          action=""
          :show-file-list="false"
          :http-request="handleAvatarUpload"
          accept="image/*"
        >
          <div class="avatar-wrapper">
             <img 
              v-if="auth.user?.avatar_url" 
              :src="auth.user.avatar_url" 
              class="profile-avatar"
            />
             <div v-else class="profile-avatar-placeholder">
               {{ auth.user?.username?.charAt(0).toUpperCase() }}
             </div>
             <div class="avatar-overlay">
               <span>更换头像</span>
             </div>
          </div>
        </el-upload>
      </div>

      <div class="profile-names">
        <h1 class="fullname">{{ auth.user?.full_name || auth.user?.username }}</h1>
        <div class="username">{{ auth.user?.username }}</div>
      </div>

      <div class="profile-meta">
        <div class="meta-item">
            <el-icon><User /></el-icon>
            <span>{{ auth.roleLabel }}</span>
        </div>
        <div class="meta-item" v-if="auth.user?.email">
            <el-icon><Message /></el-icon>
            <span>{{ auth.user.email }}</span>
        </div>
         <div class="meta-item" v-if="auth.user?.phone">
            <el-icon><Iphone /></el-icon>
            <span>{{ auth.user.phone }}</span>
        </div>
      </div>
      
      <!-- Actions removed -->
    </div>

    <div class="profile-main">
      <el-tabs v-model="activeTab" class="profile-tabs">
        <el-tab-pane label="个人信息" name="overview">
           <div class="edit-profile-form">
              <h3>修改个人信息</h3>
              <el-alert
                v-if="!isVerified"
                title="为了您的账号安全，请先验证密码以修改信息"
                type="info"
                show-icon
                :closable="false"
                style="margin-bottom: 20px"
              />

              <div v-if="!isVerified">
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
                    <div class="form-actions">
                        <el-button type="primary" :loading="auth.loading" @click="save">保存修改</el-button>
                    </div>
                 </el-form>
              </div>
           </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch, ref, onMounted } from "vue";
import { ElMessage, type UploadRequestOptions } from "element-plus";
import { useAuthStore } from "@/stores/auth";
import { uploadApi, enrollmentApi, courseApi } from "@/services/api";
import { User, Message, Iphone, Notebook } from "@element-plus/icons-vue";
import type { Course } from "@/types";

const auth = useAuthStore();
const isVerified = ref(false);
const activeTab = ref("overview");

const form = reactive({
  old_password: "",
  full_name: "",
  email: "",
  password: "",
  avatar_url: "",
});

const uploadingAvatar = ref(false);

watch(
  () => auth.user,
  (user) => {
    if (user) {
      form.old_password = "";
      form.full_name = user.full_name || "";
      form.email = user.email || "";
      form.avatar_url = user.avatar_url || "";
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

const handleAvatarUpload = async (options: UploadRequestOptions) => {
  const file = options.file as File;
  const isImage = file.type.startsWith('image/');
  const isLt2M = file.size / 1024 / 1024 < 2;

  if (!isImage) {
    ElMessage.error('上传头像图片只能是 JPG/PNG/Format!');
    return;
  }
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB!');
    return;
  }

  uploadingAvatar.value = true;
  try {
    const data = await uploadApi.uploadFile(file);
    // Update local form
    form.avatar_url = data.url; 
    // Immediately update profile to reflect change
    await auth.updateProfile({ avatar_url: data.url });
    options.onSuccess?.(data);
  } catch (error: any) {
    options.onError?.(error);
    ElMessage.error(error?.response?.data?.detail || "头像上传失败");
  } finally {
    uploadingAvatar.value = false;
  }
};

const save = async () => {
  await auth.updateProfile({
    full_name: form.full_name || undefined,
    password: form.password || undefined,
  });
  form.password = "";
  isVerified.value = false;
};
</script>

<style scoped>
.profile-container {
  display: flex;
  gap: 32px;
  align-items: flex-start;
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 20px;
}

/* Sidebar */
.profile-sidebar {
  width: 280px;
  flex-shrink: 0;
}

.profile-avatar-container {
  margin-bottom: 16px;
  position: relative;
}

.avatar-wrapper {
  width: 260px;
  height: 260px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  overflow: hidden;
  position: relative;
  cursor: pointer;
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-avatar-placeholder {
  font-size: 80px;
  color: var(--color-ink-muted);
}

.avatar-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 60px; 
  background: rgba(0, 0, 0, 0.5);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  opacity: 0;
  transition: opacity 0.2s;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.profile-names {
  margin-bottom: 24px;
}

.fullname {
  font-size: 24px;
  line-height: 1.25;
  font-weight: 600;
  color: var(--color-ink);
}

.username {
  font-size: 20px;
  font-style: normal;
  font-weight: 300;
  line-height: 24px;
  color: var(--color-ink-muted);
}

.profile-meta {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-ink);
  font-size: 14px;
}

.profile-actions .el-button {
  width: 100%;
}

/* Main Content */
.profile-main {
  flex: 1;
  min-width: 0;
}

.profile-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
}

.overview-section {
  padding: 16px 0;
}

.pinned-repo-placeholder {
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 24px;
  text-align: center;
  margin-bottom: 16px;
}

.edit-profile-form {
  max-width: 500px;
  margin: 40px auto;
}

.form-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
}

.text-muted {
  font-size: 12px;
  color: var(--color-ink-muted);
}


.section-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 12px;
}

.pinned-courses-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

.pinned-course-card {
    border: 1px solid var(--color-border);
    border-radius: 6px;
    padding: 16px;
    background: var(--color-surface);
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    flex-direction: column;
}

.pinned-course-card:hover {
    border-color: var(--color-text-light); /* Github style hover */
    transform: translateY(-2px);
    box-shadow: var(--shadow-sm);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.repo-icon {
    color: var(--color-ink-muted);
    display: flex;
    align-items: center;
}

.repo-title {
    font-weight: 600;
    color: var(--color-primary);
    font-size: 14px;
    flex: 1;
}

.repo-tag {
    font-size: 12px;
}

.repo-desc {
    font-size: 12px;
    color: var(--color-ink-muted);
    margin-bottom: 16px;
    flex: 1;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.repo-meta {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 16px;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
    color: var(--color-ink-muted);
}

.color-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
}

.calendar-graph {
    border: 1px solid var(--color-border);
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    display: flex;
    gap: 4px;
    justify-content: center;
}

.graph-row {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.graph-cell {
    width: 12px;
    height: 12px;
    border-radius: 2px;
    background-color: #ebedf0;
}

.graph-cell.level-0 { background-color: #ebedf0; }
.graph-cell.level-1 { background-color: #9be9a8; }
.graph-cell.level-2 { background-color: #40c463; }
.graph-cell.level-3 { background-color: #30a14e; }
.graph-cell.level-4 { background-color: #216e39; }

.graph-footer {
    display: flex;
    align-items: center;
    gap: 4px;
    justify-content: flex-end;
    font-size: 12px;
    color: var(--color-ink-muted);
    margin-top: 8px;
}

@media (max-width: 768px) {
  .profile-container {
    flex-direction: column;
  }
  
  .profile-sidebar {
    width: 100%;
  }

  .avatar-wrapper {
    width: 120px;
    height: 120px;
  }
  
  .pinned-courses-grid {
      grid-template-columns: 1fr;
  }
}
</style>
