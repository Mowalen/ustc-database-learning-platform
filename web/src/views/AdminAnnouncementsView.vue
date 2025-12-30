<template>
  <div class="announcement-management">
    <div class="panel-header">
      <div class="header-right">
        <!-- Search could be added here if needed, but backend listAnnouncements doesn't support query yet. 
             If needed, I'd filter client side or add backend support. 
             For now, I'll allow client-side filtering if I add a search bar. -->
        <el-input
          v-model="searchQuery"
          placeholder="搜索公告标题"
          class="search-input"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="openCreate">新建公告</el-button>
      </div>
    </div>

    <el-table :data="paginatedAnnouncements" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" align="center" width="80" />
      <el-table-column prop="title" label="标题" align="center" show-overflow-tooltip />
      <el-table-column prop="content" label="内容" align="center" show-overflow-tooltip />
      <el-table-column label="发布时间" align="center" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" align="center" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'info'" effect="plain">
            {{ scope.row.is_active ? "有效" : "已停用" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="200">
        <template #default="scope">
          <div class="action-buttons">
            <el-button
              size="small"
              type="warning"
              plain
              @click="openEdit(scope.row)"
            >
              编辑
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination" v-if="filteredAnnouncements.length > 0">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="filteredAnnouncements.length"
        layout="total, prev, pager, next, jumper"
        background
      />
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="520px"
      append-to-body
      destroy-on-close
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" :rows="4" />
        </el-form-item>
         <el-form-item label="状态" v-if="editId">
          <el-switch
            v-model="form.is_active"
            active-text="有效"
            inactive-text="停用"
          />
        </el-form-item>
      </el-form>
      
      <div class="dialog-actions-danger" v-if="editId">
        <el-divider content-position="left">危险区域</el-divider>
        <el-button type="danger" plain @click="handleDelete"
          >删除此公告</el-button
        >
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search } from "@element-plus/icons-vue";
import { adminApi } from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import type { Announcement } from "@/types";
import { formatDate } from "@/utils/format";

const auth = useAuthStore();
const loading = ref(false);
const announcements = ref<Announcement[]>([]);
const searchQuery = ref("");
const currentPage = ref(1);
const pageSize = ref(10);

const dialogVisible = ref(false);
const dialogTitle = ref("新建公告");
const editId = ref<number | null>(null);

const form = reactive({
  title: "",
  content: "",
  is_active: true,
});

const filteredAnnouncements = computed(() => {
  let result = announcements.value;
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(
      (a) =>
        a.title.toLowerCase().includes(q) || a.content.toLowerCase().includes(q)
    );
  }
  return result;
});

const paginatedAnnouncements = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredAnnouncements.value.slice(start, end);
});

const loadData = async () => {
  loading.value = true;
  try {
    // Pass true to include_inactive to see all announcements for admin
    announcements.value = await adminApi.listAnnouncements(true);
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || "加载公告失败");
  } finally {
    loading.value = false;
  }
};

const openCreate = () => {
  dialogTitle.value = "新建公告";
  editId.value = null;
  Object.assign(form, { title: "", content: "", is_active: true });
  dialogVisible.value = true;
};

const openEdit = (item: Announcement) => {
  dialogTitle.value = "编辑公告";
  editId.value = item.id;
  Object.assign(form, {
    title: item.title,
    content: item.content,
    is_active: item.is_active,
  });
  dialogVisible.value = true;
};

const submitForm = async () => {
  if (!form.title || !form.content) {
    ElMessage.warning("请填写标题和内容");
    return;
  }
  try {
    if (editId.value) {
      await adminApi.updateAnnouncement(editId.value, { ...form });
      ElMessage.success("公告已更新");
    } else {
      if (!auth.user) return;
      await adminApi.createAnnouncement({
        title: form.title,
        content: form.content,
        created_by: auth.user.id,
        is_active: form.is_active,
      });
      ElMessage.success("公告已创建");
    }
    dialogVisible.value = false;
    await loadData();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || "保存失败");
  }
};

const handleDelete = async () => {
  if (!editId.value) return;
  try {
    await ElMessageBox.confirm("确认删除此公告吗？", "提示", { type: "warning" });
    await adminApi.deleteAnnouncement(editId.value);
    ElMessage.success("公告已删除");
    dialogVisible.value = false;
    await loadData();
  } catch (e) {
    if (e !== "cancel") ElMessage.error("删除失败");
  }
};

onMounted(() => {
  loadData();
});

watch(searchQuery, () => {
  currentPage.value = 1;
});
</script>

<style scoped>
.announcement-management {
  min-height: 100%;
}

.panel-header {
  margin-bottom: 20px;
}

.header-right {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  align-items: center;
}

.search-input {
  width: 240px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}

.dialog-actions-danger {
  margin-top: 24px;
}
</style>
