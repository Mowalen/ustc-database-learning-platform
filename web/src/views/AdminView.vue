<template>
  <div class="admin">
    <!-- Main User Management Section -->
    <!-- Main User Management Section -->
    <div class="user-management-panel">
      <div class="panel-header">
        <div class="header-right">
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户"
            class="search-input"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="openCreateDialog">
            新增用户
          </el-button>
        </div>
      </div>

      <el-table :data="filteredUsers" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" align="center" />
        <el-table-column prop="username" label="用户名" align="center" />
        <el-table-column prop="full_name" label="姓名" align="center" />
        <el-table-column prop="email" label="邮箱" align="center" />
        <el-table-column prop="role_id" label="角色" align="center">
          <template #default="scope">
            <el-tag :type="getRoleType(scope.row.role_id)">
              {{ formatRole(scope.row.role_id) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" align="center">
          <template #default="scope">
            <el-tag
              :type="scope.row.is_active ? 'success' : 'danger'"
              effect="plain"
            >
              {{ scope.row.is_active ? "启用" : "停用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center">
          <template #default="scope">
            <el-button
              size="small"
              type="primary"
              plain
              @click="openEditDialog(scope.row)"
            >
              修改
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Course Management Section Removed -->

    <!-- Create User Dialog -->
    <el-dialog
      v-model="createDialogVisible"
      title="新增用户"
      width="500px"
      destroy-on-close
    >
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="createForm.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="createForm.password"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="createForm.full_name" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="createForm.email" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select
            v-model="createForm.role_id"
            placeholder="选择角色"
            style="width: 100%"
          >
            <el-option label="学生" :value="1" />
            <el-option label="教师" :value="2" />
            <el-option label="管理员" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="createForm.is_active"
            active-text="启用"
            inactive-text="停用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createUser">确认创建</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Edit User Dialog -->
    <el-dialog
      v-model="editDialogVisible"
      title="修改用户信息"
      width="500px"
      destroy-on-close
    >
      <el-form :model="updateForm" label-width="80px">
        <el-form-item label="ID">
          <el-input v-model="updateForm.user_id" disabled />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="updateForm.full_name" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="updateForm.email" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="updateForm.phone" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select
            v-model="updateForm.role_id"
            placeholder="选择角色"
            style="width: 100%"
          >
            <el-option label="学生" :value="1" />
            <el-option label="教师" :value="2" />
            <el-option label="管理员" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="重置密码">
          <el-input
            v-model="updateForm.password"
            type="password"
            show-password
            placeholder="不修改请留空"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="updateForm.is_active"
            active-text="启用"
            inactive-text="停用"
          />
        </el-form-item>
      </el-form>

      <div class="dialog-actions-danger">
        <el-divider content-position="left">危险区域</el-divider>
        <el-button type="danger" plain @click="handleDeleteUser"
          >删除此用户</el-button
        >
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateUser">保存修改</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search } from "@element-plus/icons-vue";
import { adminApi } from "@/services/api";
import type { User } from "@/types";
import { formatRole } from "@/utils/format";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const loading = ref(false);
const users = ref<User[]>([]);
const searchQuery = ref("");

// Dialog Visibility
const createDialogVisible = ref(false);
const editDialogVisible = ref(false);

const createForm = reactive({
  username: "",
  password: "",
  full_name: "",
  email: "",
  role_id: 1,
  is_active: true,
});

const updateForm = reactive({
  user_id: 0,
  username: "", // Visual only
  full_name: "",
  email: "",
  phone: "",
  role_id: null as number | null,
  password: "",
  is_active: true,
});



const filteredUsers = computed(() => {
  let result = users.value.filter((u) => u.role_id !== 3); // Filter out admins
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(
      (u) =>
        u.username.toLowerCase().includes(q) ||
        (u.full_name && u.full_name.toLowerCase().includes(q)) ||
        (u.email && u.email.toLowerCase().includes(q))
    );
  }
  return result;
});

const loadUsers = async () => {
  loading.value = true;
  try {
    users.value = await adminApi.listUsers();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "加载用户列表失败");
  } finally {
    loading.value = false;
  }
};

const getRoleType = (roleId: number) => {
  switch (roleId) {
    case 3:
      return "danger"; // Admin
    case 2:
      return "warning"; // Teacher
    default:
      return ""; // Student
  }
};

const openCreateDialog = () => {
  // Reset form
  createForm.username = "";
  createForm.password = "";
  createForm.full_name = "";
  createForm.email = "";
  createForm.role_id = 1;
  createForm.is_active = true;
  createDialogVisible.value = true;
};

const openEditDialog = (user: User) => {
  updateForm.user_id = user.id;
  updateForm.username = user.username;
  updateForm.full_name = user.full_name || "";
  updateForm.email = user.email || "";
  updateForm.phone = ""; // Phone not always in list, might be empty
  updateForm.role_id = user.role_id;
  updateForm.password = "";
  updateForm.is_active = user.is_active;
  editDialogVisible.value = true;
};

const createUser = async () => {
  if (!createForm.username || !createForm.password) {
    ElMessage.warning("请填写用户名和密码");
    return;
  }
  try {
    await adminApi.createUser({
      username: createForm.username,
      password: createForm.password,
      full_name: createForm.full_name || undefined,
      email: createForm.email || undefined,
      role_id: createForm.role_id,
      is_active: createForm.is_active,
    });
    ElMessage.success("用户已创建");
    createDialogVisible.value = false;
    await loadUsers();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "创建失败");
  }
};

const updateUser = async () => {
  if (!updateForm.user_id) return;
  try {
    await adminApi.updateUser(updateForm.user_id, {
      full_name: updateForm.full_name || undefined,
      email: updateForm.email || undefined,
      phone: updateForm.phone || undefined,
      role_id: updateForm.role_id ?? undefined,
      password: updateForm.password || undefined,
      is_active: updateForm.is_active,
    });
    ElMessage.success("用户信息已更新");
    editDialogVisible.value = false;
    await loadUsers();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "更新失败");
  }
};

const handleDeleteUser = async () => {
  if (!updateForm.user_id) return;

  if (auth.user?.id === updateForm.user_id) {
    ElMessage.error("不能删除当前登录账号");
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确认删除用户 (ID: ${updateForm.user_id}) 吗？此操作不可逆。`,
      "删除用户",
      {
        type: "warning",
        confirmButtonText: "确认删除",
        cancelButtonText: "取消",
      }
    );
    await adminApi.deleteUser(updateForm.user_id);
    ElMessage.success("用户已删除");
    editDialogVisible.value = false;
    await loadUsers();
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error(error?.response?.data?.detail || "删除失败");
    }
  }
};



onMounted(() => {
  loadUsers().catch(() => undefined);
});
</script>

<style scoped>
.admin {
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

.dialog-actions-danger {
  margin-top: 24px;
}
</style>
