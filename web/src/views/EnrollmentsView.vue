<template>
  <div class="enrollments">
    <div class="header">
      <div>
        <h2>我的选课</h2>
        <p>查看正在学习的课程，并可快速退课。</p>
      </div>
      <el-button @click="loadEnrollments">刷新</el-button>
    </div>

    <el-table :data="enrollments" style="width: 100%">
      <el-table-column prop="course.title" label="课程名称" />
      <el-table-column label="课程信息">
        <template #default="scope">
          <span v-if="scope.row.course.category_id">分类 ID：{{ scope.row.course.category_id }}</span>
          <span v-else>未分类</span>
        </template>
      </el-table-column>
      <el-table-column label="选课时间" width="160">
        <template #default="scope">
          {{ formatDate(scope.row.enrolled_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="scope">
          <el-button size="small" type="danger" plain @click="dropCourse(scope.row.course_id)">
            退课
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { enrollmentApi } from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import type { EnrollmentWithCourse } from "@/types";
import { formatDate } from "@/utils/format";

const auth = useAuthStore();
const enrollments = ref<EnrollmentWithCourse[]>([]);

const loadEnrollments = async () => {
  if (!auth.user) return;
  try {
    enrollments.value = await enrollmentApi.myEnrollments(auth.user.id);
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "加载选课失败");
  }
};

const dropCourse = async (courseId: number) => {
  if (!auth.user) return;
  try {
    await enrollmentApi.drop(courseId, auth.user.id);
    ElMessage.success("已退课");
    await loadEnrollments();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "退课失败");
  }
};

onMounted(() => {
  loadEnrollments().catch(() => undefined);
});
</script>

<style scoped>
.enrollments {
  display: grid;
  gap: 16px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h2 {
  font-family: var(--font-display);
  margin-bottom: 6px;
}

.header p {
  color: var(--color-ink-muted);
}
</style>
