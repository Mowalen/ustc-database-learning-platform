<template>
  <div class="scores">
    <div class="header">
      <div class="header__actions">
        <el-select
          v-if="isTeacher"
          v-model="selectedCourseId"
          placeholder="选择课程"
          clearable
          @change="loadScores"
        >
          <el-option
            v-for="course in myCourses"
            :key="course.id"
            :label="course.title"
            :value="course.id"
          />
        </el-select>
        <el-button @click="loadScores">刷新</el-button>
        <el-button v-if="isTeacher && selectedCourseId" type="primary" plain @click="exportScores">
          导出 CSV
        </el-button>
      </div>
    </div>

    <el-table :data="scores" style="width: 100%">
      <el-table-column prop="task_title" label="任务" min-width="180" />
      <el-table-column prop="student_id" label="学生" min-width="100" v-if="isTeacher" />
      <el-table-column prop="score" label="分数" min-width="80">
        <template #default="scope">
          {{ scope.row.score ?? "-" }}
        </template>
      </el-table-column>
      <el-table-column prop="feedback" label="评语" min-width="200">
        <template #default="scope">
          {{ scope.row.feedback || "-" }}
        </template>
      </el-table-column>
      <el-table-column label="状态" min-width="100">
        <template #default="scope">
          {{ formatStatus(scope.row.status) }}
        </template>
      </el-table-column>
      <el-table-column label="评分时间" min-width="160">
        <template #default="scope">
          {{ formatDate(scope.row.graded_at) }}
        </template>
      </el-table-column>
      <el-table-column v-if="isTeacher" label="操作" min-width="100">
        <template #default="scope">
          <el-button size="small" @click="openGrade(scope.row)">评分</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="gradeDialog" title="评分" width="420px">
      <el-form :model="gradeForm" label-position="top">
        <el-form-item label="分数">
          <el-input-number v-model="gradeForm.score" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="评语">
          <el-input v-model="gradeForm.feedback" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="gradeDialog = false">取消</el-button>
        <el-button type="primary" @click="submitGrade">提交评分</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { courseApi, scoreApi, taskApi } from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import type { Course, Score } from "@/types";
import { formatDate, formatStatus } from "@/utils/format";

const auth = useAuthStore();
const scores = ref<Score[]>([]);
const courses = ref<Course[]>([]);
const selectedCourseId = ref<number | null>(null);
const gradeDialog = ref(false);
const activeSubmissionId = ref<number | null>(null);

const gradeForm = reactive({
  score: 0,
  feedback: "",
});

const isStudent = computed(() => auth.roleId === 1);
const isTeacher = computed(() => auth.roleId === 2);

const myCourses = computed(() =>
  courses.value.filter((course) => course.teacher_id === auth.user?.id)
);

const loadScores = async () => {
  try {
    if (isStudent.value && auth.user) {
      scores.value = await scoreApi.myScores(auth.user.id);
    } else if (isTeacher.value && selectedCourseId.value) {
      scores.value = await scoreApi.courseScores(selectedCourseId.value);
    } else {
      scores.value = [];
    }
  } catch (error: any) {
    if (error?.response?.status === 404) {
      scores.value = [];
      ElMessage.info("暂无成绩记录");
      return;
    }
    ElMessage.error(error?.response?.data?.detail || "加载成绩失败");
  }
};

const exportScores = async () => {
  if (!selectedCourseId.value) return;
  try {
    const csvContent = await scoreApi.exportCourseScores(selectedCourseId.value);
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `course_${selectedCourseId.value}_scores.csv`);
    link.click();
    URL.revokeObjectURL(url);
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "导出失败");
  }
};

const openGrade = (row: Score) => {
  activeSubmissionId.value = row.submission_id;
  gradeForm.score = Number(row.score ?? 0);
  gradeForm.feedback = "";
  gradeDialog.value = true;
};

const submitGrade = async () => {
  if (!activeSubmissionId.value) return;
  try {
    await taskApi.gradeSubmission(activeSubmissionId.value, {
      score: gradeForm.score,
      feedback: gradeForm.feedback || undefined,
    });
    ElMessage.success("评分已提交");
    gradeDialog.value = false;
    await loadScores();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "评分失败");
  }
};

onMounted(async () => {
  courses.value = await courseApi.listCourses();
  await loadScores();
});
</script>

<style scoped>
.scores {
  display: grid;
  gap: 16px;
}

.header {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.header__actions {
  display: flex;
  gap: 12px;
  align-items: center;
}
</style>
