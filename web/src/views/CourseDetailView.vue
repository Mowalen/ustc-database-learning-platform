<template>
  <div class="course-detail" v-loading="loading">
    <div class="course-banner">
      <div>
        <h2>{{ course?.title }}</h2>
        <p>{{ course?.description || "暂无课程简介" }}</p>
      </div>
      <div class="course-banner__actions">
        <el-tag effect="light">{{ course?.category?.name || "未分类" }}</el-tag>
        <el-button
          v-if="isStudent"
          :type="isEnrolled ? 'danger' : 'success'"
          @click="toggleEnroll"
        >
          {{ isEnrolled ? "退课" : "选课" }}
        </el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="章节内容" name="sections">
        <div class="section-header">
          <p>课程章节与学习资源一览。</p>
          <el-button v-if="isTeacher" type="primary" @click="openSectionDialog()">
            新建章节
          </el-button>
        </div>
        <el-table :data="sections" style="width: 100%">
          <el-table-column prop="order_index" label="序号" width="80" />
          <el-table-column prop="title" label="章节标题" />
          <el-table-column prop="content" label="内容摘要" />
          <el-table-column label="资源">
            <template #default="scope">
              <div class="link-group">
                <a v-if="scope.row.material_url" :href="scope.row.material_url" target="_blank">课件</a>
                <a v-if="scope.row.video_url" :href="scope.row.video_url" target="_blank">视频</a>
                <span v-if="!scope.row.material_url && !scope.row.video_url">暂无</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column v-if="isTeacher" label="操作" width="160">
            <template #default="scope">
              <el-button size="small" @click="openSectionDialog(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" plain @click="deleteSection(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="作业与考试" name="tasks">
        <div class="section-header">
          <p>按课程发布作业与考试，支持提交与评分。</p>
          <el-button v-if="isTeacher" type="primary" @click="openTaskDialog">
            发布任务
          </el-button>
        </div>
        <el-table :data="tasks" style="width: 100%">
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="type" label="类型" width="120">
            <template #default="scope">
              {{ formatTaskType(scope.row.type) }}
            </template>
          </el-table-column>
          <el-table-column prop="deadline" label="截止时间">
            <template #default="scope">
              {{ formatDate(scope.row.deadline) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button size="small" @click="viewTask(scope.row)">查看</el-button>
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
                查看提交
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane v-if="isTeacher" label="学生名单" name="students">
        <el-table :data="students" style="width: 100%">
          <el-table-column prop="student.id" label="学生 ID" width="90" />
          <el-table-column prop="student.username" label="用户名" />
          <el-table-column prop="student.full_name" label="姓名" />
          <el-table-column label="状态">
            <template #default="scope">
              {{ scope.row.status === "active" ? "在读" : "退课" }}
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="sectionDialog" :title="sectionDialogTitle" width="520px">
      <el-form :model="sectionForm" label-position="top">
        <el-form-item label="章节标题">
          <el-input v-model="sectionForm.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="sectionForm.content" type="textarea" />
        </el-form-item>
        <el-form-item label="课件 URL">
          <el-input v-model="sectionForm.material_url" />
        </el-form-item>
        <el-form-item label="视频 URL">
          <el-input v-model="sectionForm.video_url" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="sectionForm.order_index" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="sectionDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSection">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="taskDialog" title="发布任务" width="520px">
      <el-form :model="taskForm" label-position="top">
        <el-form-item label="标题">
          <el-input v-model="taskForm.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="taskForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="taskForm.type" placeholder="选择类型">
            <el-option label="作业" value="assignment" />
            <el-option label="考试" value="exam" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker
            v-model="taskForm.deadline"
            type="datetime"
            placeholder="选择时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTask">发布</el-button>
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

    <el-dialog v-model="taskInfoDialog" title="任务详情" width="520px">
      <div class="task-detail">
        <h3>{{ activeTask?.title }}</h3>
        <p>{{ activeTask?.description || "暂无描述" }}</p>
        <div class="task-detail__meta">
          <span>类型：{{ formatTaskType(activeTask?.type) }}</span>
          <span>截止：{{ formatDate(activeTask?.deadline) }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="taskInfoDialog = false">关闭</el-button>
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
import { useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import {
  courseApi,
  sectionApi,
  taskApi,
  enrollmentApi,
} from "@/services/api";
import { useAuthStore } from "@/stores/auth";
import type { Course, Section, Task, EnrollmentWithStudent, SubmissionWithStudent } from "@/types";
import { formatDate, formatStatus, formatTaskType } from "@/utils/format";

const auth = useAuthStore();
const route = useRoute();
const courseId = Number(route.params.id);

const loading = ref(false);
const course = ref<Course | null>(null);
const sections = ref<Section[]>([]);
const tasks = ref<Task[]>([]);
const students = ref<EnrollmentWithStudent[]>([]);
const activeTab = ref("sections");

const sectionDialog = ref(false);
const sectionDialogTitle = ref("新建章节");
const editingSectionId = ref<number | null>(null);

const taskDialog = ref(false);
const submitDialog = ref(false);
const taskInfoDialog = ref(false);
const activeTask = ref<Task | null>(null);
const submissionsDialog = ref(false);
const submissions = ref<SubmissionWithStudent[]>([]);
const gradeDialog = ref(false);
const activeSubmissionId = ref<number | null>(null);

const sectionForm = reactive({
  title: "",
  content: "",
  material_url: "",
  video_url: "",
  order_index: 0,
});

const taskForm = reactive({
  title: "",
  description: "",
  type: "assignment" as "assignment" | "exam",
  deadline: "",
});

const submitForm = reactive({
  answer_text: "",
  file_url: "",
});
const gradeForm = reactive({
  score: 0,
  feedback: "",
});

const isTeacher = computed(() => auth.roleId === 2);
const isStudent = computed(() => auth.roleId === 1);
const isEnrolled = ref(false);

const loadData = async () => {
  loading.value = true;
  try {
    course.value = await courseApi.getCourse(courseId);
    sections.value = (await sectionApi.listSections(courseId)).sort(
      (a, b) => (a.order_index ?? 0) - (b.order_index ?? 0)
    );
    tasks.value = await taskApi.listTasks(courseId);
    if (isTeacher.value) {
      students.value = await enrollmentApi.courseStudents(courseId);
    }
    if (isStudent.value && auth.user) {
      const enrollments = await enrollmentApi.myEnrollments(auth.user.id);
      isEnrolled.value = enrollments.some((enroll) => enroll.course_id === courseId);
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "加载课程信息失败");
  } finally {
    loading.value = false;
  }
};

const openSectionDialog = (section?: Section) => {
  if (section) {
    sectionDialogTitle.value = "编辑章节";
    editingSectionId.value = section.id;
    Object.assign(sectionForm, {
      title: section.title,
      content: section.content || "",
      material_url: section.material_url || "",
      video_url: section.video_url || "",
      order_index: section.order_index ?? 0,
    });
  } else {
    sectionDialogTitle.value = "新建章节";
    editingSectionId.value = null;
    Object.assign(sectionForm, {
      title: "",
      content: "",
      material_url: "",
      video_url: "",
      order_index: 0,
    });
  }
  sectionDialog.value = true;
};

const saveSection = async () => {
  try {
    if (editingSectionId.value) {
      await sectionApi.updateSection(editingSectionId.value, {
        title: sectionForm.title,
        content: sectionForm.content || null,
        material_url: sectionForm.material_url || null,
        video_url: sectionForm.video_url || null,
        order_index: sectionForm.order_index,
      });
      ElMessage.success("章节已更新");
    } else {
      await sectionApi.createSection(courseId, {
        course_id: courseId,
        title: sectionForm.title,
        content: sectionForm.content || undefined,
        material_url: sectionForm.material_url || undefined,
        video_url: sectionForm.video_url || undefined,
        order_index: sectionForm.order_index,
      });
      ElMessage.success("章节已创建");
    }
    sectionDialog.value = false;
    sections.value = (await sectionApi.listSections(courseId)).sort(
      (a, b) => (a.order_index ?? 0) - (b.order_index ?? 0)
    );
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "保存章节失败");
  }
};

const deleteSection = async (section: Section) => {
  try {
    await sectionApi.deleteSection(section.id);
    ElMessage.success("章节已删除");
    sections.value = sections.value.filter((item) => item.id !== section.id);
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "删除失败");
  }
};

const openTaskDialog = () => {
  Object.assign(taskForm, {
    title: "",
    description: "",
    type: "assignment",
    deadline: "",
  });
  taskDialog.value = true;
};

const saveTask = async () => {
  if (!auth.user) return;
  try {
    await taskApi.createTask(courseId, {
      teacher_id: auth.user.id,
      title: taskForm.title,
      description: taskForm.description || undefined,
      type: taskForm.type,
      deadline: taskForm.deadline || undefined,
    });
    ElMessage.success("任务已发布");
    taskDialog.value = false;
    tasks.value = await taskApi.listTasks(courseId);
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "发布任务失败");
  }
};

const viewTask = (task: Task) => {
  activeTask.value = task;
  taskInfoDialog.value = true;
};

const openSubmissions = async (task: Task) => {
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

const openSubmit = (task: Task) => {
  activeTask.value = task;
  Object.assign(submitForm, { answer_text: "", file_url: "" });
  submitDialog.value = true;
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

const toggleEnroll = async () => {
  if (!auth.user) return;
  try {
    if (isEnrolled.value) {
      await enrollmentApi.drop(courseId, auth.user.id);
      isEnrolled.value = false;
      ElMessage.success("已退课");
    } else {
      await enrollmentApi.enroll(courseId, auth.user.id);
      isEnrolled.value = true;
      ElMessage.success("选课成功");
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "操作失败");
  }
};

onMounted(() => {
  loadData().catch(() => undefined);
});
</script>

<style scoped>
.course-detail {
  display: grid;
  gap: 20px;
}

.course-banner {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding: 20px;
  background: rgba(209, 143, 59, 0.12);
  border-radius: 18px;
}

.course-banner h2 {
  font-family: var(--font-display);
  font-size: 24px;
  margin-bottom: 6px;
}

.course-banner p {
  color: var(--color-ink-muted);
}

.course-banner__actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header p {
  color: var(--color-ink-muted);
}

.link-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 12px;
}

.link-group a {
  color: var(--color-teal);
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
