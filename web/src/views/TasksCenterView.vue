<template>
  <div class="tasks-center">
    <div class="header">
      <div>
        <h2>作业与考试</h2>
        <p>集中查看任务安排与提交记录。</p>
      </div>
      <el-button @click="loadTasks">刷新</el-button>
    </div>

    <el-table :data="tasks" style="width: 100%">
      <el-table-column prop="courseTitle" label="课程" />
      <el-table-column prop="title" label="任务标题" />
      <el-table-column label="类型" width="120">
        <template #default="scope">
          {{ formatTaskType(scope.row.type) }}
        </template>
      </el-table-column>
      <el-table-column label="截止时间" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.deadline) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="scope">
          <el-button size="small" @click="viewTask(scope.row)">详情</el-button>
          <el-button
            v-if="isStudent"
            size="small"
            type="success"
            plain
            @click="openSubmit(scope.row)"
          >
            提交
          </el-button>
          <el-button
            v-if="isTeacher"
            size="small"
            type="primary"
            plain
            @click="openSubmissions(scope.row)"
          >
            批改
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="taskDialog" title="任务详情" width="520px">
      <div class="task-detail">
        <h3>{{ activeTask?.title }}</h3>
        <p>{{ activeTask?.description || "暂无描述" }}</p>
        <div class="task-detail__meta">
          <span>课程：{{ activeTask?.courseTitle }}</span>
          <span>类型：{{ formatTaskType(activeTask?.type) }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="taskDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="submitDialog" title="提交任务" width="520px">
      <el-form :model="submitForm" label-position="top">
        <el-form-item label="答案内容">
          <el-input v-model="submitForm.answer_text" type="textarea" />
        </el-form-item>
        <el-form-item label="附件 URL">
          <el-input v-model="submitForm.file_url" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="submitDialog = false">取消</el-button>
        <el-button type="primary" @click="submitTask">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="submissionsDialog" title="提交记录" width="760px">
      <el-table :data="submissions" style="width: 100%">
        <el-table-column prop="student.username" label="学生" width="160" />
        <el-table-column prop="answer_text" label="答案" />
        <el-table-column label="附件" width="140">
          <template #default="scope">
            <a v-if="scope.row.file_url" :href="scope.row.file_url" target="_blank">查看</a>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="分数" width="90">
          <template #default="scope">
            {{ scope.row.score ?? "-" }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            {{ formatStatus(scope.row.status) }}
          </template>
        </el-table-column>
        <el-table-column label="评分时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.graded_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button size="small" @click="openGrade(scope.row)">评分</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="submissionsDialog = false">关闭</el-button>
      </template>
    </el-dialog>

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
import { courseApi, enrollmentApi, taskApi } from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import { formatDate, formatStatus, formatTaskType } from "@/utils/format";
import type { SubmissionWithStudent, Task } from "@/types";

interface TaskRow extends Task {
  courseTitle: string;
}

const auth = useAuthStore();
const tasks = ref<TaskRow[]>([]);
const taskDialog = ref(false);
const submitDialog = ref(false);
const activeTask = ref<TaskRow | null>(null);
const submissionsDialog = ref(false);
const submissions = ref<SubmissionWithStudent[]>([]);
const gradeDialog = ref(false);
const activeSubmissionId = ref<number | null>(null);

const submitForm = reactive({
  answer_text: "",
  file_url: "",
});

const isStudent = computed(() => auth.roleId === 1);
const isTeacher = computed(() => auth.roleId === 2);

const gradeForm = reactive({
  score: 0,
  feedback: "",
});

const loadTasks = async () => {
  try {
    tasks.value = [];
    if (auth.roleId === 1 && auth.user) {
      const enrollments = await enrollmentApi.myEnrollments(auth.user.id);
      const rows = await Promise.all(
        enrollments.map(async (enrollment) => {
          const courseTasks = await taskApi.listTasks(enrollment.course_id);
          return courseTasks.map((task) => ({
            ...task,
            courseTitle: enrollment.course.title,
          }));
        })
      );
      tasks.value = rows.flat();
    } else if (auth.roleId === 2 && auth.user) {
      const courses = await courseApi.listCourses();
      const myCourses = courses.filter((course) => course.teacher_id === auth.user?.id);
      const rows = await Promise.all(
        myCourses.map(async (course) => {
          const courseTasks = await taskApi.listTasks(course.id);
          return courseTasks.map((task) => ({
            ...task,
            courseTitle: course.title,
          }));
        })
      );
      tasks.value = rows.flat();
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "加载任务失败");
  }
};

const viewTask = (task: TaskRow) => {
  activeTask.value = task;
  taskDialog.value = true;
};

const openSubmit = (task: TaskRow) => {
  activeTask.value = task;
  Object.assign(submitForm, { answer_text: "", file_url: "" });
  submitDialog.value = true;
};

const openSubmissions = async (task: TaskRow) => {
  try {
    activeTask.value = task;
    submissions.value = await taskApi.listSubmissions(task.id);
    submissionsDialog.value = true;
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "加载提交记录失败");
  }
};

const openGrade = (submission: SubmissionWithStudent) => {
  activeSubmissionId.value = submission.id;
  gradeForm.score = Number(submission.score ?? 0);
  gradeForm.feedback = submission.feedback || "";
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
    if (activeTask.value) {
      submissions.value = await taskApi.listSubmissions(activeTask.value.id);
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "评分失败");
  }
};

const submitTask = async () => {
  if (!auth.user || !activeTask.value) return;
  try {
    await taskApi.submitTask(activeTask.value.id, {
      student_id: auth.user.id,
      answer_text: submitForm.answer_text || undefined,
      file_url: submitForm.file_url || undefined,
    });
    ElMessage.success("提交成功");
    submitDialog.value = false;
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "提交失败");
  }
};

onMounted(() => {
  loadTasks().catch(() => undefined);
});
</script>

<style scoped>
.tasks-center {
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

.task-detail h3 {
  font-family: var(--font-display);
  margin-bottom: 8px;
}

.task-detail p {
  color: var(--color-ink-muted);
  margin-bottom: 16px;
}

.task-detail__meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--color-ink-muted);
}
</style>
