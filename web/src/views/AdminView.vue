<template>
  <div class="admin">
    <div class="header">
      <div>
        <h2>管理员后台</h2>
        <p>管理用户账号、课程状态与系统运行。</p>
      </div>
    </div>

    <div class="admin-grid">
      <el-card>
        <h3>新建用户</h3>
        <el-form :model="createForm" label-position="top">
          <el-form-item label="用户名">
            <el-input v-model="createForm.username" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="createForm.password" type="password" show-password />
          </el-form-item>
          <el-form-item label="姓名">
            <el-input v-model="createForm.full_name" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="createForm.email" />
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="createForm.role_id" placeholder="选择角色">
              <el-option label="学生" :value="1" />
              <el-option label="教师" :value="2" />
              <el-option label="管理员" :value="3" />
            </el-select>
          </el-form-item>
          <el-form-item label="启用状态">
            <el-switch v-model="createForm.is_active" active-text="启用" inactive-text="停用" />
          </el-form-item>
        </el-form>
        <el-button type="primary" @click="createUser">创建用户</el-button>
      </el-card>

      <el-card>
        <h3>更新用户</h3>
        <el-form :model="updateForm" label-position="top">
          <el-form-item label="用户 ID">
            <el-input v-model.number="updateForm.user_id" />
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
            <el-select v-model="updateForm.role_id" placeholder="选择角色" clearable>
              <el-option label="学生" :value="1" />
              <el-option label="教师" :value="2" />
              <el-option label="管理员" :value="3" />
            </el-select>
          </el-form-item>
          <el-form-item label="新密码">
            <el-input v-model="updateForm.password" type="password" show-password />
          </el-form-item>
          <el-form-item label="启用状态">
            <el-switch v-model="updateForm.is_active" active-text="启用" inactive-text="停用" />
          </el-form-item>
        </el-form>
        <el-button type="primary" @click="updateUser">更新用户</el-button>
      </el-card>

      <el-card>
        <h3>停用用户</h3>
        <el-form :model="disableForm" label-position="top">
          <el-form-item label="用户 ID">
            <el-input v-model.number="disableForm.user_id" />
          </el-form-item>
        </el-form>
        <el-button type="danger" plain @click="disableUser">停用账号</el-button>
      </el-card>

      <el-card class="admin-list">
        <div class="admin-list__header">
          <h3>用户列表</h3>
          <el-button size="small" @click="loadUsers">刷新</el-button>
        </div>
        <el-table :data="users" style="width: 100%">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="full_name" label="姓名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="role_id" label="角色" width="90">
            <template #default="scope">
              {{ formatRole(scope.row.role_id) }}
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="90">
            <template #default="scope">
              {{ scope.row.is_active ? "启用" : "停用" }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card>
        <h3>课程下架</h3>
        <el-form :model="courseForm" label-position="top">
          <el-form-item label="课程 ID">
            <el-input v-model.number="courseForm.course_id" />
          </el-form-item>
        </el-form>
        <el-button type="danger" plain @click="deactivateCourse">下架课程</el-button>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { adminApi } from "@/services/api";
import type { User } from "@/types";
import { formatRole } from "@/utils/format";

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
  full_name: "",
  email: "",
  phone: "",
  role_id: null as number | null,
  password: "",
  is_active: true,
});

const disableForm = reactive({
  user_id: 0,
});

const courseForm = reactive({
  course_id: 0,
});

const users = ref<User[]>([]);

const loadUsers = async () => {
  try {
    users.value = await adminApi.listUsers();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "加载用户列表失败");
  }
};

const createUser = async () => {
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
    ElMessage.success("用户已更新");
    await loadUsers();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "更新失败");
  }
};

const disableUser = async () => {
  if (!disableForm.user_id) return;
  try {
    await adminApi.deleteUser(disableForm.user_id);
    ElMessage.success("用户已停用");
    await loadUsers();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "停用失败");
  }
};

const deactivateCourse = async () => {
  if (!courseForm.course_id) return;
  try {
    await adminApi.deactivateCourse(courseForm.course_id);
    ElMessage.success("课程已下架");
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "下架失败");
  }
};

onMounted(() => {
  loadUsers().catch(() => undefined);
});
</script>

<style scoped>
.admin {
  display: grid;
  gap: 16px;
}

.header h2 {
  font-family: var(--font-display);
  margin-bottom: 6px;
}

.header p {
  color: var(--color-ink-muted);
}

.admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

h3 {
  margin-bottom: 12px;
}

.admin-list {
  grid-column: 1 / -1;
}

.admin-list__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
</style>
