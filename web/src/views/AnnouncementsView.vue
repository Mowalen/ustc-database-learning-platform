<template>
  <div class="announcements">
    <div class="header">
      <div>
        <h2>公告看板</h2>
        <p>查看系统公告与课程通知。</p>
      </div>
      <div class="header__actions">
        <el-switch v-if="isAdmin" v-model="includeInactive" active-text="包含停用" />
        <el-button @click="loadAnnouncements">刷新</el-button>
        <el-button v-if="isAdmin" type="primary" @click="openDialog">发布公告</el-button>
      </div>
    </div>

    <div class="announcement-grid">
      <el-card v-for="item in announcements" :key="item.id" class="announcement-card">
        <div class="announcement-card__head">
          <h3>{{ item.title }}</h3>
          <el-tag v-if="!item.is_active" type="danger" effect="light">已停用</el-tag>
        </div>
        <p>{{ item.content }}</p>
        <div class="announcement-card__meta">
          <span>发布人 ID：{{ item.created_by }}</span>
          <span>{{ formatDate(item.created_at) }}</span>
        </div>
      </el-card>
    </div>

    <el-dialog v-model="dialogVisible" title="发布公告" width="520px">
      <el-form :model="form" label-position="top">
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAnnouncement">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import { adminApi } from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import type { Announcement } from "@/types";
import { formatDate } from "@/utils/format";

const auth = useAuthStore();
const announcements = ref<Announcement[]>([]);
const dialogVisible = ref(false);
const includeInactive = ref(false);

const form = reactive({
  title: "",
  content: "",
  is_active: true,
});

const isAdmin = computed(() => auth.roleId === 3);

const loadAnnouncements = async () => {
  try {
    announcements.value = await adminApi.listAnnouncements(includeInactive.value);
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "加载公告失败");
  }
};

const openDialog = () => {
  Object.assign(form, { title: "", content: "", is_active: true });
  dialogVisible.value = true;
};

const submitAnnouncement = async () => {
  if (!auth.user) return;
  try {
    await adminApi.createAnnouncement({
      title: form.title,
      content: form.content,
      created_by: auth.user.id,
      is_active: form.is_active,
    });
    ElMessage.success("公告已发布");
    dialogVisible.value = false;
    await loadAnnouncements();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "发布失败");
  }
};

watch(includeInactive, () => {
  loadAnnouncements().catch(() => undefined);
});

onMounted(() => {
  loadAnnouncements().catch(() => undefined);
});
</script>

<style scoped>
.announcements {
  display: grid;
  gap: 16px;
}

.header {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.header h2 {
  font-family: var(--font-display);
  margin-bottom: 6px;
}

.header p {
  color: var(--color-ink-muted);
}

.header__actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.announcement-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.announcement-card h3 {
  font-size: 18px;
  margin-bottom: 6px;
}

.announcement-card p {
  color: var(--color-ink-muted);
  min-height: 48px;
}

.announcement-card__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.announcement-card__meta {
  margin-top: 12px;
  font-size: 12px;
  color: var(--color-ink-muted);
  display: flex;
  justify-content: space-between;
}
</style>
